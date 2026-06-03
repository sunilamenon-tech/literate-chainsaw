with st.chat_message("assistant"):
        with st.spinner('FocusFlow is thinking...'):
            # This logic finds the first working model automatically
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model_name = models[0] if models else 'gemini-1.0-pro'
            
            model = genai.GenerativeModel(model_name)
            context = f"Goal: {exam_goal}. Test Date: {test_date}. Subject: {current_topic}."
            full_prompt = f"You are FocusFlow, a best-friend coach. Context: {context}. User asks: {prompt}. Provide mnemonics or cheat sheets if needed."
            
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
