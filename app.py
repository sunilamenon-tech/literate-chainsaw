import streamlit as st
import google.generativeai as genai

# Configure Google Gemini
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = model = genai.GenerativeModel('gemini-pro')
# App Configuration
st.set_page_config(page_title="FocusFlow", page_icon="⚡")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")
st.write("Your personal study companion. Let's crush it together. 💪")

mood = st.radio("HOW ARE YOU FEELING?", ["Stressed (Need calm support)", "Focused (Let's go fast)"])
user_input = st.text_area("WHAT DO YOU NEED HELP WITH?")

if st.button("Get Help"):
    if user_input:
        with st.spinner('FocusFlow is thinking...'):
            try:
                # The "Pro" Prompt Logic
                prompt = f"""
                You are a top-tier tutor for JEE/NEET. 
                The student is feeling: {mood}.
                Topic to explain: {user_input}

                Please provide a High-Yield Cheat Sheet including:
                1. The 3 most important concepts (The 80/20 rule).
                2. A simple, non-academic analogy to help visualize it.
                3. One 'Check-your-knowledge' practice question with the answer.
                Keep it encouraging and very concise.
                """
                
                response = model.generate_content(prompt)
                st.success("Here is your high-yield cheat sheet:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Waiting for quota reset. Error: {e}")
    else:
        st.warning("Please enter a topic!")
