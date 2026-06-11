import streamlit as st
import requests
from datetime import date, datetime, timedelta
import random

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
    .error-box {
        background-color: #FFEBEE;
        border-left: 4px solid #C62828;
        padding: 12px;
        border-radius: 8px;
        color: #C62828;
    }
    .setup-box {
        background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
        border: 2px solid #FF6600;
        padding: 24px;
        border-radius: 16px;
        margin: 20px 0;
    }
    .setup-step {
        background: white;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 3px solid #FF6600;
    }
    .challenge-box {
        background: linear-gradient(135deg, #FFF8E1, #FFECB3);
        border-left: 4px solid #FFC107;
        padding: 16px;
        border-radius: 12px;
        margin: 8px 0;
    }
    .challenge-complete {
        background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
        border-left: 4px solid #4CAF50;
        padding: 16px;
        border-radius: 12px;
        margin: 8px 0;
    }
    .challenge-missed {
        background: linear-gradient(135deg, #FFEBEE, #FFCDD2);
        border-left: 4px solid #C62828;
        padding: 16px;
        border-radius: 12px;
        margin: 8px 0;
    }
    .streak-flame {
        font-size: 24px;
        animation: pulse 1.5s infinite;
    }
    .followup-btn>button {
        background-color: #2196F3 !important;
        color: white !important;
        border-radius: 20px !important;
        font-weight: 600 !important;
        margin-top: 6px !important;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# ============================================================
# DETECT WHICH API KEY IS AVAILABLE
# ============================================================
api_config = None

try:
    key = st.secrets["GROQ_API_KEY"]
    if key and len(key) > 10:
        api_config = {
            "provider": "groq",
            "key": key,
            "model": "llama-3.1-8b-instant",
            "url": "https://api.groq.com/openai/v1/chat/completions"
        }
except:
    pass

if not api_config:
    try:
        key = st.secrets["OPENROUTER_API_KEY"]
        if key and len(key) > 10:
            api_config = {
                "provider": "openrouter",
                "key": key,
                "model": "meta-llama/llama-3.2-3b-instruct:free",
                "url": "https://openrouter.ai/api/v1/chat/completions"
            }
    except:
        pass

if not api_config:
    try:
        key = st.secrets["GOOGLE_API_KEY"]
        if key and len(key) > 10:
            api_config = {
                "provider": "google",
                "key": key,
                "model": "gemini-1.5-pro",
                "url": None
            }
    except:
        pass

if not api_config:
    st.markdown("""
    <div class='setup-box'>
        <h2>🔧 Setup Required</h2>
        <p>Add any ONE of these API keys to your Streamlit secrets:</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Option 1: Groq ⭐ (Recommended)")
    st.markdown("""
    <div class='setup-step'>
        <b>Step 1:</b> Go to <a href='https://console.groq.com/keys' target='_blank'>console.groq.com/keys</a><br>
        <b>Step 2:</b> Sign up with Google/GitHub<br>
        <b>Step 3:</b> Create API Key (starts with <code>gsk_</code>)<br>
        <b>Step 4:</b> Add to Streamlit Secrets:<br>
        <code>GROQ_API_KEY = "gsk_your-key"</code>
    </div>
    """, unsafe_allow_html=True)

    st.error("⛔ No valid API key found.")
    st.stop()

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
    "daily_challenge": None,
    "daily_challenge_date": None,
    "daily_challenge_completed": False,
    "daily_challenge_subject": None,
    "challenge_streak": 0,
    "last_challenge_completed_date": None,
    "challenge_history": [],
    "pending_ai_request": None,
    "awaiting_answer": False,
    "last_socratic_question": None,
    "original_question": None,        # FIX: pin original question
    "last_followup_label": None,       # For dynamic follow-up button
    "last_followup_prompt": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# CORE API CALL HELPER
# ============================================================
def call_api(messages_list, system_prompt):
    """Single function to call whichever API is configured."""
    provider = api_config["provider"]
    model = api_config["model"]

    try:
        if provider == "groq":
            payload = {
                "model": model,
                "messages": [{"role": "system", "content": system_prompt}] + messages_list,
                "temperature": 0.7,
                "max_tokens": 1500
            }
            headers = {
                "Authorization": f"Bearer {api_config['key']}",
                "Content-Type": "application/json"
            }
            response = requests.post(api_config["url"], json=payload, headers=headers, timeout=30).json()
            if 'choices' in response and response['choices']:
                return response['choices'][0]['message']['content']
            else:
                return f"⚠️ Groq Error: {response.get('error', {}).get('message', 'Unknown error')}"

        elif provider == "openrouter":
            payload = {
                "model": model,
                "messages": [{"role": "system", "content": system_prompt}] + messages_list,
                "temperature": 0.7,
                "max_tokens": 1500
            }
            headers = {
                "Authorization": f"Bearer {api_config['key']}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://focusflow.app",
                "X-Title": "FocusFlow"
            }
            response = requests.post(api_config["url"], json=payload, headers=headers, timeout=30).json()
            if 'choices' in response and response['choices']:
                return response['choices'][0]['message']['content']
            else:
                return f"⚠️ OpenRouter Error: {response.get('error', {}).get('message', 'Unknown error')}"

        else:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_config['key']}"
            # Convert to Google format
            google_messages = []
            for m in ([{"role": "system", "content": system_prompt}] + messages_list):
                role = "user" if m["role"] in ("user", "system") else "model"
                google_messages.append({"role": role, "parts": [{"text": m["content"]}]})
            payload = {
                "contents": google_messages,
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1500}
            }
            response = requests.post(url, json=payload, timeout=30).json()
            if 'candidates' in response and response['candidates']:
                return response['candidates'][0]['content']['parts'][0]['text']
            else:
                return f"⚠️ Google Error: {response.get('error', {}).get('message', 'Unknown API error')}"

    except requests.exceptions.RequestException as e:
        return f"🌐 Connection error: {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"


# ============================================================
# GENERATE DAILY CHALLENGE VIA AI
# ============================================================
def generate_daily_challenge(subject, exam_goal):
    system_prompt = f"""You are FocusFlow, an expert tutor for {exam_goal} students.
Generate exactly 5 practice questions for the subject: {subject}.

Rules:
- Questions must be specific to {subject} and relevant for {exam_goal}
- Mix of MCQ and short answer questions
- Each question should be clearly numbered
- MCQ options should be on the same line as the question or clearly indented
- Do NOT include answers
- Keep each question concise

Format EXACTLY like this:
**Today's Challenge: {subject} — 5 Questions**

**Q1.** [Question text here]
A) option  B) option  C) option  D) option

