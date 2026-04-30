from __future__ import annotations

import io
import time
from contextlib import redirect_stdout
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from prototype.core import (
    USER_TYPES,
    generate_tasks,
    load_feature_usage_logs,
    load_user_segment,
    log_session,
    profile_user,
    recommend,
    register,
    session_summary,
    user_recent_activity,
    FEATURE_LABEL,
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="NextSync Guide Demo")


class ChatRequest(BaseModel):
    session_id: str
    user_id: str
    user_type: str
    goal: str


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "onboarding.html", {
        "user_types": USER_TYPES,
        "result": None,
    })


@app.post("/onboard", response_class=HTMLResponse)
async def onboard(
    request: Request,
    user_id: int = Form(...),
    user_type_override: str = Form(""),
    goal: str = Form(...),
) -> HTMLResponse:
    segment = load_user_segment()
    logs = load_feature_usage_logs()

    user_type = user_type_override or profile_user(user_id, segment)
    features = recommend(user_type, logs, segment)
    recent = user_recent_activity(user_id, logs)
    features_labeled = [{"code": f, "label": FEATURE_LABEL.get(f, f)} for f in features]

    out = generate_tasks(user_type, features, recent, goal)

    mock_log = io.StringIO()
    with redirect_stdout(mock_log):
        register(user_id, user_type, out)

    result = {
        "user_id": user_id,
        "user_type": user_type,
        "features": features_labeled,
        "recent": recent,
        "goal": goal,
        "tasks": out.get("tasks", []),
        "team_invites": out.get("team_invites", []),
        "notifications": out.get("notifications", []),
        "mock_log": mock_log.getvalue().strip(),
    }

    return templates.TemplateResponse(request, "onboarding.html", {
        "user_types": USER_TYPES,
        "result": result,
        "submitted": {"user_id": user_id, "user_type_override": user_type_override, "goal": goal},
    })


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "chat.html", {})


@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request) -> HTMLResponse:
    summary = session_summary()
    return templates.TemplateResponse(request, "analytics.html", {"summary": summary})


@app.post("/api/chat/generate")
async def chat_generate(req: ChatRequest) -> JSONResponse:
    segment = load_user_segment()
    logs = load_feature_usage_logs()

    user_type = req.user_type
    features = recommend(user_type, logs, segment)
    recent = user_recent_activity(req.user_id, logs)
    features_labeled = [{"code": f, "label": FEATURE_LABEL.get(f, f)} for f in features]

    t0 = time.monotonic()
    out = generate_tasks(user_type, features, recent, req.goal)
    elapsed_ms = round((time.monotonic() - t0) * 1000)

    mock_log = io.StringIO()
    with redirect_stdout(mock_log):
        register(req.user_id, user_type, out)

    log_session(req.session_id, req.user_id, user_type, req.goal, out, elapsed_ms)

    return JSONResponse({
        "user_id": req.user_id,
        "user_type": user_type,
        "features": features_labeled,
        "tasks": out.get("tasks", []),
        "team_invites": out.get("team_invites", []),
        "notifications": out.get("notifications", []),
        "elapsed_ms": elapsed_ms,
    })
