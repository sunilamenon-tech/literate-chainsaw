import streamlit as st
import requests

st.title("⚡ FocusFlow")

# SIDEBAR (Just to keep your UI consistent)
with st.sidebar:
    st.write("Sidebar is working!")

# CHAT DISPLAY
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# CHAT INPUT
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner('Thinking...'):
            try:
                # Use the hardcoded stable URL for the Pro model
                api_key = st.secrets["GOOGLE_API_KEY"]
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                payload = {"contents": [{"parts": [{"text": f"You are a helpful study coach. User: {prompt}"}]}]}
                response = requests.post(url, json=payload).json()
                
                if 'candidates' in response:
                    answer = response['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"AI response error: {response}")
            except Exception as e:
                st.error(f"Error: {e}")