**Q2.** [Question text here]
A) option  B) option  C) option  D) option

**Q3.** [Short answer question]

**Q4.** [Question text here]
A) option  B) option  C) option  D) option

**Q5.** [Short answer question]
"""
    return call_api([{"role": "user", "content": f"Generate 5 {subject} questions for {exam_goal}"}], system_prompt)


# ============================================================
# GENERATE SMART FOLLOW-UP BUTTON LABEL
# ============================================================
def generate_followup(last_ai_reply, subject):
    system_prompt = """You are a smart assistant. Based on the AI tutor's last reply, suggest ONE short follow-up action a student might want to take next.

Reply with ONLY a JSON object like this (no extra text, no markdown):
{"label": "📜 Explore more poems by Robert Frost", "prompt": "List more poems by Robert Frost and briefly describe each one"}

Rules for label:
- Start with a relevant emoji
- Max 6 words
- Should feel natural and helpful
- Examples: "📄 Get full cheat sheet", "🔍 Go deeper into this", "📝 Give me practice questions", "💡 Show a solved example", "🔗 How does this connect to exam?"
"""
    result = call_api(
        [{"role": "user", "content": f"Last AI reply was about: {last_ai_reply[:300]}"}],
        system_prompt
    )
    try:
        import json
        # Clean up in case model adds backticks
        result = result.strip().replace("```json", "").replace("```", "").strip()
        parsed = json.loads(result)
        return parsed.get("label", "🔍 Explore further"), parsed.get("prompt", "Tell me more about this topic")
    except:
        return "🔍 Explore further", "Tell me more about this topic"


# ============================================================
# INTENT DETECTION
# ============================================================
def detect_intent(prompt: str) -> str:
    prompt_lower = prompt.lower().strip()

    direct_signals = [
        "explain", "cheat sheet", "give me", "tell me", "what is",
        "what are", "define", "formula for", "equation for",
        "how does", "how do", "steps to", "method for",
        "list of", "summary of", "overview of", "notes on",
        "derive", "proof", "theorem", "law of", "principle of"
    ]
    if any(signal in prompt_lower for signal in direct_signals):
        return "direct"

    casual_signals = [
        "hi", "hello", "hey", "what's up", "sup", "how are you",
        "bored", "tired", "joke", "fun", "chat", "thanks", "thank you",
        "bye", "goodbye", "see you", "good morning", "good night"
    ]
    if any(signal in prompt_lower for signal in casual_signals) and len(prompt_lower.split()) < 6:
        return "casual"

    struggle_signals = [
        "hate", "difficult", "hard", "don't understand", "confused",
        "stuck", "help me", "panic", "scared", "anxious", "worried",
        "i can't", "i dont get", "no idea", "lost", "frustrated"
    ]
    if any(signal in prompt_lower for signal in struggle_signals):
        return "empathetic"

    return "socratic"


# ============================================================
# MAIN AI RESPONSE — NOW WITH FULL HISTORY + PINNED ORIGINAL Q
# ============================================================
def get_ai_response(prompt: str, msg_type: str, topic_tag: str):
    days_left = (st.session_state.test_date - date.today()).days
    crunch_mode = (days_left <= 3 and st.session_state.has_specific_date)

    # Build conversation history for context
    current_messages = st.session_state.threads[st.session_state.current_thread]
    history = []
    for msg in current_messages:
        if not msg.get("hidden") and msg.get("msg_type") not in ("welcome", "stats", "system_trigger"):
            role = "user" if msg["role"] == "user" else "assistant"
            history.append({"role": role, "content": msg["content"]})
    # Keep last 10 exchanges for context window
    history = history[-10:]

    # Pin original question reminder
    original_q_reminder = ""
    if st.session_state.original_question:
        original_q_reminder = f"\n\nIMPORTANT: The student's ORIGINAL question was: \"{st.session_state.original_question}\". Always keep this in mind. If the conversation drifts, bring it back to this."

    if msg_type == "evaluate_answer":
        system_prompt = f"""You are FocusFlow, a warm and encouraging tutor for {st.session_state.exam_goal} {st.session_state.current_topic}.{original_q_reminder}

