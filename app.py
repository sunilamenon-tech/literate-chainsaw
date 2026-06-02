import streamlit as st
import google.generativeai as genai

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("Debug Mode: Finding your Model")

if st.button("List Available Models"):
    st.write("Here are the models your API key can access:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            st.write(f"Model Name: {m.name}")
