import streamlit as st
import requests
import base64

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "JEE Advanced", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English", "Other"])
    test_date = st.date_input("When is your test?")
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated for {exam_goal}. Let's master {current_topic}!"}]
        st.rerun()

# INITIALIZE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]

# DISPLAY CHAT
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # LOGIC: 
        # 1. If AI asked a question (Diagnostic), offer "Give me the explanation/cheat sheet"
        # 2. If AI gave explanation/cheat sheet, offer "Analyze & Quiz Me!"
        if message["role"] == "assistant" and i > 0:
            if "?" in message["content"] and "cheat sheet" not in message["content"].lower():
                if st.button("⚡ Just give me the explanation/cheat sheet", key=f"ans_{i}"):
                    st.session_state.messages.append({"role": "user", "content": "Just give me the explanation and cheat sheet."})
                    st.rerun()
            elif "cheat sheet" in message["content"].lower() or "formula" in message["content"].lower():
                if st.button("⚡ Analyze & Quiz Me!", key=f"quiz_{i}"):
                    st.session_state.messages.append({"role": "user", "content": "Give me a quiz based on this."})
                    st.rerun()

# CHAT INPUT
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# AI PROCESSING
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner('FocusFlow is thinking...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            models = requests.get(list_url).json()['models']
            model_name = next(m['name'] for m in models if 'generateContent' in m['supportedGenerationMethods'])
            
            user_msg = st.session_state.messages[-1]["content"].lower()
            
            # THE LOGIC FLOW
            if "give me a quiz" in user_msg:
                full_prompt = f"Context: {current_topic}. Based on the previous explanation, provide a 3-question quiz to test mastery."
            elif "cheat sheet" in user_msg or "just give me" in user_msg:
                full_prompt = f"Context: {current_topic}. Provide a concise, high-yield cheat sheet for: {st.session_state.messages[-2]['content']}. Include key formulas."
            else:
                full_prompt = f"Context: {current_topic}. User: {st.session_state.messages[-1]['content']}. Be a Socratic coach, ask ONE diagnostic question to start."
            
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
            
            response = requests.post(url, json=payload).json()
            if 'candidates' in response:
                answer = response['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
