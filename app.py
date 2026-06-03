with st.chat_message("assistant"):
        with st.spinner('FocusFlow is thinking...'):
            # The prompt is now much stricter about NOT giving the answer early
            context = f"Goal: {exam_goal}. Test Date: {test_date}. Subject: {current_topic}."
            full_prompt = f"""
            You are a Socratic Study Coach. 
            Context: {context}. 
            User asks: {prompt}.
            
            Task:
            1. DO NOT give the cheat sheet yet.
            2. Ask one challenging diagnostic question to check their understanding.
            3. Tell the user: "Answer this, and then I'll reveal the cheat sheet!"
            4. Keep the tone warm and best-friend like.
            """
            
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
