import streamlit as st
import requests
import base64
from datetime import date

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR: Context & Status
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

# TABS
tab1, tab2 = st.tabs(["💬 Chat", "📸 Upload/Analyze"])

# TAB 1: CHAT
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]
    
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Button logic: only shows if AI didn't already give a cheat sheet
            if message["role"] == "assistant" and i > 0 and "cheat sheet" not in message["content"].lower():
                if st.button("⚡ Stuck? Get a hint/cheat sheet", key=f"btn_{i}"):
                    st.session_state.messages.append({"role": "user", "content": "Just give me the cheat sheet."})
                    st.rerun()

    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

# TAB 2: UPLOAD
with tab2:
    if uploaded_file := st.file_uploader("Upload a diagram", type=["jpg", "png"]):
        st.image(uploaded_file, use_column_width=True)
        if st.button("Analyze & Quiz Me!"):
            st.warning("Analysis feature is coming soon! Please use the Chat tab to discuss this topic.")

# AI PROCESSING
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner('FocusFlow is thinking...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            # 1. Fetch models reliably
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            try:
                models_data = requests.get(list_url).json()
                model_name = next(m['name'] for m in models_data['models'] if 'generateContent' in m['supportedGenerationMethods'])
                url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
                
                # 2. Logic for Prompt
                user_msg = st.session_state.messages[-1]["content"].lower()
                if "cheat sheet" in user_msg or "give me the answer" in user_msg:
                    full_prompt = f"Context: {current_topic}. Provide a concise cheat sheet for: {st.session_state.messages[-2]['content']}"
                else:
                    full_prompt = f"You are a Socratic tutor. Context: {exam_goal}, {current_topic}. User: {st.session_state.messages[-1]['content']}. Ask ONE diagnostic question first."
                
                # 3. Call API
                payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
                response = requests.post(url, json=payload).json()
                
                # 4. Extract Answer Safely
                if 'candidates' in response and len(response['candidates']) > 0:
                    answer = response['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.rerun()
                else:
                    st.error("The AI didn't return an answer. It might be a safety block. Try rephrasing.")
            except Exception as e:
                st.error(f"Engine Error: {e}")
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
