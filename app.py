import streamlit as st
import requests
from datetime import date

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# 1. SIDEBAR (The Control Panel)
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "JEE Advanced", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English", "Other"])
    
    # Date logic: Only show if NOT Other
    test_date = None
    if exam_goal != "Other":
        test_date = st.date_input("When is your test?", min_value=date.today())
    
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated! Ready to master {current_topic}!"}]
        st.rerun()

    # TENSION METER (Appears only if date exists)
    if test_date:
        days_left = (test_date - date.today()).days
        tension = "High 🚨" if days_left < 7 else ("Medium ⚠️" if days_left < 20 else "Low 😌")
        st.markdown(f"--- \n### 📊 Your Status \n- **Tension:** {tension} \n- **Days Left:** {days_left}")

# 2. CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. CHAT INPUT & AI PROCESSING
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner('FocusFlow is thinking...'):
            try:
                api_key = st.secrets["GOOGLE_API_KEY"]
                # Use standard Gemini model endpoint
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                # Context injection
                msg = st.session_state.messages[-1]["content"].lower()
                if any(x in msg for x in ["cheat sheet", "give me", "explain"]):
                    prompt_text = f"Context: {current_topic}. Provide high-yield cheat sheet for: {st.session_state.messages[-2]['content']}."
                else:
                    prompt_text = f"Context: {exam_goal}, {current_topic}. User: {msg}. Rules: Act as Socratic Coach. Ask diagnostic questions."
                
                response = requests.post(url, json={"contents": [{"parts": [{"text": prompt_text}]}]}).json()
                answer = response['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
            except Exception as e:
                st.error("AI is busy. Please try again!")
