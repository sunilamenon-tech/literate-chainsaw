import streamlit as st
import requests
import base64
from datetime import date

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "JEE Advanced", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English", "Other"])
    test_date = st.date_input("When is your test?", min_value=date.today())
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated for {exam_goal}. Let's master {current_topic}!"}]
        st.rerun()
    
    days_left = (test_date - date.today()).days
    tension = "High 🚨" if days_left < 7 else ("Medium ⚠️" if days_left < 20 else "Low 😌")
    st.markdown(f"--- \n### 📊 Your Status \n- **Tension:** {tension} \n- **Days Left:** {days_left}")

# TABS
tab1, tab2 = st.tabs(["💬 Chat", "📸 Upload/Analyze"])

# TAB 1
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]
    
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and i > 0 and "cheat sheet" not in message["content"].lower():
                if st.button("⚡ Give me the Cheat Sheet!", key=f"btn_{i}"):
                    st.session_state.messages.append({"role": "user", "content": "Just give me the cheat sheet."})
                    st.rerun()

    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    # AI PROCESSING (CHAT)
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.chat_message("assistant"):
            with st.spinner('FocusFlow is thinking...'):
                api_key = st.secrets["GOOGLE_API_KEY"]
                list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
                models = requests.get(list_url).json()['models']
                model_name = next(m['name'] for m in models if 'generateContent' in m['supportedGenerationMethods'])
                url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
                
                user_msg = st.session_state.messages[-1]["content"].lower()
                if any(word in user_msg for word in ["just explain", "give me the answer", "help me with", "cheat sheet"]):
                    full_prompt = f"Context: {current_topic}. Provide a concise cheat sheet for: {st.session_state.messages[-2]['content']}"
                else:
                    full_prompt = f"Context: {current_topic}. User: {st.session_state.messages[-1]['content']}. Be a Socratic coach, ask one diagnostic question first."
                
                response = requests.post(url, json={"contents": [{"parts": [{"text": full_prompt}]}]}).json()
                if 'candidates' in response:
                    answer = response['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.rerun()

# TAB 2
with tab2:
    uploaded_file = st.file_uploader("Upload a diagram", type=["jpg", "png"])
    if uploaded_file and st.button("Analyze & Quiz Me!"):
        st.warning("Feature in progress! Please use the Chat tab.")
