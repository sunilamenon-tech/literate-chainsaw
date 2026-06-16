import streamlit as st
import requests
import base64
from datetime import date, datetime, timedelta
import random
import json

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="centered")

st.markdown("""
<style>
    .stApp {background-color: #FFF9E6;}
    .stButton>button {background-color: #FF6600; color: white; border-radius: 20px; font-weight: 600;}
    .cheat-sheet-box { background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border-left: 4px solid #FF6600; padding: 16px; border-radius: 12px; margin: 8px 0; }
    .socratic-box { background: linear-gradient(135deg, #E8F5E9, #C8E6C9); border-left: 4px solid #4CAF50; padding: 16px; border-radius: 12px; margin: 8px 0; }
    .welcome-box { background: linear-gradient(135deg, #E3F2FD, #BBDEFB); border-left: 4px solid #2196F3; padding: 16px; border-radius: 12px; margin: 8px 0; }
    .stats-box { background: linear-gradient(135deg, #F3E5F5, #E1BEE7); border-left: 4px solid #9C27B0; padding: 16px; border-radius: 12px; margin: 8px 0; }
    .evaluate-correct-box { background: linear-gradient(135deg, #E8F5E9, #C8E6C9); border-left: 4px solid #4CAF50; padding: 16px; border-radius: 12px; margin: 8px 0; }
    .evaluate-wrong-box { background: linear-gradient(135deg, #FFF3E0, #FFE0B2); border-left: 4px solid #FF9800; padding: 16px; border-radius: 12px; margin: 8px 0; }
    .streak-badge { background: linear-gradient(45deg, #FF6600, #FF9900); color: white; padding: 8px 16px; border-radius: 20px; text-align: center; font-weight: bold; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# ============================================================
# INITIALIZE SESSION
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.exam_goal = "JEE Main"
    st.session_state.current_topic = "Physics"
    st.session_state.test_date = date.today() + timedelta(days=90)
    st.session_state.has_specific_date = True
    st.session_state.study_streak = 0
    st.session_state.last_study_date = None
    st.session_state.weak_areas = {}
    st.session_state.threads = {"General": []}
    st.session_state.current_thread = "General"
    st.session_state.pending_ai_request = None
    st.session_state.awaiting_answer = False
    st.session_state.last_socratic_question = None

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English"])
    test_date = st.date_input("When is your test?", min_value=date.today())
    
    if st.button("Sync My Goal"):
        st.session_state.exam_goal = exam_goal
        st.session_state.current_topic = current_topic
        st.session_state.test_date = test_date
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated! Ready to master {current_topic}!"}]
        st.rerun()

# ============================================================
# DISPLAY CHAT
# ============================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ============================================================
# CHAT INPUT & AI
# ============================================================
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner('Thinking...'):
            try:
                api_key = st.secrets["GOOGLE_API_KEY"]
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                full_prompt = f"Context: {st.session_state.exam_goal}, {st.session_state.current_topic}. User: {prompt}. Rules: Socratic Coach. Ask ONE diagnostic question."
                
                response = requests.post(url, json={"contents": [{"parts": [{"text": full_prompt}]}]}).json()
                answer = response['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error("AI is busy. Please try again!")
