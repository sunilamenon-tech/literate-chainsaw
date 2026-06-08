import streamlit as st
import requests
from datetime import date

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR
with st.sidebar:
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "JEE Advanced", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English", "Other"])
    test_date = st.date_input("When is your test?", min_value=date.today())
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated! Ready to master {current_topic}!"}]
        st.rerun()

# TAB LOGIC
tab1, tab2 = st.tabs(["💬 Chat", "📸 Upload"])

with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # DISPLAY USER MESSAGE
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI PROCESSING
        with st.chat_message("assistant"):
            with st.spinner('Thinking...'):
                try:
                    api_key = st.secrets["GOOGLE_API_KEY"]
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                    payload = {"contents": [{"parts": [{"text": f"Context: {exam_goal}, {current_topic}. User: {prompt}. Be a Socratic Coach: Ask one diagnostic question first."}]}]}
                    
                    response = requests.post(url, json=payload).json()
                    
                    if 'candidates' in response:
                        answer = response['candidates'][0]['content']['parts'][0]['text']
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        st.error(f"AI Error: {response}") # This shows us the REAL error
                except Exception as e:
                    st.error(f"Connection Error: {e}")
        st.rerun()

with tab2:
    st.info("Analysis feature is under maintenance.")
