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

# TABS
tab1, tab2 = st.tabs(["💬 Chat", "📸 Upload/Analyze"])

# TAB 1: CHAT
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]
    
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

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
                url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
                
                history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages[-5:]])
                
                full_prompt = f"""
                You are FocusFlow, a helpful Study Coach.
                Context: {exam_goal}, {current_topic}.
                Conversation History: {history_text}
                
                Rules:
                1. If user asks for 'cheat sheet', provide a high-yield summary.
                2. Otherwise, be a Socratic tutor: Ask ONE diagnostic question to check understanding.
                3. ALWAYS end your reply with a question to keep the student thinking.
                """
                
                payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
                response = requests.post(url, json=payload).json()
                if 'candidates' in response:
                    answer = response['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.rerun()

# TAB 2: UPLOAD
with tab2:
    if uploaded_file := st.file_uploader("Upload a diagram", type=["jpg", "png"]):
        st.image(uploaded_file, use_column_width=True)
        if st.button("Analyze & Quiz Me!"):
            st.warning("Analysis feature is under maintenance. Please use the Chat tab!")