The AI previously asked this Socratic question:
"{st.session_state.last_socratic_question}"

The student answered: "{prompt}"

IMPORTANT: The student may have typed just a single option letter like "A", "B", "C", or "D".
Match their answer against the options in the question above and evaluate accordingly.

Your job:
1. If CORRECT: Start with warm praise (e.g. "🎉 That's correct!"), then give the full clear explanation of the concept.
2. If PARTIALLY CORRECT: Acknowledge what they got right, gently correct what's wrong, then explain the full concept.
3. If INCORRECT: Be kind — say something like "Not quite, but great attempt! 💪", correct gently, then explain clearly.

Format your explanation with markdown. Keep it concise but complete.
End with an encouraging line like "You're doing great, keep it up! 🚀"
Do NOT ask another question at the end."""

    elif msg_type == "casual":
        system_prompt = f"""You are FocusFlow, a warm study buddy.{original_q_reminder}
Respond conversationally and warmly. Keep under 3 sentences. Be encouraging."""

    elif msg_type == "empathetic":
        system_prompt = f"""The student is struggling emotionally with studying.{original_q_reminder}
Be deeply empathetic. Acknowledge their feelings. Share ONE motivational tip.
Then gently suggest ONE tiny next step related to {st.session_state.current_topic}.
Be warm, like a caring older sibling."""

    elif msg_type == "direct" or crunch_mode:
        system_prompt = f"""You are an expert {st.session_state.exam_goal} tutor for {st.session_state.current_topic}.{original_q_reminder}
