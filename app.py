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
    
    # Conditional Date Picker
    if exam_goal != "Other":
        test_date = st.date_input("When is your test?", min_value=date.today())
    else:
        test_date = None
    
    if st.button("Sync My Goal"):
        # Custom dynamic message
        welcome_msg = f"Context updated! Let's master {current_topic} for {exam_goal}." if exam_goal != "Other" else f"Context updated! Let's master {current_topic}."
        st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
        st.rerun()
        
    if test_date:
        days_left = (test_date - date.today()).days
        tension = "High 🚨" if days_left < 7 else ("Medium ⚠️" if days_left < 20 else "Low 😌")
        st.markdown(f"--- \n### 📊 Your Status \n- **Tension:** {tension} \n- **Days Left:** {days_left}")

# CHAT
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and i > 0:
            if "?" in message["content"] and not any(x in message["content"].lower() for x in ["cheat sheet", "formula", "here is"]):
                if st.button("⚡ Stuck? Get a hint/cheat sheet", key=f"btn_{i}"):
                    st.session_state.messages.append({"role": "user", "content": "Just give me the cheat sheet."})
                    st.rerun()

if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# AI PROCESSING
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner('Thinking...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            models = requests.get(list_url).json()['models']
            model_name = next(m['name'] for m in models if 'generateContent' in m['supportedGenerationMethods'])
            
            user_msg = st.session_state.messages[-1]["content"].lower()
            if any(x in user_msg for x in ["cheat sheet", "give me", "explain"]):
                full_prompt = f"Context: {exam_goal}, {current_topic}. Provide a concise high-yield cheat sheet for: {st.session_state.messages[-2]['content']}. Be direct."
            else:
                full_prompt = f"Context: {exam_goal}, {current_topic}. User: {user_msg}. Rules: Act as Socratic Coach. Ask ONE diagnostic question."
            
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
            response = requests.post(url, json={"contents": [{"parts": [{"text": full_prompt}]}]}).json()
            
            if 'candidates' in response:
                answer = response['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
