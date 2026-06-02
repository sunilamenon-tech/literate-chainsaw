import streamlit as st
import time

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
            time.sleep(2) # Simulates AI thinking
            if "Stressed" in mood:
                st.success("Here is your high-yield cheat sheet:")
                st.write("Hey! Take a deep breath. 😮‍💨 I know Periodic Table feels overwhelming, but just focus on the 'Trends' (Ionization energy, Atomic radius). Don't memorize everything today. You’re doing great!")
            else:
                st.success("Here is your high-yield cheat sheet:")
                st.write("Let's crush this! Focus on the exceptions in the table. You've got the momentum—let's keep it going! 🔥")
    else:
        st.warning("Please enter a topic!")