Provide a CLEAR, STRUCTURED explanation.
Format with markdown:
## 📋 [Topic Name]
### 🔑 Core Concept
### 🧮 Key Formula / Steps
### ⚠️ Common Mistake
### 💡 Quick Example"""

    else:
        system_prompt = f"""You are a Socratic tutor for {st.session_state.exam_goal} {st.session_state.current_topic}.{original_q_reminder}

Ask ONE specific diagnostic question to check the student's understanding.
Rules:
- Must relate directly to their question
- Make it multiple choice (A, B, C, D) OR short numerical
- Do NOT give the answer yet
- End with: "Take your time! If you're stuck, click the ⚡ button below 👇"
- Keep under 5 lines total"""

    # Add current prompt to history
    history.append({"role": "user", "content": prompt})
    return call_api(history, system_prompt), msg_type


# ============================================================
# SUBJECT-SPECIFIC WELCOME CONTENT
# ============================================================
SUBJECT_CONTENT = {
    "Physics": {"example_concept": "Explain Newton's Laws of Motion", "example_question": "What is Newton's First Law?"},
    "Chemistry": {"example_concept": "Explain balancing chemical equations", "example_question": "How do I balance chemical equations?"},
    "Maths": {"example_concept": "Explain quadratic equations", "example_question": "How do I solve quadratic equations?"},
    "Biology": {"example_concept": "Explain Photosynthesis", "example_question": "What is photosynthesis?"},
    "English": {"example_concept": "Explain the theme of 'The Road Not Taken'", "example_question": "What is the theme of 'The Road Not Taken'?"},
    "History": {"example_concept": "Explain the causes of World War I", "example_question": "What were the main causes of World War I?"},
    "Other": {"example_concept": "Explain the Pythagorean Theorem", "example_question": "What is the Pythagorean Theorem?"}
}

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
            test_date = st.date_input("Test Date", value=st.session_state.test_date, min_value=date.today())
        else:
            test_date = date.today() + timedelta(days=365)
            st.caption("📌 No countdown. Learning at your own pace!")
    else:
        st.session_state.has_specific_date = True
        test_date = st.date_input("Test Date", value=st.session_state.test_date, min_value=date.today())

    days_left = (test_date - date.today()).days

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
        if current_topic not in st.session_state.threads:
            st.session_state.threads[current_topic] = []
        st.session_state.current_thread = current_topic
        st.toast(f"Switched to {current_topic}!")
        st.rerun()

    st.divider()

    st.markdown("### 🔌 AI Status")
    st.success(f"✅ {api_config['provider'].upper()}")
    st.caption(f"Model: {api_config['model'].split('/')[-1]}")

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

    # ============================================================
    # DAILY CHALLENGE — AUTO GENERATED, AI POWERED
    # ============================================================
    st.markdown("### 🎯 Daily Challenge")

    today = date.today()

    # Reset if new day
    if st.session_state.daily_challenge_date != today:
        st.session_state.daily_challenge = None
        st.session_state.daily_challenge_completed = False
        st.session_state.daily_challenge_subject = None

    # Reset if subject changed
    if st.session_state.daily_challenge_subject and st.session_state.daily_challenge_subject != current_topic:
        st.session_state.daily_challenge = None
        st.session_state.daily_challenge_completed = False
        st.session_state.daily_challenge_subject = None

    # Check missed yesterday
    if st.session_state.daily_challenge_date:
        yesterday = today - timedelta(days=1)
        if st.session_state.daily_challenge_date == yesterday and not st.session_state.daily_challenge_completed:
            st.session_state.challenge_streak = 0

    # Challenge streak badge
    if st.session_state.challenge_streak > 0:
        flame = "🔥" * min(st.session_state.challenge_streak, 5)
        st.markdown(f"<div class='streak-badge'><span class='streak-flame'>{flame}</span> {st.session_state.challenge_streak} day streak!</div>", unsafe_allow_html=True)

    # Auto-generate challenge on app open if not yet generated
    if not st.session_state.daily_challenge and not st.session_state.daily_challenge_completed:
        with st.spinner("📝 Generating today's challenge..."):
            challenge_text = generate_daily_challenge(current_topic, exam_goal)
            st.session_state.daily_challenge = challenge_text
            st.session_state.daily_challenge_date = today
            st.session_state.daily_challenge_subject = current_topic
            st.session_state.daily_challenge_completed = False

    # Display challenge
    if st.session_state.daily_challenge and not st.session_state.daily_challenge_completed:
        st.markdown(f"<div class='challenge-box'>{st.session_state.daily_challenge}</div>", unsafe_allow_html=True)
        if st.button("✅ Mark as Complete", use_container_width=True, type="primary"):
            st.session_state.daily_challenge_completed = True
            st.session_state.last_challenge_completed_date = today
            st.session_state.challenge_streak += 1
            st.session_state.challenge_history.append({
                "date": str(today),
                "subject": current_topic,
                "completed": True
            })
            st.balloons()
            st.toast(f"🎉 Challenge completed! Streak: {st.session_state.challenge_streak}")
            st.rerun()

    elif st.session_state.daily_challenge_completed:
        st.markdown("<div class='challenge-complete'><b>✅ Today's challenge done!</b><br>🎉 Great job! Come back tomorrow for a new one.</div>", unsafe_allow_html=True)

    # Weekly summary
    if st.session_state.challenge_history:
        st.divider()
        st.markdown("### 📊 This Week")
        this_week = [c for c in st.session_state.challenge_history
                     if datetime.strptime(c["date"], "%Y-%m-%d").date() >= today - timedelta(days=7)]
        completed_this_week = sum(1 for c in this_week if c["completed"])
        st.markdown(f"✅ **{completed_this_week}/7** challenges completed this week")

    st.divider()

    if st.button("🗑️ Clear This Chat", use_container_width=True):
        st.session_state.threads[st.session_state.current_thread] = []
        st.session_state.awaiting_answer = False
        st.session_state.last_socratic_question = None
        st.session_state.original_question = None
        st.session_state.last_followup_label = None
        st.session_state.last_followup_prompt = None
        st.rerun()

