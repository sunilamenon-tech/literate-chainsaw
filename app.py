import streamlit as st
import requests
from datetime import date, datetime, timedelta
import base64

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="centered")

st.markdown("""
<style>
    .stApp {background-color: #FFF9E6;}
    .stButton>button {background-color: #FF6600; color: white; border-radius: 20px; font-weight: 600;}
    .stChatMessage {border-radius: 15px;}
    .cheat-sheet-box {
        background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
        border-left: 4px solid #FF6600;
        padding: 16px;
        border-radius: 12px;
        margin: 8px 0;
    }
    .socratic-box {
        background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
        border-left: 4px solid #4CAF50;
        padding: 16px;
        border-radius: 12px;
        margin: 8px 0;
    }
    .welcome-box {
        background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
        border-left: 4px solid #2196F3;
        padding: 16px;
        border-radius: 12px;
        margin: 8px 0;
    }
    .stats-box {
        background: linear-gradient(135deg, #F3E5F5, #E1BEE7);
        border-left: 4px solid #9C27B0;
        padding: 16px;
        border-radius: 12px;
        margin: 8px 0;
    }
    .streak-badge {
        background: linear-gradient(45deg, #FF6600, #FF9900);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        text-align: center;
        font-weight: bold;
        margin: 8px 0;
    }
    .weak-area-tag {
        display: inline-block;
        background-color: #FFEBEE;
        color: #C62828;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        margin: 2px;
    }
    .subject-pill {
        display: inline-block;
        background-color: #FFE4CC;
        color: #FF6600;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 11px;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "messages": [],
    "threads": {"General": []},
    "current_thread": "General",
    "exam_goal": "JEE Main",
    "current_topic": "Physics",
    "test_date": date.today() + timedelta(days=90),
    "has_specific_date": True,
    "study_streak": 0,
    "last_study_date": None,
    "weak_areas": {},
    "total_study_minutes": 0,
    "pomodoro_active": False,
    "pomodoro_end": None,
    "daily_challenge": None,
    "last_challenge_date": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### 🎯 Your Goal")
    
    exam_goal = st.selectbox(
        "Exam/Goal",
        ["JEE Main", "NEET", "10th Boards", "12th Boards", "UPSC", "Other"],
        index=["JEE Main", "NEET", "10th Boards", "12th Boards", "UPSC", "Other"].index(st.session_state.exam_goal)
    )
    
    current_topic = st.selectbox(
        "Subject",
        ["Physics", "Chemistry", "Maths", "Biology", "English", "History", "Other"],
        index=["Physics", "Chemistry", "Maths", "Biology", "English", "History", "Other"].index(st.session_state.current_topic)
    )
    
    # Date section - always visible but flexible for "Other"
    if exam_goal == "Other":
        st.markdown("**Do you have a specific exam date?**")
        has_date = st.radio(
            "Choose one:",
            ["Yes, I have a test date", "No, just learning"],
            index=0 if st.session_state.has_specific_date else 1,
            label_visibility="collapsed"
        )
        st.session_state.has_specific_date = (has_date == "Yes, I have a test date")
        
        if st.session_state.has_specific_date:
            test_date = st.date_input(
                "Test Date",
                value=st.session_state.test_date,
                min_value=date.today()
            )
        else:
            test_date = date.today() + timedelta(days=365)  # Far future, no urgency
            st.caption("📌 No countdown shown. Learning at your own pace!")
    else:
        st.session_state.has_specific_date = True
        test_date = st.date_input(
            "Test Date",
            value=st.session_state.test_date,
            min_value=date.today()
        )
    
    days_left = (test_date - date.today()).days
    
    # Urgency indicator (only if has specific date)
    if st.session_state.has_specific_date:
        if days_left <= 3:
            st.error(f"🚨 {days_left} days left! CRUNCH MODE")
        elif days_left <= 14:
            st.warning(f"⏰ {days_left} days left")
        else:
            st.info(f"📅 {days_left} days left")
    
    if st.button("🔄 Update Context", use_container_width=True):
        st.session_state.exam_goal = exam_goal
        st.session_state.current_topic = current_topic
        st.session_state.test_date = test_date
        
        # Create thread for this subject if not exists
        if current_topic not in st.session_state.threads:
            st.session_state.threads[current_topic] = []
        
        # Switch to subject thread
        st.session_state.current_thread = current_topic
        st.toast(f"Switched to {current_topic}!")
        st.rerun()
    
    st.divider()
    
    # Study Streak
    st.markdown("### 🔥 Study Streak")
    today = date.today()
    if st.session_state.last_study_date == today - timedelta(days=1):
        st.session_state.study_streak += 1
        st.session_state.last_study_date = today
    elif st.session_state.last_study_date != today:
        st.session_state.study_streak = 1
        st.session_state.last_study_date = today
    
    st.markdown(f"<div class='streak-badge'>🔥 {st.session_state.study_streak} day streak</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Weak Areas
    st.markdown("### ⚠️ Focus Areas")
    if st.session_state.weak_areas:
        sorted_weak = sorted(st.session_state.weak_areas.items(), key=lambda x: x[1], reverse=True)[:5]
        for topic, count in sorted_weak:
            st.markdown(f"<span class='weak-area-tag'>{topic} ({count})</span>", unsafe_allow_html=True)
    else:
        st.caption("Keep studying to see your focus areas!")
    
    st.divider()
    
    # Thread Switcher
    st.markdown("### 💬 Chat Threads")
    for thread_name in list(st.session_state.threads.keys()):
        cols = st.columns([4, 1])
        with cols[0]:
            active = "✅ " if thread_name == st.session_state.current_thread else ""
            if st.button(f"{active}📁 {thread_name}", key=f"thread_{thread_name}", use_container_width=True):
                st.session_state.current_thread = thread_name
                st.rerun()
        with cols[1]:
            if thread_name != "General" and st.button("🗑️", key=f"del_{thread_name}"):
                del st.session_state.threads[thread_name]
                st.session_state.current_thread = "General"
                st.rerun()
    
    st.divider()
    
    # Pomodoro Timer
    st.markdown("### ⏱️ Focus Timer")
    pomo_cols = st.columns(2)
    with pomo_cols[0]:
        if st.button("▶️ 25m", use_container_width=True):
            st.session_state.pomodoro_active = True
            st.session_state.pomodoro_end = datetime.now() + timedelta(minutes=25)
    with pomo_cols[1]:
        if st.button("⏹️ Stop", use_container_width=True):
            st.session_state.pomodoro_active = False
            st.session_state.pomodoro_end = None
    
    if st.session_state.pomodoro_active and st.session_state.pomodoro_end:
        remaining = st.session_state.pomodoro_end - datetime.now()
        if remaining.total_seconds() > 0:
            mins, secs = divmod(int(remaining.total_seconds()), 60)
            st.markdown(f"<h3 style='text-align: center; color: #FF6600;'>{mins:02d}:{secs:02d}</h3>", unsafe_allow_html=True)
        else:
            st.session_state.pomodoro_active = False
            st.session_state.total_study_minutes += 25
            st.balloons()
            st.success("🎉 25 min done! Take a 5 min break.")
    
    st.divider()
    
    # Daily Challenge
    st.markdown("### 🎯 Daily Challenge")
    if st.session_state.last_challenge_date != today:
        st.session_state.daily_challenge = None
    
    if st.session_state.daily_challenge:
        st.info(st.session_state.daily_challenge)
    else:
        if st.button("Generate Challenge", use_container_width=True):
            st.session_state.daily_challenge = f"Solve 5 questions from {st.session_state.current_topic} ({st.session_state.exam_goal})"
            st.session_state.last_challenge_date = today
            st.rerun()
    
    st.divider()
    
    # Clear current thread
    if st.button("🗑️ Clear This Chat", use_container_width=True):
        st.session_state.threads[st.session_state.current_thread] = []
        st.rerun()

# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(prompt: str) -> str:
    prompt_lower = prompt.lower().strip()
    
    # DIRECT: Explicit requests for explanation, formula, cheat sheet
    direct_signals = [
        "explain", "cheat sheet", "give me", "tell me", "what is",
        "what are", "define", "formula for", "equation for",
        "how does", "how do", "steps to", "method for",
        "list of", "summary of", "overview of", "notes on",
        "derive", "proof", "theorem", "law of", "principle of"
    ]
    if any(signal in prompt_lower for signal in direct_signals):
        return "direct"
    
    # CASUAL: Social chat, not studying
    casual_signals = [
        "hi", "hello", "hey", "what's up", "sup", "how are you",
        "bored", "tired", "joke", "fun", "chat", "thanks", "thank you",
        "bye", "goodbye", "see you", "good morning", "good night"
    ]
    if any(signal in prompt_lower for signal in casual_signals) and len(prompt_lower.split()) < 6:
        return "casual"
    
    # EMOTIONAL: Struggling, anxious
    struggle_signals = [
        "hate", "difficult", "hard", "don't understand", "confused",
        "stuck", "help me", "panic", "scared", "anxious", "worried",
        "i can't", "i dont get", "no idea", "lost", "frustrated"
    ]
    if any(signal in prompt_lower for signal in struggle_signals):
        return "empathetic"
    
    # Default: Socratic questioning
    return "socratic"

# ============================================================
# DISPLAY CHAT
# ============================================================

current_messages = st.session_state.threads[st.session_state.current_thread]

# Welcome message if thread is empty
if not current_messages:
    if st.session_state.has_specific_date:
        days_info = f"**{days_left} days** until your {st.session_state.exam_goal} exam!"
    else:
        days_info = "Learning at your own pace — no pressure!"
    
    welcome = f"""👋 Hey! I'm your FocusFlow coach.

**Current Setup:** {st.session_state.exam_goal} | {st.session_state.current_topic} | {days_info}

I can help you:
- 🧠 **Explain concepts** — Just ask "Explain Photosynthesis"
- ❓ **Socratic mode** — I'll ask you a question first to check your understanding. Stuck? Click the button!
- 📸 **Solve from images** — Upload a problem photo
- 📝 **Practice questions** — Quick mock tests

**Try asking: "What is Newton's First Law?"**"""
    
    current_messages.append({
        "role": "assistant",
        "content": welcome,
        "msg_type": "welcome"
    })

# Render messages
for i, message in enumerate(current_messages):
    with st.chat_message(message["role"]):
        
        # Style based on message type
        msg_type = message.get("msg_type", "default")
        if msg_type == "welcome":
            st.markdown(f"<div class='welcome-box'>{message['content']}</div>", unsafe_allow_html=True)
        elif msg_type == "cheat_sheet":
            st.markdown(f"<div class='cheat-sheet-box'>{message['content']}</div>", unsafe_allow_html=True)
        elif msg_type == "socratic":
            st.markdown(f"<div class='socratic-box'>{message['content']}</div>", unsafe_allow_html=True)
        elif msg_type == "stats":
            st.markdown(f"<div class='stats-box'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(message["content"])
        
        # Show subject tag for assistant messages
        if message["role"] == "assistant" and "subject" in message:
            st.markdown(f"<span class='subject-pill'>📚 {message['subject']}</span>", unsafe_allow_html=True)
        
        # THE "STUCK?" BUTTON — Only for active Socratic questions
        if (message["role"] == "assistant" and
            message.get("msg_type") == "socratic" and
            not message.get("resolved", False)):
            
            if st.button("⚡ Stuck? Get the cheat sheet", key=f"stuck_btn_{st.session_state.current_thread}_{i}"):
                # Mark resolved
                message["resolved"] = True
                
                # Track weak area
                weak_key = f"{st.session_state.current_topic}: {message.get('topic', 'General')}"
                st.session_state.weak_areas[weak_key] = st.session_state.weak_areas.get(weak_key, 0) + 1
                
                # Inject system trigger for direct answer
                current_messages.append({
                    "role": "user",
                    "content": f"[SYSTEM: Student clicked 'Stuck' on Socratic question about: {message.get('topic', 'topic')}. Provide direct, structured cheat sheet with: 1) Core concept 2) Key formula/steps 3) Common mistake 4) Quick example. Be concise.]",
                    "hidden": True,
                    "msg_type": "system_trigger"
                })
                st.rerun()

# ============================================================
# IMAGE UPLOAD
# ============================================================
with st.expander("📎 Attach Image (Optional)"):
    uploaded_image = st.file_uploader("Upload problem photo", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        st.image(uploaded_image, caption="Preview", use_column_width=True)

# ============================================================
# CHAT INPUT & PROCESSING
# ============================================================

if prompt := st.chat_input("Ask a question..."):
    
    # Track study activity
    today = date.today()
    if st.session_state.last_study_date != today:
        st.session_state.study_streak += 1
        st.session_state.last_study_date = today
    
    # Add user message
    current_messages.append({
        "role": "user",
        "content": prompt,
        "msg_type": "user_question"
    })
    
    # Detect intent
    intent = detect_intent(prompt)
    
    # Determine response strategy
    days_left = (st.session_state.test_date - date.today()).days
    crunch_mode = (days_left <= 3 and st.session_state.has_specific_date)
    
    if intent == "casual":
        system_prompt = f"""You are FocusFlow, a warm study buddy. The student said: "{prompt}"
Respond conversationally and warmly. If it's a greeting, greet back and briefly mention you're ready to help with {st.session_state.current_topic}.
Keep under 3 sentences. Be encouraging. No study pressure right now."""
        msg_type = "casual"
        topic_tag = None
        
    elif intent == "empathetic":
        system_prompt = f"""The student is struggling emotionally with studying. They said: "{prompt}"
Be deeply empathetic. Acknowledge their feelings genuinely. Share ONE quick motivational tip or breathing technique.
Then gently suggest ONE tiny, manageable next step related to {st.session_state.current_topic}.
Keep it warm, not robotic. Like a caring older sibling, not a teacher."""
        msg_type = "empathetic"
        topic_tag = None
        
    elif intent == "direct" or crunch_mode:
        system_prompt = f"""You are an expert {st.session_state.exam_goal} tutor. The student asked: "{prompt}"
Provide a CLEAR, STRUCTURED cheat sheet / explanation.
Format with markdown:
## 📋 [Topic Name]
### 🔑 Core Concept
(2-3 sentences)
### 🧮 Key Formula / Steps
- Point 1
- Point 2
### ⚠️ Common Mistake
(What students usually get wrong)
### 💡 Quick Example
(One solved example)
Context: {st.session_state.exam_goal}, Subject: {st.session_state.current_topic}"""
        msg_type = "cheat_sheet"
        topic_tag = prompt[:40]
        
    else:
        # SOCRATIC MODE
        system_prompt = f"""You are a Socratic tutor for {st.session_state.exam_goal} {st.session_state.current_topic}.
The student asked: "{prompt}"

Your job: Ask ONE specific diagnostic question to check their understanding.
Rules:
- Must relate directly to their question
- Make it multiple choice (A, B, C, D) OR a short numerical answer
- Do NOT give the answer or explanation yet
- End with: "Take your time! If you're stuck, click the ⚡ button below 👇"
- Keep under 5 lines total

Example:
"Quick check before I explain: In which organelle does photosynthesis occur?
A) Mitochondria  B) Chloroplast  C) Nucleus  D) Ribosome

