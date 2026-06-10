import streamlit as st
import requests
from datetime import date

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# 1. SIDEBAR
with st.sidebar:
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English", "Other"])
    test_date = st.date_input("When is your test?", min_value=date.today())
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated! Ready to master {current_topic} for {exam_goal}!"}]
        st.rerun()

# 2. INITIALIZE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]

# 3. DISPLAY CHAT
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and i > 0 and "?" in message["content"] and "cheat sheet" not in message["content"].lower():
            if st.button("⚡ Stuck? Get a hint/cheat sheet", key=f"btn_{i}"):
                st.session_state.messages.append({"role": "user", "content": "Just give me the cheat sheet."})
                st.rerun()

# 4. CHAT INPUT & PROCESSING
if prompt := st.chat_input("Ask a question..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Process AI response
    with st.chat_message("assistant"):
        with st.spinner('Thinking...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            # Logic to decide persona
            if any(x in prompt.lower() for x in ["cheat sheet", "give me", "explain"]):
                full_prompt = f"Context: {exam_goal}, {current_topic}. Cheat Sheet for: {prompt}. Be direct."
            else:
                full_prompt = f"Context: {exam_goal}, {current_topic}. User: {prompt}. Act as a Socratic Coach: Ask ONE diagnostic question to check knowledge."
            
            response = requests.post(url, json={"contents": [{"parts": [{"text": full_prompt}]}]}).json()
            
            if 'candidates' in response:
                answer = response['candidates'][0]['content']['parts'][0]['text']
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
            else:
                st.error("AI is busy. Try again!")
