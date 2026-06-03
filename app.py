import streamlit as st
import google.generativeai as genai

# Setup
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

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
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated! I see you're prepping for {exam_goal}. Let's master {current_topic}. What's the biggest challenge?"}]
        st.rerun()

# Initialize Chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hey! Set your goal in the sidebar and hit 'Sync My Goal' to begin!"}]

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
        with st.spinner('FocusFlow is thinking...'):
            try:
                # Find available model
                models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model_name = models[0] if models else 'gemini-pro'
                model = genai.GenerativeModel(model_name)
                
                context = f"Goal: {exam_goal}. Test Date: {test_date}. Subject: {current_topic}."
                full_prompt = f"You are a coach. Context: {context}. User asks: {prompt}. Provide mnemonics/cheat sheets."
                
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")
