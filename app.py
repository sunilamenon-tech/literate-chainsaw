import streamlit as st
import google.generativeai as genai

# Setup
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR
with st.sidebar:
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "NEET", "10th Boards"])
    current_topic = st.selectbox("Subject", ["Biology", "Physics", "Chemistry", "Maths"])
    test_date = st.date_input("Test Date")
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": "Context updated! Ready to master " + current_topic}]
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Hit 'Sync My Goal' and ask me anything!"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What's on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner('Thinking...'):
            try:
                # DYNAMIC MODEL FINDER: This looks for what your API key is allowed to use
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                # Pick the first one that exists
                model_name = available_models[0] if available_models else 'gemini-1.5-flash'
                
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(f"You are a coach. Subject: {current_topic}. User asks: {prompt}. Ask a diagnostic question first.")
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error: {e}")
