# CHAT LOGIC (Replace your existing Chat Logic block from the previous code)
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# AI PROCESSING
if st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner('FocusFlow is thinking...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            models = requests.get(list_url).json()['models']
            model_name = next(m['name'] for m in models if 'generateContent' in m['supportedGenerationMethods'])
            
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
            
            if "cheat sheet" in st.session_state.messages[-1]["content"].lower():
                full_prompt = f"Context: {current_topic}. Provide a high-yield cheat sheet for: {st.session_state.messages[-2]['content']}"
            else:
                full_prompt = f"Context: {current_topic}. User: {st.session_state.messages[-1]['content']}. Be a Socratic coach, ask one diagnostic question first."
            
            payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
            response = requests.post(url, json=payload).json()
            
            # --- THE SAFETY CHECK ---
            if 'candidates' in response and len(response['candidates']) > 0:
                answer = response['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
            else:
                st.error("The AI had a hiccup! Please try rephrasing your question or click the button to try again.")
                # Log the error for you to see what happened
                st.write(response)
