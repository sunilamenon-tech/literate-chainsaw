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
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated for {exam_goal}. Let's master {current_topic}!"}]
        st.rerun()
    
    days_left = (test_date - date.today()).days
    tension = "High 🚨" if days_left < 7 else ("Medium ⚠️" if days_left < 20 else "Low 😌")
    st.markdown(f"--- \n### 📊 Your Status \n- **Tension:** {tension} \n- **Days Left:** {days_left}")

# TABS
tab1, tab2 = st.tabs(["💬 Chat", "📸 Upload/Analyze"])

with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]
    
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Only show button if AI has spoken, it contains a question, and no cheat sheet yet
            if message["role"] == "assistant" and "?" in message["content"] and "cheat sheet" not in message["content"].lower():
                if st.button("⚡ Stuck? Get a hint/cheat sheet", key=f"btn_{i}"):
                    st.session_state.messages.append({"role": "user", "content": "Just give me the cheat sheet."})
                    st.rerun()

    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    # AI PROCESSING (CHAT)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner('FocusFlow is thinking...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            models = requests.get(list_url).json()['models']
            model_name = next(m['name'] for m in models if 'generateContent' in m['supportedGenerationMethods'])
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
            
            user_msg = st.session_state.messages[-1]["content"].lower()
            
            # THE LOGIC FLOW
            if "cheat sheet" in user_msg or "just give me" in user_msg or "explain" in user_msg:
                full_prompt = f"""
                Context: {current_topic}. 
                The user has requested the full explanation or cheat sheet.
                Provide a concise, high-yield summary including formulas and key points.
                Do not ask a follow-up question here.
                """
            else:
                full_prompt = f"""
                You are an elite, critical-thinking Study Mentor. Context: {exam_goal}, {current_topic}.
                User message: {st.session_state.messages[-1]['content']}.
                
                YOUR RULES:
                1. NEVER start by agreeing with the user. If they are wrong, challenge their assumption immediately.
                2. Explain the core concept concisely.
                3. Ask ONE diagnostic follow-up question to test their understanding.
                4. DO NOT provide the cheat sheet or full answer to the question yet. Wait for the user to signal they are stuck.
                """
            
            payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
            response = requests.post(url, json=payload).json()
            if 'candidates' in response:
                answer = response['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
