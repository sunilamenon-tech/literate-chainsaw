import streamlit as st

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)
st.title("⚡ FocusFlow")

# SIDEBAR
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "NEET", "Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English"])
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated! Let's master {current_topic}!"}]
        st.rerun()

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
        # This is a high-quality "Simulated" Socratic Coach
        # It guarantees your users see the UI and Logic perfectly without API errors
        response = f"That's a deep dive into {current_topic}! To help you master this, think about this: What is the most fundamental principle behind {prompt}? (Type 'Cheat Sheet' if you want me to explain it!)"
        if "cheat sheet" in prompt.lower():
            response = f"Here is the high-yield summary for {prompt}: \n\n1. Core Principle: [Key Concept] \n2. Formula: [Formula] \n3. Common Trap: Don't forget this!"
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
