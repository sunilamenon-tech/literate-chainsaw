import streamlit as st
from datetime import date

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "JEE Advanced", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English", "Other"])
    
    test_date = None
    if exam_goal != "Other":
        test_date = st.date_input("When is your test?", min_value=date.today())
    
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated! Prepping for {exam_goal}. Let's master {current_topic}!"}]
        st.rerun()

    if test_date:
        days_left = (test_date - date.today()).days
        tension = "High 🚨" if days_left < 7 else ("Medium ⚠️" if days_left < 20 else "Low 😌")
        st.markdown(f"--- \n### 📊 Your Status \n- **Tension:** {tension} \n- **Days Left:** {days_left}")

# CHAT
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        # SIMULATED INTELLIGENCE
        if any(x in prompt.lower() for x in ["cheat sheet", "give me", "explain"]):
            answer = f"**{current_topic} Cheat Sheet:** \n1. Core Principle: Focus on fundamental laws. \n2. Key Formula: Review your standard textbook equations. \n3. Pro-Tip: Active recall is 2x more effective than re-reading."
        else:
            answer = f"That's a deep dive into {current_topic}! To help me understand where you're at, what's the most confusing part about '{prompt}' for you right now?"
        
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()
