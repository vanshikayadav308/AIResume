#  CVPilot – AI-Powered Resume & JD Intelligence Assistant

CVPilot is your personal AI-powered job application assistant. Built using FastAPI, Streamlit, and OpenAI, it helps users match their resumes to job descriptions with intelligent GPT-based feedback, resume improvement suggestions, keyword analytics, and downloadable reports.

---

##  Features

| Feature | Description |
|--------|-------------|
|  Resume Upload | Upload PDF resume and extract text |
|  JD Input | Paste any job description |
|  GPT Feedback | See how well your resume fits and what’s missing |
|  Bullet Rewriter | Get improved GPT-generated resume bullets |
|  Analytics Dashboard | Visual insights on match scores and keyword coverage |
|  JD Keyword Intelligence | GPT extracts key skills, tools, and action verbs from the JD |
|  Resume Fit Score by Category | Category-wise score breakdown (Skills, Tools, Experience, Education) |
| Download Report | PDF report of score + recommendations |
|  Ask CVPilot | Interactive GPT assistant to ask anything about your resume or match |
|  Match History | SQLite-backed session tracker with full history dashboard |

---

## Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **AI Model**: [OpenAI GPT-3.5 Turbo](https://openai.com/)
- **Database**: SQLite
- **Visualization**: Plotly & Pandas

---


---

##  Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cvpilot.git
cd cvpilot
python -m venv venv
source venv/bin/activate  # or .\\venv\\Scripts\\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
cd streamlit_app
streamlit run main.py
