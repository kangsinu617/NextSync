git clone https://github.com/kangsinu617/NextSync.git
  
cd NextSync   

pip install google-genai python-dotenv fastapi uvicorn jinja2 python-multipart

echo "GEMINI_API_KEY=발급받은키" > .env   

uvicorn src.app:app --port 8000

http://127.0.0.1:8000 접속.
