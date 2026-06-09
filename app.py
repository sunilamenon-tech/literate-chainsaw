import streamlit as st
import requests
import base64
from datetime import date

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "JEE Advanced", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English", "Other"])
    test_date = st.date_input("When is your test?", min_value=date.today())
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated! Prepping for {exam_goal}. Let's master {current_topic}!"}]
        st.rerun()
    days_left = (test_date - date.today()).days
    tension = "High 🚨" if days_left < 7 else ("Medium ⚠️" if days_left < 20 else "Low 😌")
    st.markdown(f"--- \n### 📊 Your Status \n- **Tension:** {tension} \n- **Days Left:** {days_left}")

# CHAT
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and i > 0 and "?" in message["content"] and "cheat sheet" not in message["content"].lower():
            if st.button("⚡ Stuck? Get a hint/cheat sheet", key=f"btn_{i}"):
                st.session_state.messages.append({"role": "user", "content": "Just give me the cheat sheet."})
                st.rerun()

if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# AI PROCESSING
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner('Thinking...'):
            try:
                api_key = st.secrets["GOOGLE_API_KEY"]
                # We use the simplest possible URL for the model
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                payload = {"contents": [{"parts": [{"text": st.session_state.messages[-1]["content"]}]}]}
                
                response = requests.post(url, json=payload).json()
                
                if 'candidates' in response and response['candidates']:
                    answer = response['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Debug: {response}") # This will tell us EXACTLY what Google says
            except Exception as e:
                st.error(f"Error: {e}")