# ============================================================
# DISPLAY CHAT
# ============================================================
current_messages = st.session_state.threads[st.session_state.current_thread]
days_left = (st.session_state.test_date - date.today()).days

if not current_messages:
    if st.session_state.has_specific_date:
        days_info = f"**{days_left} days** until your {st.session_state.exam_goal} exam!"
    else:
        days_info = "Learning at your own pace — no pressure!"

    subject_data = SUBJECT_CONTENT.get(st.session_state.current_topic, SUBJECT_CONTENT["Other"])

    welcome = f"""👋 Hey! I'm your FocusFlow coach.

**Current Setup:** {st.session_state.exam_goal} | {st.session_state.current_topic} | {days_info}

I can help you:
- 🧠 **Explain concepts** — Just ask "{subject_data['example_concept']}"
- ❓ **Socratic mode** — I'll ask you a question first to check your understanding. Stuck? Click the button!
- 📸 **Solve from images** — Upload a problem photo
- 📝 **Practice questions** — Quick mock tests

**Try asking: "{subject_data['example_question']}"**"""

    current_messages.append({"role": "assistant", "content": welcome, "msg_type": "welcome"})

for i, message in enumerate(current_messages):
    if message.get("hidden"):
        continue
    with st.chat_message(message["role"]):
        msg_type = message.get("msg_type", "default")
        if msg_type == "welcome":
            st.markdown(f"<div class='welcome-box'>{message['content']}</div>", unsafe_allow_html=True)
        elif msg_type == "cheat_sheet":
            st.markdown(f"<div class='cheat-sheet-box'>{message['content']}</div>", unsafe_allow_html=True)
        elif msg_type in ("socratic", "evaluate_answer"):
            st.markdown(f"<div class='socratic-box'>{message['content']}</div>", unsafe_allow_html=True)
        elif msg_type == "stats":
            st.markdown(f"<div class='stats-box'>{message['content']}</div>", unsafe_allow_html=True)
        elif msg_type == "error":
            st.markdown(f"<div class='error-box'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(message["content"])

        if message["role"] == "assistant" and "subject" in message:
            st.markdown(f"<span class='subject-pill'>📚 {message['subject']}</span>", unsafe_allow_html=True)

        # STUCK button for unresolved Socratic questions
        if (message["role"] == "assistant" and
            message.get("msg_type") == "socratic" and
            not message.get("resolved", False)):
            if st.button("⚡ Stuck? Get the cheat sheet", key=f"stuck_btn_{st.session_state.current_thread}_{i}"):
                message["resolved"] = True
                st.session_state.awaiting_answer = False
                st.session_state.last_socratic_question = None

                weak_key = f"{st.session_state.current_topic}: {message.get('topic', 'General')}"
                st.session_state.weak_areas[weak_key] = st.session_state.weak_areas.get(weak_key, 0) + 1

                trigger_prompt = f"[SYSTEM: Student clicked 'Stuck'. Provide direct cheat sheet for: {message.get('topic', 'topic')}]"
                current_messages.append({"role": "user", "content": trigger_prompt, "hidden": True, "msg_type": "system_trigger"})

                with st.chat_message("assistant"):
                    with st.spinner("Generating cheat sheet..."):
                        answer, _ = get_ai_response(trigger_prompt, "direct", message.get("topic", "General"))
                        current_messages.append({
                            "role": "assistant",
                            "content": answer,
                            "msg_type": "cheat_sheet",
                            "topic": message.get("topic", "General"),
                            "subject": st.session_state.current_topic,
                            "resolved": True
                        })
                st.rerun()

        # SMART FOLLOW-UP BUTTON — on last assistant message only
        is_last = (i == len(current_messages) - 1)
        if (message["role"] == "assistant" and
            is_last and
            msg_type not in ("welcome", "socratic", "stats") and
            st.session_state.last_followup_label):
            st.markdown("<div class='followup-btn'>", unsafe_allow_html=True)
            if st.button(st.session_state.last_followup_label, key=f"followup_{i}"):
                followup_prompt = st.session_state.last_followup_prompt
                st.session_state.last_followup_label = None
                st.session_state.last_followup_prompt = None
                current_messages.append({"role": "user", "content": followup_prompt, "msg_type": "user_question"})
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        answer, msg_type_r = get_ai_response(followup_prompt, "direct", followup_prompt[:40])
                        current_messages.append({
                            "role": "assistant",
                            "content": answer,
                            "msg_type": msg_type_r,
                            "subject": st.session_state.current_topic,
                            "resolved": True
                        })
                        # Generate next follow-up label
                        label, prompt_suggestion = generate_followup(answer, st.session_state.current_topic)
                        st.session_state.last_followup_label = label
                        st.session_state.last_followup_prompt = prompt_suggestion
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# IMAGE UPLOAD
# ============================================================
with st.expander("📎 Attach Image (Optional)"):
    uploaded_image = st.file_uploader("Upload problem photo", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        st.image(uploaded_image, caption="Preview", use_column_width=True)

# ============================================================
# PROCESS PENDING AI REQUESTS
# ============================================================
if st.session_state.pending_ai_request:
    request = st.session_state.pending_ai_request
    st.session_state.pending_ai_request = None

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, msg_type = get_ai_response(request["prompt"], request["msg_type"], request["topic"])
            current_messages.append({
                "role": "assistant",
                "content": answer,
                "msg_type": msg_type,
                "topic": request["topic"],
                "subject": st.session_state.current_topic,
                "resolved": True if msg_type != "socratic" else False
            })
            if msg_type == "socratic":
                st.session_state.awaiting_answer = True
                st.session_state.last_socratic_question = answer
            else:
                label, prompt_suggestion = generate_followup(answer, st.session_state.current_topic)
                st.session_state.last_followup_label = label
                st.session_state.last_followup_prompt = prompt_suggestion
    st.rerun()

# ============================================================
# CHAT INPUT
# ============================================================
if prompt := st.chat_input("Ask a question..."):

    today = date.today()
    if st.session_state.last_study_date != today:
        st.session_state.study_streak += 1
        st.session_state.last_study_date = today

    current_messages.append({"role": "user", "content": prompt, "msg_type": "user_question"})

    # Pin original question if this is the first user message in the thread
    user_msgs = [m for m in current_messages if m["role"] == "user" and not m.get("hidden")]
    if len(user_msgs) == 1:
        st.session_state.original_question = prompt

    # Check if awaiting answer to Socratic question
    if st.session_state.awaiting_answer and st.session_state.last_socratic_question:
        intent = "evaluate_answer"
        topic_tag = st.session_state.last_socratic_question[:40]
        st.session_state.awaiting_answer = False
        st.session_state.last_socratic_question = None
        for msg in reversed(current_messages):
            if msg.get("msg_type") == "socratic" and not msg.get("resolved", False):
                msg["resolved"] = True
                break
    else:
        intent = detect_intent(prompt)
        topic_tag = prompt[:40]

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, msg_type = get_ai_response(prompt, intent, topic_tag)

            if msg_type == "socratic":
                st.session_state.awaiting_answer = True
                st.session_state.last_socratic_question = answer
                st.session_state.last_followup_label = None
                st.session_state.last_followup_prompt = None
            else:
                # Generate smart follow-up button label
                label, prompt_suggestion = generate_followup(answer, st.session_state.current_topic)
                st.session_state.last_followup_label = label
                st.session_state.last_followup_prompt = prompt_suggestion

            current_messages.append({
                "role": "assistant",
                "content": answer,
                "msg_type": "evaluate_answer" if intent == "evaluate_answer" else msg_type,
                "topic": topic_tag,
                "subject": st.session_state.current_topic,
                "resolved": True
            })
    st.rerun()

# ============================================================
# QUICK ACTION BUTTONS
# ============================================================
st.divider()
qa_col1, qa_col2, qa_col3, qa_col4 = st.columns(4)

with qa_col1:
    if st.button("📄 Cheat Sheet", use_container_width=True):
        cheat_prompt = f"Give me a comprehensive cheat sheet for {st.session_state.current_topic} ({st.session_state.exam_goal})"
        current_messages.append({"role": "user", "content": cheat_prompt, "msg_type": "user_question"})
        st.session_state.pending_ai_request = {
            "prompt": cheat_prompt, "msg_type": "direct",
            "topic": f"{st.session_state.current_topic} Cheat Sheet", "has_image": False
        }
        st.rerun()

with qa_col2:
    if st.button("📝 Mock Test", use_container_width=True):
        mock_prompt = f"Generate 5 practice questions for {st.session_state.current_topic} ({st.session_state.exam_goal}) with answers and explanations"
        current_messages.append({"role": "user", "content": mock_prompt, "msg_type": "user_question"})
        st.session_state.pending_ai_request = {
            "prompt": mock_prompt, "msg_type": "direct",
            "topic": f"{st.session_state.current_topic} Mock Test", "has_image": False
        }
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
        current_messages.append({"role": "assistant", "content": stats_msg, "msg_type": "stats", "subject": "System"})
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
            "📥 Download Chat", export_text,
            file_name=f"focusflow_{st.session_state.current_thread}_{date.today()}.txt",
            mime="text/plain", use_container_width=True
        )
