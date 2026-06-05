# AI PROCESSING (CHAT)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        with st.spinner('FocusFlow is thinking...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            models = requests.get(list_url).json()['models']
            model_name = next(m['name'] for m in models if 'generateContent' in m['supportedGenerationMethods'])
            
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
            
            # --- INTENT-AWARE LOGIC ---
            user_text = st.session_state.messages[-1]["content"].lower()
            
            # If user asks to skip, stop, or give answer, go direct.
            if any(word in user_text for word in ["stop asking", "just explain", "give me the answer", "help me with", "skip"]):
                full_prompt = f"Context: {current_topic}. User: {st.session_state.messages[-1]['content']}. Be a helpful, direct tutor. Provide a clear explanation and cheat sheet. Do not ask questions."
            # If it's a request for a cheat sheet
            elif "cheat sheet" in user_text:
                full_prompt = f"Context: {current_topic}. Provide a high-yield cheat sheet for: {st.session_state.messages[-2]['content']}"
            # Default: Act like a Socratic Coach
            else:
                full_prompt = f"Context: {current_topic}. User: {st.session_state.messages[-1]['content']}. Be a Socratic coach, ask ONE diagnostic question first to check understanding."
            
            payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
            response = requests.post(url, json=payload).json()
            answer = response['candidates'][0]['content']['parts'][0]['text']
            
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
