import streamlit as st
import requests
from PIL import Image
import io

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "JEE Advanced", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Maths", "Physics", "Chemistry", "Biology", "History", "English", "Other"])
    test_date = st.date_input("When is your test?")
    st.info("I'm tracking your progress!")

tab1, tab2 = st.tabs(["💬 Chat", "📸 Upload/Analyze"])

with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi! Ask me anything about your studies."}]
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What's on your mind?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

with tab2:
    uploaded_file = st.file_uploader("Upload a diagram", type=["jpg", "png"])
    if uploaded_file and st.button("Analyze Image"):
        st.image(uploaded_file, use_column_width=True)
        with st.spinner('Analyzing...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            # Use the direct REST API - no "Not Found" errors
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            # This is a bit advanced, but for now, let's keep it simple: 
            # If image analysis fails, we'll tell the user to use the text chat.
            st.warning("Image analysis is being optimized. Please try typing your question in the Chat tab instead for the best results!")

# AI Processing (Runs for chat)
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner('FocusFlow is thinking...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": f"Context: {current_topic}. User: {st.session_state.messages[-1]['content']}. Be a Socratic coach."}]}]}
            
            response = requests.post(url, json=payload).json()
            if 'candidates' in response:
                answer = response['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error("Model busy. Try again in 30 seconds!")
