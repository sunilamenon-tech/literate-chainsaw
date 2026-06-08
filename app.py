import streamlit as st
import requests
import base64
from datetime import date

# 1. PAGE CONFIG
st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# 2. SIDEBAR (Includes Goals, Sync, and Tension Meter)
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
    st.markdown("---")
    st.markdown(f"### 📊 Your Status")
    st.markdown(f"- **Tension:** {tension}")
    st.markdown(f"- **Days Left:** {days_left}")

# 3. TABS
tab1, tab2 = st.tabs(["💬 Chat", "📸 Upload/Analyze"])

# TAB 1: CHAT
# TAB 1: CHAT
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]
    
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"].replace("[QUIZ_ACTIVE]", "")) # Hide the tag from user
            
            # SHOW BUTTON ONLY IF:
            # 1. AI is the sender.
            # 2. The AI marked this message with [QUIZ_ACTIVE] (meaning it asked a question).
            # 3. User hasn't already asked for the cheat sheet.
            if message["role"] == "assistant" and i > 0 and "[QUIZ_ACTIVE]" in message["content"]:
                if st.button("⚡ Give me the Cheat Sheet!", key=f"btn_{i}"):
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
                if "cheat sheet" in user_msg or "just give me" in user_msg or "explain" in user_msg:
                    full_prompt = f"Context: {current_topic}. Provide a concise high-yield cheat sheet for: {st.session_state.messages[-2]['content']}. Be direct."
                else:
                    full_prompt = f"Context: {current_topic}. User: {st.session_state.messages[-1]['content']}. Rules: Do not agree immediately. Challenge the user. Ask ONE diagnostic question to start."
                
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
