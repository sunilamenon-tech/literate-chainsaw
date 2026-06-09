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
        
        # IMPROVED BUTTON LOGIC
        # Only shows if: 1. It's AI 2. It has a question 3. It's NOT a cheat sheet/summary
        if message["role"] == "assistant" and i > 0:
            content_lower = message["content"].lower()
            if "?" in content_lower and not any(word in content_lower for word in ["cheat sheet", "here is", "formula", "summar"]):
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
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                models_data = requests.get(list_url).json()
                model_name = next(m['name'] for m in models_data['models'] if 'generateContent' in m['supportedGenerationMethods'])
                
                url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
                user_msg = st.session_state.messages[-1]["content"].lower()
                
                if any(x in user_msg for x in ["cheat sheet", "give me", "explain"]):
                    full_prompt = f"Context: {current_topic}. Provide a concise high-yield cheat sheet for: {st.session_state.messages[-2]['content']}. Be direct."
                else:
                    full_prompt = f"Context: {current_topic}. User: {user_msg}. Rules: Act as Socratic Coach. Challenge assumptions. Ask ONE diagnostic question."
                
                payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
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
