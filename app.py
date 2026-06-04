import streamlit as st
import google.generativeai as genai
from PIL import Image

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="centered")
st.markdown("""<style>.stApp {background-color: #FFF9E6;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR: Control Panel
with st.sidebar:
    st.header("🎯 Study Context")
    exam_goal = st.selectbox("Exam", ["JEE Main", "NEET", "Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Maths", "Physics", "Chemistry", "Biology", "Other"])
    if st.button("Sync Context"):
        st.session_state.messages = [{"role": "assistant", "content": f"Ready to master {current_topic} for {exam_goal}!"}]
        st.rerun()

# MAIN TABS: Cleaner Layout
tab1, tab2 = st.tabs(["💬 Chat", "📸 Upload/Analyze"])

with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi! Ask me anything about your studies."}]
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

with tab2:
    uploaded_file = st.file_uploader("Upload an image for analysis", type=["jpg", "png"])
    if uploaded_file:
        st.image(uploaded_file, use_column_width=True)
        if st.button("Analyze Image"):
            img = Image.open(uploaded_file)
            # Send to AI
            response = model.generate_content(["Explain this image as a study coach", img])
            st.markdown(response.text)
