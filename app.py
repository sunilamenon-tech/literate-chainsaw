import streamlit as st
import requests
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
    if days_left == 0: tension = "TEST DAY! 🚀"
    else: tension = "High 🚨" if days_left < 7 else ("Medium ⚠️" if days_left < 20 else "Low 😌")
    st.markdown(f"--- \n### 📊 Your Status \n- **Tension:** {tension} \n- **Days Left:** {days_left}")

# CHAT LOGIC
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # SMART BUTTON LOGIC: 
        # Only appears if AI asked a question (?) AND we aren't in "chitchat"
        is_coaching = "?" in message["content"] and any(x in message["content"].lower() for x in ["what", "how", "why", "describe"])
        if message["role"] == "assistant" and i > 0 and is_coaching:
            if st.button("⚡ Stuck? Get the cheat sheet", key=f"btn_{i}"):
                st.session_state.messages.append({"role": "user", "content": "Just give me the cheat sheet."})
                st.rerun()

if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# AI PROCESSING
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner('Thinking...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            user_msg = st.session_state.messages[-1]["content"].lower()
            
            # THE "RADICAL TRUTH" PROMPT
            if any(x in user_msg for x in ["cheat sheet", "give me", "explain", "answer"]):
                full_prompt = f"Context: {exam_goal}, {current_topic}. Provide a high-yield cheat sheet for: {st.session_state.messages[-2]['content']}. Be direct, no fluff."
            elif any(x in user_msg for x in ["hi", "hello", "12 hours", "study hours"]):
                full_prompt = f"User: {user_msg}. Respond naturally as a mentor. Challenge inefficient study habits (like 12-hour study days). Do not ask a diagnostic question."
            else:
                full_prompt = f"Context: {exam_goal}, {current_topic}. User: {user_msg}. Act as a Socratic coach. Challenge assumptions. Ask ONE diagnostic question."
            
            response = requests.post(url, json={"contents": [{"parts": [{"text": full_prompt}]}]}).json()
            if 'candidates' in response:
                answer = response['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
