import streamlit as st
import google.generativeai as genai

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("⚡ FocusFlow Debugger")

if st.button("Check Available Models & Chat"):
    try:
        # Get the first available model that supports generateContent
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not models:
            st.error("No models found. Check your API Key permissions.")
        else:
            selected_model_name = models[0]
            st.write(f"Using model: {selected_model_name}")
            model = genai.GenerativeModel(selected_model_name)
            response = model.generate_content("Hello! Are you working?")
            st.success(f"Success! AI says: {response.text}")
            
    except Exception as e:
        st.error(f"Error: {e}")
