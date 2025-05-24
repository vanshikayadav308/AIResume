from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import sqlite3
from datetime import datetime
import os

# Path to your SQLite history DB
DB_PATH = "data/match_history.db"

# --- PDF Report Generator ---

def generate_pdf_report(filename: str, score: float, verdict: str, bullets: str, output_path: str):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    margin = 40
    text_object = c.beginText(margin, height - margin)
    text_object.setFont("Helvetica", 12)

    # Structured report content
    lines = [
        "CVPilot Resume Match Report",
        "-----------------------------",
        f"Filename: {filename}",
        f"Match Score: {score}%",
        "",
        "🧠 GPT Feedback:",
        verdict,
        "",
        "✍️ Suggested Bullet Points:",
        bullets,
    ]

    # Write lines with automatic wrapping
    for line in lines:
        for subline in line.split("\n"):
            text_object.textLine(subline)

    c.drawText(text_object)
    c.showPage()
    c.save()

# --- Match History Saver (SQLite) ---

def save_match_to_history(filename: str, jd_text: str, score: float):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().isoformat()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            job_description TEXT NOT NULL,
            match_score REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    cursor.execute("""
        INSERT INTO history (filename, job_description, match_score, timestamp)
        VALUES (?, ?, ?, ?)
    """, (filename, jd_text[:250], score, timestamp))

    conn.commit()
    conn.close()