Take your time! If you're stuck, click the ⚡ button below 👇"
"""
        msg_type = "socratic"
        topic_tag = prompt[:40]
    
    # API CALL
    with st.chat_message("assistant"):
        with st.spinner('Thinking...'):
            try:
                api_key = st.secrets["GOOGLE_API_KEY"]
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                # Build content parts
                content_parts = [{"text": system_prompt}]
                
                # Add image if uploaded
                if uploaded_image:
                    image_bytes = uploaded_image.getvalue()
                    image_b64 = base64.b64encode(image_bytes).decode()
                    content_parts.append({
                        "inline_data": {
                            "mime_type": uploaded_image.type,
                            "data": image_b64
                        }
                    })
                
                payload = {
                    "contents": [{"parts": content_parts}],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 1000
                    }
                }
                
                response = requests.post(url, json=payload, timeout=30).json()
                
                if 'candidates' in response and response['candidates']:
                    answer = response['candidates'][0]['content']['parts'][0]['text']
                    
                    current_messages.append({
                        "role": "assistant",
                        "content": answer,
                        "msg_type": msg_type,
                        "topic": topic_tag,
                        "subject": st.session_state.current_topic,
                        "resolved": False,
                        "timestamp": datetime.now().isoformat()
                    })
                    st.rerun()
                else:
                    error = response.get('error', {}).get('message', 'Unknown API error')
                    st.error(f"⚠️ AI Error: {error}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"🌐 Connection error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Something went wrong: {str(e)}")

# ============================================================
# QUICK ACTION BUTTONS
# ============================================================
st.divider()
qa_col1, qa_col2, qa_col3, qa_col4 = st.columns(4)

with qa_col1:
    if st.button("📄 Cheat Sheet", use_container_width=True):
        current_messages.append({
            "role": "user",
            "content": f"Give me a comprehensive cheat sheet for {st.session_state.current_topic} ({st.session_state.exam_goal})",
            "msg_type": "user_question"
        })
        st.rerun()

with qa_col2:
    if st.button("📝 Mock Test", use_container_width=True):
        current_messages.append({
            "role": "user",
            "content": f"Generate 5 practice questions for {st.session_state.current_topic} with answers and explanations",
            "msg_type": "user_question"
        })
        st.rerun()

with qa_col3:
    if st.button("📊 My Stats", use_container_width=True):
        total_msgs = sum(len(msgs) for msgs in st.session_state.threads.values())
        weak_topics = list(st.session_state.weak_areas.keys())[:3]
        focus_time = st.session_state.total_study_minutes
        
        stats_msg = f"""📊 Your FocusFlow Stats

