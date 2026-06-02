import streamlit as st
import requests

# App Configuration
st.set_page_config(page_title="FocusFlow", page_icon="⚡")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")
mood = st.radio("HOW ARE YOU FEELING?", ["Stressed (Need calm support)", "Focused (Let's go fast)"])
user_input = st.text_area("WHAT DO YOU NEED HELP WITH?")

if st.button("Get Help"):
    if user_input:
        with st.spinner('FocusFlow is thinking...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            # We use the REST API directly - it is much more robust
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [{"parts": [{"text": f"You are a Best-Friend Coach. Mood: {mood}. Help the user with: {user_input}"}]}]
            }
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                st.success("Here is your high-yield cheat sheet:")
                st.write(data['candidates'][0]['content']['parts'][0]['text'])
            else:
                st.error(f"Error {response.status_code}: {response.text}")
    else:
        st.warning("Please enter a topic!")
