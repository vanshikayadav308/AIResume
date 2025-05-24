import streamlit as st
import requests
import os
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="CVPilot – Resume & JD AI Matcher", layout="wide")
st.title("📄 CVPilot – Resume & Job Description AI Assistant")

backend_url = "http://127.0.0.1:8000"

# Load match history
def load_match_history():
    try:
        conn = sqlite3.connect("../data/match_history.db")
        df = pd.read_sql_query("SELECT * FROM history ORDER BY timestamp DESC", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# Sidebar: Match history & analytics
df = load_match_history()
if st.sidebar.button("📊 View Match History"):
    if not df.empty:
        st.subheader("📋 Resume Match History")
        st.dataframe(df)
    else:
        st.warning("⚠️ No match history found.")

if st.sidebar.button("📈 Open Analytics Dashboard"):
    if not df.empty:
        st.subheader("📊 Analytics Dashboard")
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
        fig_line = px.line(df, x="timestamp", y="match_score", title="Match Score Over Time")
        st.plotly_chart(fig_line, use_container_width=True)

        bins = [0, 50, 70, 85, 100]
        labels = ['Poor', 'Average', 'Good', 'Excellent']
        df["bucket"] = pd.cut(df["match_score"], bins=bins, labels=labels)
        score_counts = df["bucket"].value_counts().sort_index()
        fig_bar = px.bar(x=score_counts.index, y=score_counts.values,
                         labels={"x": "Score Category", "y": "Number of Matches"},
                         title="Score Distribution")
        st.plotly_chart(fig_bar, use_container_width=True)

        fig_pie = px.pie(values=[72, 28], names=["Matched", "Missing"],
                         title="Simulated Keyword Match Coverage")
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("📭 No match history available to generate analytics.")

# Upload form
uploaded_file = st.file_uploader("📤 Upload your resume (.pdf)", type=["pdf"])
jd_text = st.text_area("📝 Paste the Job Description here")

# JD Keyword Intelligence Dashboard (live from JD input)
if jd_text:
    st.subheader("🔍 JD Keyword Intelligence")
    keyword_response = requests.post(
        f"{backend_url}/extract-keywords/",
        data={"jd": jd_text}
    )
    if keyword_response.status_code == 200:
        keywords = keyword_response.json()
        col1, col2, col3 = st.columns(3)
        col1.markdown("**Skills:**")
        col1.write("\n".join(keywords.get("skills", [])))
        col2.markdown("**Tools/Technologies:**")
        col2.write("\n".join(keywords.get("tools", [])))
        col3.markdown("**Action Verbs:**")
        col3.write("\n".join(keywords.get("actions", [])))
    else:
        st.warning("⚠️ Could not extract keywords from JD.")

# Resume extraction preview
if uploaded_file:
    temp_filename = f"temp_{uploaded_file.name}"
    with open(temp_filename, "wb") as f:
        f.write(uploaded_file.read())
    with open(temp_filename, "rb") as f:
        upload_response = requests.post(
            f"{backend_url}/upload-resume/",
            files={"file": (uploaded_file.name, f, "application/pdf")}
        )
    os.remove(temp_filename)

    if upload_response.status_code == 200:
        st.session_state["resume_preview"] = upload_response.json()["extracted_text"]
        st.session_state["filename"] = upload_response.json()["filename"]
        st.success(f"✅ Resume processed: {uploaded_file.name}")
        st.text_area("📄 Extracted Resume Text", st.session_state["resume_preview"], height=250)
    else:
        st.warning("❌ Failed to extract resume.")

# Resume Fit Score by Category (Simulated demo)
if uploaded_file and jd_text:
    st.subheader("📐 Resume Fit Score by Category")
    scores = {
        "Skills": 78,
        "Tools": 65,
        "Experience": 85,
        "Education": 90
    }
    st.dataframe(pd.DataFrame(scores.items(), columns=["Category", "Score (%)"]))
    radar_df = pd.DataFrame({"Score": list(scores.values()), "Category": list(scores.keys())})
    fig_radar = px.line_polar(radar_df, r="Score", theta="Category", line_close=True,
                              title="Fit Score Radar", range_r=[0, 100])
    st.plotly_chart(fig_radar, use_container_width=True)

# Match analysis
if uploaded_file and jd_text:
    if st.button("Analyze Match"):
        match_response = requests.post(
            f"{backend_url}/match-resume/",
            data={"jd": jd_text, "filename": st.session_state.get("filename", "")}
        )
        if match_response.status_code == 200 and "similarity_score" in match_response.json():
            result = match_response.json()
            st.metric("🧠 Match Score", f"{result['similarity_score']}%")
            st.subheader("🛠 GPT Feedback")
            st.write(result["verdict"])

            bullet_response = requests.post(
                f"{backend_url}/rewrite-bullets/",
                data={"jd": jd_text, "filename": st.session_state.get("filename", "")}
            )
            if bullet_response.status_code == 200:
                st.subheader("✍️ Suggested Bullet Points")
                st.code(bullet_response.json()["suggested_bullets"])

            report_response = requests.post(
                f"{backend_url}/generate-report/",
                data={"jd": jd_text, "filename": st.session_state.get("filename", "")}
            )
            if report_response.status_code == 200:
                with open("CVPilot_Report.pdf", "wb") as f:
                    f.write(report_response.content)
                with open("CVPilot_Report.pdf", "rb") as file:
                    st.download_button("Download Report", file, file_name="CVPilot_Report.pdf")

            cover_response = requests.post(
                f"{backend_url}/generate-cover-letter/",
                data={"jd": jd_text, "filename": st.session_state.get("filename", "")}
            )
            if cover_response.status_code == 200:
                st.subheader("✉️ Cover Letter")
                st.text_area("📃 Generated Cover Letter", cover_response.json()["cover_letter"], height=300)
        else:
            st.error("❌ Resume matching failed.")

# --- Assistant Always Visible ---
st.subheader("💬 Ask CVPilot Anything")
user_question = st.text_input("Ask a question about your resume, job match, or anything career-related:")
resume_context = st.session_state.get("resume_preview", "")
if user_question:
    ask_response = requests.post(
        f"{backend_url}/ask-cvpilot/",
        data={"jd": jd_text, "resume": resume_context, "question": user_question}
    )
    if ask_response.status_code == 200:
        st.write("🤖 CVPilot says:")
        st.info(ask_response.json()["answer"])
    else:
        st.warning("⚠️ CVPilot couldn’t answer your question.")
