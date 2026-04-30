git clone https://github.com/kangsinu617/NextSync.git
  
cd NextSync   

pip install google-genai python-dotenv fastapi uvicorn jinja2 python-multipart

echo "GEMINI_API_KEY=발급받은키" > .env   

uvicorn src.app:app --host 0.0.0.0 --port 8000

http://[서버IP]:8000/chat 접속

http://[서버IP]:8000/analytics 에서 분석 가능