🔥 **Study Streak:** {st.session_state.study_streak} days
⏱️ **Focus Time:** {focus_time} minutes ({focus_time // 60}h {focus_time % 60}m)
💬 **Total Messages:** {total_msgs}
⚠️ **Focus Areas:** {', '.join(weak_topics) if weak_topics else 'None yet — keep going!'}

Keep crushing it! 🚀"""
        
        current_messages.append({
            "role": "assistant",
            "content": stats_msg,
            "msg_type": "stats",
            "subject": "System"
        })
        st.rerun()

with qa_col4:
    if st.button("💾 Export", use_container_width=True):
        chat_text = []
        for msg in current_messages:
            if not msg.get("hidden"):
                prefix = "🧑‍🎓 You" if msg["role"] == "user" else "🤖 FocusFlow"
                chat_text.append(f"{prefix}:\n{msg['content']}")
        
        export_text = f"FocusFlow Chat Export\n{'='*50}\nExam: {st.session_state.exam_goal}\nSubject: {st.session_state.current_topic}\nDate: {date.today()}\n{'='*50}\n\n" + "\n\n---\n\n".join(chat_text)
        
        st.download_button(
            "📥 Download Chat",
            export_text,
            file_name=f"focusflow_{st.session_state.current_thread}_{date.today()}.txt",
            mime="text/plain",
            use_container_width=True
        )
