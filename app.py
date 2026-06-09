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
                # 1. Ask Google for the list of available models
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                models_response = requests.get(list_url).json()
                
                # 2. Find the first model that supports generateContent
                # This ensures we pick a name that actually exists in YOUR project
                valid_models = [m['name'] for m in models_response['models'] if 'generateContent' in m['supportedGenerationMethods']]
                model_name = valid_models[0] # Pick the first available one
                
                # 3. Call the API with the dynamically found model name
                url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
                user_msg = st.session_state.messages[-1]["content"]
                payload = {"contents": [{"parts": [{"text": f"You are a helpful study coach. User asks: {user_msg}"}]}]}
                
                response = requests.post(url, json=payload).json()
                
                if 'candidates' in response:
                    answer = response['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.rerun()
                else:
                    st.error(f"AI Error: {response}")
            except Exception as e:
                st.error(f"Error: {e}")
