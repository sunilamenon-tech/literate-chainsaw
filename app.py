import streamlit as st
import requests
from datetime import date

st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="wide")
st.markdown("""<style>.stApp {background-color: #FFF9E6;} .stButton>button {background-color: #FF6600; color: white;}</style>""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# SIDEBAR: Context, Sync & Tension Meter
with st.sidebar:
    st.header("🎯 Your Study Context")
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "JEE Advanced", "NEET", "10th Boards", "12th Boards", "Other"])
    current_topic = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English", "Other"])
    
    # NEW LOGIC: Only show date if NOT "Other"
    test_date = None
    if exam_goal != "Other":
        test_date = st.date_input("When is your test?", min_value=date.today())
    
    if st.button("Sync My Goal"):
        st.session_state.messages = [{"role": "assistant", "content": f"Context updated for {exam_goal}. Let's master {current_topic}!"}]
        st.rerun()
    
    # Only show status if a test date exists
    if test_date:
        days_left = (test_date - date.today()).days
        tension = "High 🚨" if days_left < 7 else ("Medium ⚠️" if days_left < 20 else "Low 😌")
        st.markdown("---")
        st.markdown(f"### 📊 Your Status \n- **Tension:** {tension} \n- **Days Left:** {days_left}")

# 2. CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Set your goal and ask me anything!"}]

# 3. DISPLAY CHAT & BUTTONS
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Only show button if AI asked a question (Diagnostic Mode)
        if message["role"] == "assistant" and i > 0 and "?" in message["content"] and "cheat sheet" not in message["content"].lower():
            if st.button("⚡ Stuck? Get a hint/cheat sheet", key=f"btn_{i}"):
                # We save a special trigger in session state
                st.session_state.trigger_cheat_sheet = True
                st.rerun()

# 4. CHAT INPUT
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# 5. AI PROCESSING
if (st.session_state.messages and st.session_state.messages[-1]["role"] == "user") or st.session_state.get("trigger_cheat_sheet"):
    with st.chat_message("assistant"):
        with st.spinner('Thinking...'):
            api_key = st.secrets["GOOGLE_API_KEY"]
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            models_data = requests.get(list_url).json()
            model_name = next(m['name'] for m in models_data['models'] if 'generateContent' in m['supportedGenerationMethods'])
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
            
            # Use trigger if button was clicked
            if st.session_state.get("trigger_cheat_sheet"):
                prompt_text = f"Context: {current_topic}. Provide a concise high-yield cheat sheet for: {st.session_state.messages[-2]['content']}. Be direct."
                st.session_state.trigger_cheat_sheet = False # Reset trigger
            else:
                prompt_text = f"Context: {exam_goal}, {current_topic}. User: {st.session_state.messages[-1]['content']}. Rules: Act as Socratic Coach. Ask ONE diagnostic question."
            
            response = requests.post(url, json={"contents": [{"parts": [{"text": prompt_text}]}]}).json()
            
            if 'candidates' in response:
                answer = response['candidates'][0]['content']['parts'][0]['text']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()
