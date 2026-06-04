import streamlit as st
import requests

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR
with st.sidebar:
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "NEET", "10th Boards"])
    current_topic = st.selectbox("Subject", ["Maths", "Physics", "Chemistry", "Biology"])
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated for {current_topic}."}]
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Sync your goal and ask me anything!"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What's on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner('FocusFlow is thinking...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            
            # 1. Fetch available models first to be 100% sure of the name
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            list_resp = requests.get(list_url)
            
            if list_resp.status_code == 200:
                models = list_resp.json()['models']
                # Pick a model that supports generateContent
                model_name = next(m['name'] for m in models if 'generateContent' in m['supportedGenerationMethods'])
                
                # 2. Use that exact name
                url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
                payload = {"contents": [{"parts": [{"text": f"Context: {current_topic}. User: {prompt}. Be a Socratic coach."}]}]}
                
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    answer = response.json()['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            else:
                st.error("Could not fetch models. Check your API Key.")
