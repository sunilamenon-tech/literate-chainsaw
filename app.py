import streamlit as st
import google.generativeai as genai

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;}</style>""", unsafe_allow_html=True)

# SIDEBAR: The "Proactive" Context
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.text_input("Exam/Goal", "JEE Main")
    test_date = st.date_input("When is your test?")
    current_topic = st.text_input("What are you studying right now?")
    st.info("Fill this in so I can keep you on track!")

st.title("⚡ FocusFlow")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": f"Hi! I'm ready to help you with {current_topic} for your {exam_goal} prep!"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What's on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # The AI now gets the syllabus context!
        context = f"Goal: {exam_goal}. Test Date: {test_date}. Current Focus: {current_topic}."
        full_prompt = f"You are FocusFlow, a study coach. Context: {context}. User asks: {prompt}. Provide mnemonics or cheat sheets if needed."
        
        response = model.generate_content(full_prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
