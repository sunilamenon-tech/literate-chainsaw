import streamlit as st
import google.generativeai as genai

# Configure Google Gemini
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.set_page_config(page_title="FocusFlow", page_icon="⚡")
st.markdown("""<style>.stApp {background-color: #FFF9E6;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hey there! I'm your study coach. How are you feeling about your prep today?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What's on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # We define the model here, inside the function, to ensure it loads fresh
        model = genai.GenerativeModel('gemini-1.5-flash')
        full_prompt = "You are a Best-Friend Coach. Keep it short and empathetic: " + prompt
        response = model.generate_content(full_prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
