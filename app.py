import streamlit as st
import requests

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR: Context & Sync
with st.sidebar:
    st.header("🎯 Your Study Context")
    
    # Updated Goals
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "NEET", "Class 10", "Class 12", "Other"])
    
    # Updated Subjects
    current_topic = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English", "Hindi"])
    
    # Date Selection
    test_date = st.date_input("When is your test?")
    
    # Sync Button
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated! Prepping for {exam_goal} {current_topic}. Ready to master this?"}]
        st.rerun()

# INITIALIZE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal in the sidebar and hit 'Sync My Goal' to begin!"}]

# CHAT DISPLAY
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# CHAT INPUT
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()
