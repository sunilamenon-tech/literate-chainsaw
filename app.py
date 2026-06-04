import streamlit as st
import requests

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR: Full restored list
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "JEE Advanced", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Maths", "Physics", "Chemistry", "Biology", "History", "English", "Other"])
    test_date = st.date_input("When is your test?")
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated for {exam_goal}. Let's master {current_topic}!"}]
        st.rerun()

# Initialize Chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# FEATURE: Emergency Cheat Sheet Button
if st.button("⚡ Give me the Cheat Sheet immediately!"):
    st.session_state.messages.append({"role": "user", "content": "Just give me the cheat sheet."})
    st.rerun()

# Chat Logic
if prompt := st.chat_input("What's on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner('FocusFlow is thinking...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            # Auto-find model
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            models = requests.get(list_url).json()['models']
            model_name = next(m['name'] for m in models if 'generateContent' in m['supportedGenerationMethods'])
            
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
            
            # Logic: If they click the button or type 'cheat sheet', skip Socratic questions
            if "cheat sheet" in prompt.lower() or prompt == "Just give me the cheat sheet.":
                full_prompt = f"Context: {current_topic}. Provide a high-yield cheat sheet for: {prompt}."
            else:
                full_prompt = f"Context: {current_topic}. User: {prompt}. Be a Socratic coach, ask one diagnostic question first."
            
            payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
            response = requests.post(url, json=payload).json()
            answer = response['candidates'][0]['content']['parts'][0]['text']
            
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
