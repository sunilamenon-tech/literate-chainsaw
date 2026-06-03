import streamlit as st
import google.generativeai as genai

# Setup
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR: Updated with your full list
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.selectbox("Exam/Goal", 
                             ["JEE Main", "JEE Advanced", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", 
                                 ["Maths", "Physics", "Chemistry", "Biology", "History", "English", "Other"])
    test_date = st.date_input("When is your test?")
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated! Prepping for {exam_goal}. Let's master {current_topic}. What's your biggest challenge?"}]
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
                # Find available model dynamically
                models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model_name = models[0] if models else 'gemini-1.5-flash'
                model = genai.GenerativeModel(model_name)
                
                context = f"Goal: {exam_goal}. Test Date: {test_date}. Subject: {current_topic}."
                
                # The Smart Socratic Prompt
                full_prompt = f"""
                You are a supportive Socratic Study Coach. Context: {context}. 
                User message: {prompt}.
                
                Task:
                1. If the user seems lost or explicitly asks for help/answer, provide a clear explanation and a high-yield cheat sheet.
                2. If the user is answering well, ask a challenging follow-up question to test their understanding.
                3. Always keep the tone encouraging and best-friend like.
                """
                
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                # If Flash hits a quota error, automatically try Pro
                if "429" in str(e):
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    response = model.generate_content(full_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                else:
                    st.error(f"Error: {e}")
