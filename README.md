git clone https://github.com/kangsinu617/NextSync.git
  
cd NextSync   

pip install google-genai python-dotenv fastapi uvicorn jinja2 python-multipart

echo "GEMINI_API_KEY=발급받은키" > .env   

python3 -m src.cli --user-id 105 --goal "NextSync"

uvicorn src.app:app --port 8000
