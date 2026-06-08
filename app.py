import streamlit as st

st.title("⚡ FocusFlow Test")

# Test Sidebar
with st.sidebar:
    st.write("Sidebar is working!")
    if st.button("Test Sync"):
        st.success("Button works!")

# Test Chat
if prompt := st.chat_input("Say something..."):
    st.chat_message("user").markdown(prompt)
    with st.chat_message("assistant"):
        st.markdown(f"I heard you say: {prompt}. If you see this, the app logic is 100% fine!")
