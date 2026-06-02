import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="FocusFlow", page_icon="⚡")
st.markdown("""<style>.stApp {background-color: #FFF9E6;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")
st.write("Your personal study companion. Let's crush it together. 💪")

# Configure AI
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey there! I'm your study coach. Feeling stressed or ready to focus today?"}
    ]

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept Input
if prompt := st.chat_input("What's on your mind?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner('FocusFlow is thinking...'):
            # Combine history into a context
            context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            response = model.generate_content(f"You are a Best-Friend Coach. Here is the conversation so far:\n{context}")
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
