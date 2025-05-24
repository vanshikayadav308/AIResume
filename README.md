# CVPilot

🚀 AI-powered Resume Analyzer and Matcher built with FastAPI and OpenAI

## Features
- Upload your resume PDF
- Extract and parse content automatically
- Match your resume against a job description using embeddings
- Get a similarity score and GPT-powered feedback

## How to Run

1. Clone this project
2. Create and activate virtual environment
3. Install dependencies:
```
pip install -r requirements.txt
```
4. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=sk-xxxxxxxx
```
5. Run server:
```
uvicorn app.main:app --reload
```
6. Open Swagger UI:
```
http://127.0.0.1:8000/docs
```

Upload your resume, then paste a job description to get results!
