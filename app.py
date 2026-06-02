import streamlit as st
import google.generativeai as genai
import os

# Configure Google Gemini
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

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
               model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"You are a Best-Friend Coach. Mood: {mood}. Help the user with: {user_input}"
                response = model.generate_content(prompt)
                st.success("Here is your high-yield cheat sheet:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error details: {e}")
                st.write("Available models:")
                for m in genai.list_models():
                    st.write(m.name)
