import openai
import numpy as np
from numpy.linalg import norm
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Embedding & Similarity ---

def get_embedding(text: str, model: str = "text-embedding-3-small") -> list:
    text = text.replace("\n", " ")
    response = openai.Embedding.create(input=[text], model=model)
    return response['data'][0]['embedding']

def cosine_similarity(vec1, vec2) -> float:
    vec1, vec2 = np.array(vec1), np.array(vec2)
    return float(np.dot(vec1, vec2) / (norm(vec1) * norm(vec2)))

# --- Resume-to-JD Matching ---

def match_resume_to_jd(resume_text: str, jd_text: str) -> dict:
    resume_embedding = get_embedding(resume_text)
    jd_embedding = get_embedding(jd_text)
    score = cosine_similarity(resume_embedding, jd_embedding)
    match_percent = round(score * 100, 2)
    
    return {
        "similarity_score": match_percent,
        "verdict": generate_verdict(resume_text, jd_text, match_percent)
    }

# --- GPT Feedback (Verdict) ---

def generate_verdict(resume: str, jd: str, score: float) -> str:
    prompt = f"""
You are an AI resume expert.

Job Description:
{jd}

Resume:
{resume}

The similarity score between the resume and JD is {score}%.

Now, explain in 3 short bullet points:
- What is good about the match
- What is missing or could be improved
- What keywords should be added to the resume
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

# --- GPT Bullet Suggestions ---

def generate_bullet_improvements(resume: str, jd: str) -> str:
    prompt = f"""
You are an AI resume enhancer.

Based on the job description below, suggest 3 improved bullet points that could be added or replaced in the resume to increase its relevance.

Job Description:
{jd}

Resume:
{resume}

Only output 3 strong bullet points.
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

# --- AI Cover Letter Generator ---

def generate_cover_letter(resume: str, jd: str) -> str:
    prompt = f"""
You are an expert career coach and writer.

Based on the following job description and resume, write a personalized, professional cover letter that:

- Is tailored to the job
- Highlights relevant skills and experience
- Follows a professional tone
- Is 3–5 short paragraphs max

Job Description:
{jd}

Resume:
{resume}

Only return the cover letter text, no introductions.
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()
