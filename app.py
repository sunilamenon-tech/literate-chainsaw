import streamlit as st
import requests
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

# CHAT DISPLAY
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# CHAT INPUT & AI
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner('Thinking...'):
            try:
                api_key = st.secrets["GOOGLE_API_KEY"]
                # We use the direct, most stable model name
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                full_prompt = f"Context: {exam_goal}, {current_topic}. User: {prompt}. Rules: Act as a coach, ask one diagnostic question first. Do not agree immediately."
                
                payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
                response = requests.post(url, json=payload).json()
                
                if 'candidates' in response:
                    answer = response['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error("AI Error: Check API Quota or Billing.")
            except Exception as e:
                st.error(f"Error: {e}")
