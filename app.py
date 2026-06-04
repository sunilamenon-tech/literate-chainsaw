import streamlit as st
import google.generativeai as genai
from PIL import Image

# Setup
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "JEE Advanced", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Maths", "Physics", "Chemistry", "Biology", "History", "English", "Other"])
    test_date = st.date_input("When is your test?")
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated! Prepping for {exam_goal}. Let's master {current_topic}."}]
        st.rerun()

# Initialize Chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Upload an image or ask me anything!"}]

# File Uploader
uploaded_file = st.file_uploader("Upload a diagram or note (Optional)", type=["jpg", "jpeg", "png"])

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Logic
if prompt := st.chat_input("What's on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner('FocusFlow is analyzing...'):
            context = f"Goal: {exam_goal}. Test Date: {test_date}. Subject: {current_topic}."
            
            # Prepare content
            content_parts = [f"You are a Socratic coach. Context: {context}. User asks: {prompt}. Ask diagnostic questions, then cheat sheet."]
            
            if uploaded_file:
                img = Image.open(uploaded_file)
                content_parts.append(img)
                st.image(img, caption="Analyzing your image...", use_column_width=True)

            response = model.generate_content(content_parts)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
