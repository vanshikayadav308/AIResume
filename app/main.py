from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv
import openai

from app.resume_parser import extract_text_from_pdf
from app.matcher import (
    match_resume_to_jd,
    generate_bullet_improvements,
    generate_cover_letter,
)
from app.utils import generate_pdf_report, save_match_to_history

# Load OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="CVPilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"message": "CVPilot is running ✅"}

@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    extracted_text = extract_text_from_pdf(file_location)
    return {
        "filename": file.filename,
        "extracted_text": extracted_text[:1000]
    }

@app.post("/match-resume/")
async def match_resume(jd: str = Form(...), filename: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "Resume file not found."}
    try:
        resume_text = extract_text_from_pdf(file_path)
        result = match_resume_to_jd(resume_text, jd)
        save_match_to_history(filename, jd, result["similarity_score"])
        return result
    except Exception as e:
        return {"error": f"Failed to match resume: {str(e)}"}

@app.post("/rewrite-bullets/")
async def rewrite_bullets(jd: str = Form(...), filename: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "Resume file not found."}
    resume_text = extract_text_from_pdf(file_path)
    suggestions = generate_bullet_improvements(resume_text, jd)
    return {"suggested_bullets": suggestions}

@app.post("/generate-report/")
async def generate_report(jd: str = Form(...), filename: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "Resume file not found."}
    resume_text = extract_text_from_pdf(file_path)
    result = match_resume_to_jd(resume_text, jd)
    bullets = generate_bullet_improvements(resume_text, jd)
    report_path = os.path.join(UPLOAD_DIR, "CVPilot_Report.pdf")
    generate_pdf_report(
        filename, result["similarity_score"], result["verdict"], bullets, report_path
    )
    return FileResponse(report_path, media_type="application/pdf", filename="CVPilot_Report.pdf")

@app.post("/generate-cover-letter/")
async def generate_cover_letter_api(jd: str = Form(...), filename: str = Form(...)):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "Resume file not found."}
    resume_text = extract_text_from_pdf(file_path)
    letter = generate_cover_letter(resume_text, jd)
    return {"cover_letter": letter}

@app.post("/ask-cvpilot/")
async def ask_cvpilot(jd: str = Form(...), resume: str = Form(...), question: str = Form(...)):
    prompt = f"""
You are CVPilot, an AI assistant that helps users tailor their resumes to job descriptions.

User asked: "{question}"

Resume:
{resume}

Job Description:
{jd}

Please answer clearly and use bullet points if helpful.
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )
    return {"answer": response.choices[0].message.content.strip()}
