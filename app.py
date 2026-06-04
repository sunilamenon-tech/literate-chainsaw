import streamlit as st
import requests
import base64

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR: Context
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "JEE Advanced", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Maths", "Physics", "Chemistry", "Biology", "History", "English", "Other"])
    test_date = st.date_input("When is your test?")
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated for {exam_goal}. Let's master {current_topic}!"}]
        st.rerun()

# TABS
tab1, tab2 = st.tabs(["💬 Chat", "📸 Upload/Analyze"])

# TAB 1: Chat Logic
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]
    
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and i > 0 and "cheat sheet" not in message["content"].lower():
                if st.button("⚡ Give me the Cheat Sheet!", key=f"btn_{i}"):
                    st.session_state.messages.append({"role": "user", "content": "Just give me the cheat sheet."})
                    st.rerun()

    if prompt := st.chat_input("What's on your mind?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

# TAB 2: Vision Logic
with tab2:
    uploaded_file = st.file_uploader("Upload a diagram to master", type=["jpg", "png"])
    if uploaded_file and st.button("Analyze & Quiz Me!"):
        with st.spinner('FocusFlow is analyzing...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            bytes_data = uploaded_file.getvalue()
            b64_image = base64.b64encode(bytes_data).decode('utf-8')
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            smart_prompt = f"You are a JEE/NEET tutor. Context: {exam_goal}, {current_topic}. Analyze this image. 1. Explain the concepts. 2. Create a 'Rapid Fire' diagnostic question based on the image."
            
            payload = {"contents": [{"parts": [{"text": smart_prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": b64_image}}]}]}
            response = requests.post(url, json=payload).json()
            answer = response['candidates'][0]['content']['parts'][0]['text']
            st.markdown(answer)

# AI Processing (Chat)
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner('FocusFlow is thinking...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            models = requests.get(list_url).json()['models']
            model_name = next(m['name'] for m in models if 'generateContent' in m['supportedGenerationMethods'])
            
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
            
            if "cheat sheet" in st.session_state.messages[-1]["content"].lower():
                full_prompt = f"Context: {current_topic}. Provide a high-yield cheat sheet for: {st.session_state.messages[-2]['content']}"
            else:
                full_prompt = f"Context: {current_topic}. User: {st.session_state.messages[-1]['content']}. Be a Socratic coach, ask one diagnostic question first."
            
            payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
            response = requests.post(url, json=payload).json()
            answer = response['candidates'][0]['content']['parts'][0]['text']
            
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
