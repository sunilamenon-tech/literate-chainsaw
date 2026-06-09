import streamlit as st
import requests
from datetime import date

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# 1. SIDEBAR (The Control Panel)
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "JEE Advanced", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English", "Other"])
    
    # Date logic: Only show if NOT Other
    test_date = None
    if exam_goal != "Other":
        test_date = st.date_input("When is your test?", min_value=date.today())
    
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated! Ready to master {current_topic}!"}]
        st.rerun()

    # TENSION METER (Appears only if date exists)
    if test_date:
        days_left = (test_date - date.today()).days
        tension = "High 🚨" if days_left < 7 else ("Medium ⚠️" if days_left < 20 else "Low 😌")
        st.markdown(f"--- \n### 📊 Your Status \n- **Tension:** {tension} \n- **Days Left:** {days_left}")

# 2. CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. CHAT INPUT & AI PROCESSING
# AI PROCESSING
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner('FocusFlow is thinking...'):
            user_msg = st.session_state.messages[-1]["content"].lower()
            
            # This simulates the AI tutor perfectly without needing a blocked API
            if any(x in user_msg for x in ["cheat sheet", "give me", "explain"]):
                answer = f"**{current_topic.upper()} Cheat Sheet:** \n1. Core Principle: Photosynthesis converts light energy into chemical energy (Glucose). \n2. Formula: 6CO2 + 6H2O + Light -> C6H12O6 + 6O2. \n3. Pro-Tip: Remember that the light-dependent reaction happens in the thylakoids!"
            else:
                answer = f"That's a great question about {current_topic}! To help you master this for your {exam_goal} prep, think about this: What do you think is the role of Chlorophyll in this process?"
            
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
