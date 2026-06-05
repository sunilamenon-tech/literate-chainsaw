import streamlit as st
import requests
import base64

# --- SETTINGS ---
st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# --- SIDEBAR (DO NOT CHANGE) ---
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "JEE Advanced", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English", "Other"])
    test_date = st.date_input("When is your test?")
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated! Prepping for {exam_goal}. Let's master {current_topic}!"}]
        st.rerun()

# --- TABS ---
tab1, tab2 = st.tabs(["💬 Chat", "📸 Upload/Analyze"])

# --- TAB 1: CHAT (Existing Logic) ---
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

# --- TAB 2: IMAGE UPLOAD & QUIZ LOGIC (The New Feature) ---
with tab2:
    uploaded_file = st.file_uploader("Upload a diagram", type=["jpg", "png"])
    if uploaded_file:
        st.image(uploaded_file, use_column_width=True)
        if st.button("Analyze & Quiz Me!"):
            with st.spinner('FocusFlow is analyzing...'):
                api_key = st.secrets["GOOGLE_API_KEY"]
                b64_image = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
                
                # Fetch model dynamically
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                model_name = next(m['name'] for m in requests.get(list_url).json()['models'] if 'generateContent' in m['supportedGenerationMethods'])
                
                url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
                
                # Socratic Prompt for Images
                prompt = "Analyze this diagram. 1. Explain it clearly. 2. Ask ONE quiz question to check understanding."
                payload = {"contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/jpeg", "data": b64_image}}]}]}
                
                response = requests.post(url, json=payload).json()
                answer = response['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)

# --- AI PROCESSING (CHAT) ---
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner('Thinking...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            model_name = next(m['name'] for m in requests.get(list_url).json()['models'] if 'generateContent' in m['supportedGenerationMethods'])
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
            
            if "cheat sheet" in st.session_state.messages[-1]["content"].lower():
                prompt_text = f"Context: {current_topic}. Cheat Sheet for: {st.session_state.messages[-2]['content']}"
            else:
                prompt_text = f"Context: {current_topic}. User: {st.session_state.messages[-1]['content']}. Be a Socratic coach."
            
            payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
            response = requests.post(url, json=payload).json()
            answer = response['candidates'][0]['content']['parts'][0]['text']
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
