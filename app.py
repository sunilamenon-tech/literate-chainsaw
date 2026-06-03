import streamlit as st
import google.generativeai as genai

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR: The "Context Engine"
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.text_input("Exam/Goal", "JEE Main")
    test_date = st.date_input("When is your test?")
    current_topic = st.text_input("What are you studying right now?", "Maths")
    st.info("I'm tracking your progress!")

# Initialize Chat
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": f"Hey! Ready to crush {current_topic} for your {exam_goal} exam?"}]

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# CHAT LOGIC (Now with Live Context)
if prompt := st.chat_input("What's on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner('FocusFlow is thinking...'):
            # The AI pulls the context FROM THE SIDEBAR every time it talks
            context = f"Goal: {exam_goal}. Test Date: {test_date}. Studying: {current_topic}."
            full_prompt = f"System: You are a coach. {context}. User asks: {prompt}. Provide mnemonics or cheat sheets."
            
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
