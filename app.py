import streamlit as st
import requests
import base64
from datetime import date

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR: Context & Sync
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "JEE Advanced", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English", "Other"])
    test_date = st.date_input("When is your test?")
    
    # By clicking this, we force the whole app to refresh with the new date
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated! Prepping for {exam_goal}. Let's master {current_topic}!"}]
        st.rerun()

    # GROWTH ENGINE - Now it recalculates every time Sync is clicked
    from datetime import date
    days_left = (test_date - date.today()).days
    tension = "High" if days_left < 7 else ("Medium" if days_left < 20 else "Low")
    
    if "q_count" not in st.session_state: st.session_state.q_count = 0
    archetype = "Explorer" if st.session_state.q_count < 5 else ("Scholar" if st.session_state.q_count < 15 else "Master")
    
    st.markdown(f"--- \n### 📊 Your Status \n- **Tension:** {tension} \n- **Archetype:** {archetype}")

# --- TABS ---
tab1, tab2 = st.tabs(["💬 Chat", "📸 Upload/Analyze"])

# TAB 1: CHAT
with tab1:
    if "messages" not in st.session_state: st.session_state.messages = []
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and i > 0 and "cheat sheet" not in msg["content"].lower():
                if st.button("⚡ Give me the Cheat Sheet!", key=f"btn_{i}"):
                    st.session_state.messages.append({"role": "user", "content": "Just give me the cheat sheet."})
                    st.rerun()

    if prompt := st.chat_input("Ask a question..."):
        st.session_state.q_count += 1
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

# TAB 2: UPLOAD
with tab2:
    if uploaded_file := st.file_uploader("Upload diagram", type=["jpg", "png"]):
        st.image(uploaded_file, use_column_width=True)
        if st.button("Analyze & Quiz Me!"):
            st.session_state.q_count += 1
            st.rerun()

# AI PROCESSING
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner('FocusFlow is thinking...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            model_name = next(m['name'] for m in requests.get(list_url).json()['models'] if 'generateContent' in m['supportedGenerationMethods'])
            
            payload = {"contents": [{"parts": [{"text": f"You are a coach. Mood: {archetype}. Context: {exam_goal}, {current_topic}. User: {st.session_state.messages[-1]['content']}. Ask a diagnostic question."}]}]}
            response = requests.post(f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}", json=payload).json()
            answer = response['candidates'][0]['content']['parts'][0]['text']
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
