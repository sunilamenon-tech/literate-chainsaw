import streamlit as st
import requests
import base64

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# Sidebar
with st.sidebar:
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "NEET", "Boards"])
    current_topic = st.selectbox("Subject", ["Maths", "Physics", "Chemistry", "Biology"])
    if st.button("Sync Goal"): st.rerun()

tab1, tab2 = st.tabs(["💬 Chat", "📸 Upload"])

# Chat Logic
with tab1:
    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages: st.chat_message(msg["role"]).markdown(msg["content"])

    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").markdown(prompt)
        
        with st.chat_message("assistant"):
            api_key = st.secrets["GOOGLE_API_KEY"]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": f"You are a coach. Subject: {current_topic}. Help: {prompt}"}]}]}
            
            try:
                resp = requests.post(url, json=payload).json()
                answer = resp['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except:
                st.error("I'm thinking! Try again in a moment.")

# Upload Logic (Simplified & Safe)
with tab2:
    uploaded_file = st.file_uploader("Upload image", type=["jpg", "png"])
    if uploaded_file and st.button("Analyze"):
        st.warning("Analysis feature is currently under maintenance. Please use the Chat tab for your questions!")
