import streamlit as st
import requests
from datetime import date, datetime, timedelta
import random
import json

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="FocusFlow", page_icon="⚡", layout="centered")

st.markdown("""
<style>
    .stApp {background-color: #FFF9E6;}
    .stButton>button {background-color: #FF6600; color: white; border-radius: 20px; font-weight: 600;}
    .stChatMessage {border-radius: 15px;}
    * { font-family: 'Inter', system-ui, -apple-system, sans-serif !important; }
    .cheat-sheet-box {
        background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
        border-left: 4px solid #FF6600;
        padding: 16px; border-radius: 12px; margin: 8px 0;
    }
    .socratic-box {
        background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
        border-left: 4px solid #4CAF50;
        padding: 16px; border-radius: 12px; margin: 8px 0;
    }
    .welcome-box {
        background: linear-gradient(135deg, #E3F2FD, #BBDEFB);
        border-left: 4px solid #2196F3;
        padding: 16px; border-radius: 12px; margin: 8px 0;
    }
    .stats-box {
        background: linear-gradient(135deg, #F3E5F5, #E1BEE7);
        border-left: 4px solid #9C27B0;
        padding: 16px; border-radius: 12px; margin: 8px 0;
    }
    .evaluate-correct-box {
        background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
        border-left: 4px solid #4CAF50;
        padding: 16px; border-radius: 12px; margin: 8px 0;
    }
    .evaluate-wrong-box {
        background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
        border-left: 4px solid #FF9800;
        padding: 16px; border-radius: 12px; margin: 8px 0;
    }
    .streak-badge {
        background: linear-gradient(45deg, #FF6600, #FF9900);
        color: white; padding: 8px 16px; border-radius: 20px;
        text-align: center; font-weight: bold; margin: 8px 0;
    }
    .weak-area-tag {
        display: inline-block; background-color: #FFEBEE;
        color: #C62828; padding: 4px 10px; border-radius: 12px;
        font-size: 12px; margin: 2px;
    }
    .subject-pill {
        display: inline-block; background-color: #FFE4CC;
        color: #FF6600; padding: 4px 12px; border-radius: 12px;
        font-size: 11px; margin-top: 4px;
    }
    .error-box {
        background-color: #FFEBEE; border-left: 4px solid #C62828;
        padding: 12px; border-radius: 8px; color: #C62828;
    }
    .setup-box {
        background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
        border: 2px solid #FF6600; padding: 24px;
        border-radius: 16px; margin: 20px 0;
    }
    .setup-step {
        background: white; padding: 12px 16px; border-radius: 8px;
        margin: 8px 0; border-left: 3px solid #FF6600;
    }
    .challenge-box {
        background: linear-gradient(135deg, #FFF8E1, #FFECB3);
        border-left: 4px solid #FFC107;
        padding: 16px; border-radius: 12px; margin: 8px 0;
    }
    .challenge-complete {
        background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
        border-left: 4px solid #4CAF50;
        padding: 16px; border-radius: 12px; margin: 8px 0;
    }
    .clap-banner {
        background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
        border: 2px solid #4CAF50; border-radius: 12px;
        padding: 12px 16px; text-align: center;
        font-size: 18px; font-weight: 700; color: #2E7D32;
        margin: 8px 0;
        animation: popIn 0.4s ease-out;
    }
    @keyframes popIn {
        0% { transform: scale(0.8); opacity: 0; }
        70% { transform: scale(1.05); }
        100% { transform: scale(1); opacity: 1; }
    }
    .followup-btn button {
        background: transparent !important;
        border: 1.5px solid #2196F3 !important;
        color: #2196F3 !important;
        border-radius: 20px !important;
        font-size: 12px !important;
        padding: 4px 14px !important;
        margin-top: 6px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ FocusFlow")

# ============================================================
# CLAP SOUND
# ============================================================
CLAP_JS = """
<script>
(function() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        function clap(t) {
            const buf = ctx.createBuffer(1, ctx.sampleRate * 0.15, ctx.sampleRate);
            const d = buf.getChannelData(0);
            for (let i = 0; i < d.length; i++) {
                d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / d.length, 3);
            }
            const src = ctx.createBufferSource();
            src.buffer = buf;
            const gain = ctx.createGain();
            gain.gain.setValueAtTime(0.6, ctx.currentTime + t);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + t + 0.15);
            src.connect(gain);
            gain.connect(ctx.destination);
            src.start(ctx.currentTime + t);
        }
        clap(0); clap(0.2); clap(0.4); clap(0.6); clap(0.8);
    } catch(e) {}
})();
</script>
"""

def show_clap_celebration():
    st.markdown(
        "<div class='clap-banner'>👏 👏 👏 &nbsp; Well done! That's correct! &nbsp; 👏 👏 👏</div>" + CLAP_JS,
        unsafe_allow_html=True
    )

# ============================================================
# API KEY DETECTION
# ============================================================
api_config = None

try:
    key = st.secrets["GROQ_API_KEY"]
    if key and len(key) > 10:
        api_config = {"provider": "groq", "key": key, "model": "llama-3.1-8b-instant", "url": "https://api.groq.com/openai/v1/chat/completions"}
except: pass

if not api_config:
    try:
        key = st.secrets["OPENROUTER_API_KEY"]
        if key and len(key) > 10:
            api_config = {"provider": "openrouter", "key": key, "model": "meta-llama/llama-3.2-3b-instruct:free", "url": "https://openrouter.ai/api/v1/chat/completions"}
    except: pass

if not api_config:
    try:
        key = st.secrets["GOOGLE_API_KEY"]
        if key and len(key) > 10:
            api_config = {"provider": "google", "key": key, "model": "gemini-1.5-pro", "url": None}
    except: pass

if not api_config:
    st.markdown("<div class='setup-box'><h2>🔧 Setup Required</h2><p>Add any ONE API key to Streamlit secrets.</p></div>", unsafe_allow_html=True)
    st.markdown("<div class='setup-step'><b>Groq (Free):</b> <a href='https://console.groq.com/keys' target='_blank'>console.groq.com/keys</a><br>Add: <code>GROQ_API_KEY = \"gsk_your-key\"</code></div>", unsafe_allow_html=True)
    st.error("⛔ No valid API key found.")
    st.stop()

# ============================================================
# SESSION STATE
# ============================================================
defaults = {
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
    "original_question": None,
    "last_followup_label": None,
    "last_followup_prompt": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# CORE API CALL
# ============================================================
def call_api(messages_list, system_prompt):
    provider = api_config["provider"]
    model = api_config["model"]
    try:
        if provider == "groq":
            msgs = [{"role": "system", "content": system_prompt}] + messages_list
            payload = {"model": model, "messages": msgs, "temperature": 0.7, "max_tokens": 1500}
            headers = {"Authorization": f"Bearer {api_config['key']}", "Content-Type": "application/json"}
            r = requests.post(api_config["url"], json=payload, headers=headers, timeout=30).json()
            if 'choices' in r and r['choices']:
                return r['choices'][0]['message']['content']
            return f"⚠️ Error: {r.get('error', {}).get('message', 'Unknown')}"

        elif provider == "openrouter":
            msgs = [{"role": "system", "content": system_prompt}] + messages_list
            payload = {"model": model, "messages": msgs, "temperature": 0.7, "max_tokens": 1500}
            headers = {"Authorization": f"Bearer {api_config['key']}", "Content-Type": "application/json",
                       "HTTP-Referer": "https://focusflow.app", "X-Title": "FocusFlow"}
            r = requests.post(api_config["url"], json=payload, headers=headers, timeout=30).json()
            if 'choices' in r and r['choices']:
                return r['choices'][0]['message']['content']
            return f"⚠️ Error: {r.get('error', {}).get('message', 'Unknown')}"

        else:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_config['key']}"
            google_msgs = []
            all_msgs = [{"role": "system", "content": system_prompt}] + messages_list
            for m in all_msgs:
                role = "user" if m["role"] in ("user", "system") else "model"
                google_msgs.append({"role": role, "parts": [{"text": m["content"]}]})
            payload = {"contents": google_msgs, "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1500}}
            r = requests.post(url, json=payload, timeout=30).json()
            if 'candidates' in r and r['candidates']:
                return r['candidates'][0]['content']['parts'][0]['text']
            return f"⚠️ Error: {r.get('error', {}).get('message', 'Unknown')}"

    except Exception as e:
        return f"❌ Error: {str(e)}"

# ============================================================
# GENERATE DAILY CHALLENGE
# ============================================================
def generate_daily_challenge(subject, exam_goal):
    system_prompt = f"""You are FocusFlow, an expert tutor for {exam_goal} students.
Generate exactly 5 practice questions for the subject: {subject}.
Rules:
- Specific to {subject}, relevant for {exam_goal}
- Mix of MCQ and short answer
- Clearly numbered, no answers included

Format EXACTLY like this:
**🎯 Today's Challenge: {subject} — 5 Questions**

**Q1.** [Question]
A) option  B) option  C) option  D) option

**Q2.** [Question]
A) option  B) option  C) option  D) option

**Q3.** [Short answer question]

**Q4.** [Question]
A) option  B) option  C) option  D) option

**Q5.** [Short answer question]
"""
    return call_api([{"role": "user", "content": f"Generate 5 {subject} questions for {exam_goal}"}], system_prompt)

# ============================================================
# GENERATE SMART FOLLOW-UP
# ============================================================
def generate_followup(last_ai_reply, subject):
    system_prompt = """Based on the AI tutor's last reply, suggest ONE short follow-up action.
Reply with ONLY a JSON object (no markdown, no extra text):
{"label": "📄 Get full cheat sheet", "prompt": "Give me a full cheat sheet on this topic"}
Label: start with emoji, max 6 words."""
    result = call_api([{"role": "user", "content": f"Last reply about: {last_ai_reply[:300]}"}], system_prompt)
    try:
        result = result.strip().replace("```json", "").replace("```", "").strip()
        parsed = json.loads(result)
        return parsed.get("label", "🔍 Explore further"), parsed.get("prompt", "Tell me more about this topic")
    except:
        return "🔍 Explore further", "Tell me more about this topic"

# ============================================================
# INTENT DETECTION
# ============================================================
def detect_intent(prompt: str) -> str:
    p = prompt.lower().strip()
    if any(s in p for s in ["explain", "cheat sheet", "give me", "tell me", "what is", "what are", "define", "formula", "how does", "how do", "steps", "derive", "proof", "theorem", "law of", "principle", "list", "name"]):
        return "direct"
    if any(s in p for s in ["hi", "hello", "hey", "thanks", "thank you", "bye", "good morning", "good night"]) and len(p.split()) < 6:
        return "casual"
    if any(s in p for s in ["hate", "difficult", "hard", "don't understand", "confused", "stuck", "panic", "scared", "anxious", "i can't", "lost", "frustrated"]):
        return "empathetic"
    return "socratic"

# ============================================================
# CHECK IF ANSWER IS CORRECT
# ============================================================
def check_if_correct(ai_response: str) -> bool:
    positive = ["correct", "that's right", "well done", "excellent", "perfect", "great job",
                "spot on", "you got it", "absolutely right", "100%", "🎉", "right answer"]
    return any(p in ai_response.lower() for p in positive)

# ============================================================
# MAIN AI RESPONSE
# ============================================================
def get_ai_response(prompt: str, msg_type: str, topic_tag: str):
    days_left = (st.session_state.test_date - date.today()).days
    crunch_mode = (days_left <= 3 and st.session_state.has_specific_date)

    current_messages = st.session_state.threads[st.session_state.current_thread]
    history = []
    for msg in current_messages:
        if not msg.get("hidden") and msg.get("msg_type") not in ("welcome", "stats", "system_trigger"):
            role = "user" if msg["role"] == "user" else "assistant"
            history.append({"role": role, "content": msg["content"]})
    history = history[-10:]

    original_q_reminder = ""
    if st.session_state.original_question:
        original_q_reminder = f"\n\nIMPORTANT: The student's ORIGINAL question was: \"{st.session_state.original_question}\". Always keep this in mind."

    # Evaluate answer
    if msg_type == "evaluate_answer":
        system_prompt = f"""You are FocusFlow, a warm encouraging tutor for {st.session_state.exam_goal} {st.session_state.current_topic}.{original_q_reminder}

You previously asked this Socratic question:
"{st.session_state.last_socratic_question}"

The student answered: "{prompt}"

IMPORTANT: Student may type just "A", "B", "C", "D" — match against the options in the question above.

If CORRECT:
- Start with "🎉 That's correct!" and warm praise
- Then give full explanation of the concept
- End with encouragement like "You're doing great! 🚀"

If INCORRECT or PARTIAL:
- Start with "Not quite, but great attempt! 💪"
- Gently explain what was wrong
- Then explain the full concept clearly
- End with encouragement

Use markdown. Do NOT ask another question."""

    elif msg_type == "casual":
        system_prompt = f"""You are FocusFlow, a warm study buddy.{original_q_reminder}
Respond warmly and conversationally. Keep under 3 sentences. Be encouraging."""

    elif msg_type == "empathetic":
        system_prompt = f"""Student is struggling emotionally.{original_q_reminder}
Be deeply empathetic. Acknowledge feelings. Share ONE motivational tip.
Suggest ONE tiny next step for {st.session_state.current_topic}. Be warm like a caring older sibling."""

    elif msg_type == "direct" or crunch_mode:
        system_prompt = f"""You are an expert {st.session_state.exam_goal} tutor for {st.session_state.current_topic}.{original_q_reminder}
Give a CLEAR STRUCTURED answer with markdown:
## 📋 [Topic]
### 🔑 Core Concept
### 🧮 Key Formula / Steps
### ⚠️ Common Mistake
### 💡 Quick Example"""

    else:
        system_prompt = f"""You are a Socratic tutor for {st.session_state.exam_goal} {st.session_state.current_topic}.{original_q_reminder}

The student asked: "{prompt}"

Your ONLY job: Ask ONE diagnostic multiple choice question to check their understanding BEFORE explaining anything.

Rules:
- Directly related to what they asked
- Give 4 options: A) B) C) D)
- Do NOT explain the concept yet
- Do NOT give the answer
- Keep it under 5 lines
- End EXACTLY with: "Take your time! If you're stuck, click the 'Cheat Sheet' button below 👇"

Format:
Quick check before I explain — [question]?
A) option  B) option  C) option  D) option

Take your time! If you're stuck, click the 'Cheat Sheet' button below 👇"""

    history.append({"role": "user", "content": prompt})
    return call_api(history, system_prompt), msg_type

# ============================================================
# WELCOME CONTENT
# ============================================================
SUBJECT_CONTENT = {
    "Physics": {
        "concepts": ["Newton's Laws", "Thermodynamics", "Optics"],
        "starters": ["What is Newton's First Law?", "Explain how a lens works", "What is the principle of conservation of energy?"]
    },
    "Chemistry": {
        "concepts": ["Periodic Table", "Chemical Bonding", "Organic Chemistry"],
        "starters": ["Why are Noble gases inert?", "Explain covalent bonding", "How do I balance a redox reaction?"]
    },
    "History": {
        "concepts": ["World War I", "French Revolution", "Industrial Revolution"],
        "starters": ["What were the main causes of WWI?", "What triggered the French Revolution?", "How did the steam engine change the world?"]
    },
    # ... add as many as you like!
}

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### 🎯 Your Goal")
    exam_goal = st.selectbox("Exam/Goal", ["JEE Main", "NEET", "10th Boards", "12th Boards", "UPSC", "Other"],
        index=["JEE Main", "NEET", "10th Boards", "12th Boards", "UPSC", "Other"].index(st.session_state.exam_goal))
    current_topic = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English", "History", "Other"],
        index=["Physics", "Chemistry", "Maths", "Biology", "English", "History", "Other"].index(st.session_state.current_topic))

    if exam_goal == "Other":
        has_date = st.radio("Choose one:", ["Yes, I have a test date", "No, just learning"],
            index=0 if st.session_state.has_specific_date else 1, label_visibility="collapsed")
        st.session_state.has_specific_date = (has_date == "Yes, I have a test date")
        if st.session_state.has_specific_date:
            test_date = st.date_input("Test Date", value=st.session_state.test_date, min_value=date.today())
        else:
            test_date = date.today() + timedelta(days=365)
            st.caption("📌 Learning at your own pace!")
    else:
        st.session_state.has_specific_date = True
        test_date = st.date_input("Test Date", value=st.session_state.test_date, min_value=date.today())

    days_left = (test_date - date.today()).days
    if st.session_state.has_specific_date:
        if days_left <= 3: st.error(f"🚨 {days_left} days left! CRUNCH MODE")
        elif days_left <= 14: st.warning(f"⏰ {days_left} days left")
        else: st.info(f"📅 {days_left} days left")

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
    st.markdown("### ⚠️ Focus Areas")
    if st.session_state.weak_areas:
        for topic, count in sorted(st.session_state.weak_areas.items(), key=lambda x: x[1], reverse=True)[:5]:
            st.markdown(f"<span class='weak-area-tag'>{topic} ({count})</span>", unsafe_allow_html=True)
    else:
        st.caption("Keep studying to see your focus areas!")

    st.divider()
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

    # DAILY CHALLENGE
    st.markdown("### 🎯 Daily Challenge")
    today = date.today()

    if st.session_state.daily_challenge_date != today:
        st.session_state.daily_challenge = None
        st.session_state.daily_challenge_completed = False
        st.session_state.daily_challenge_subject = None

    if st.session_state.daily_challenge_subject and st.session_state.daily_challenge_subject != current_topic:
        st.session_state.daily_challenge = None
        st.session_state.daily_challenge_completed = False
        st.session_state.daily_challenge_subject = None

    if st.session_state.daily_challenge_date:
        yesterday = today - timedelta(days=1)
        if st.session_state.daily_challenge_date == yesterday and not st.session_state.daily_challenge_completed:
            st.session_state.challenge_streak = 0

    if st.session_state.challenge_streak > 0:
        flame = "🔥" * min(st.session_state.challenge_streak, 5)
        st.markdown(f"<div class='streak-badge'>{flame} {st.session_state.challenge_streak} day challenge streak!</div>", unsafe_allow_html=True)

    if not st.session_state.daily_challenge and not st.session_state.daily_challenge_completed:
        with st.spinner("📝 Generating today's challenge..."):
            challenge_text = generate_daily_challenge(current_topic, exam_goal)
            st.session_state.daily_challenge = challenge_text
            st.session_state.daily_challenge_date = today
            st.session_state.daily_challenge_subject = current_topic

    if st.session_state.daily_challenge and not st.session_state.daily_challenge_completed:
        st.markdown(f"<div class='challenge-box'>{st.session_state.daily_challenge}</div>", unsafe_allow_html=True)
        if st.button("✅ Mark as Complete", use_container_width=True, type="primary"):
            st.session_state.daily_challenge_completed = True
            st.session_state.challenge_streak += 1
            st.session_state.challenge_history.append({"date": str(today), "subject": current_topic, "completed": True})
            st.balloons()
            st.toast(f"🎉 Challenge done! Streak: {st.session_state.challenge_streak}")
            st.rerun()
    elif st.session_state.daily_challenge_completed:
        st.markdown("<div class='challenge-complete'>✅ <b>Today's challenge done!</b><br>🎉 Come back tomorrow for a new one!</div>", unsafe_allow_html=True)

    if st.session_state.challenge_history:
        st.divider()
        st.markdown("### 📊 This Week")
        this_week = [c for c in st.session_state.challenge_history
                     if datetime.strptime(c["date"], "%Y-%m-%d").date() >= today - timedelta(days=7)]
        done = sum(1 for c in this_week if c["completed"])
        st.markdown(f"✅ **{done}/7** challenges completed this week")

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
    days_info = f"**{days_left} days** until your {st.session_state.exam_goal} exam!" if st.session_state.has_specific_date else "Learning at your own pace — no pressure!"
    subject_data = SUBJECT_CONTENT.get(st.session_state.current_topic, SUBJECT_CONTENT["Other"])
    welcome = f"""👋 Hey! I'm your FocusFlow coach.

**Current Setup:** {st.session_state.exam_goal} | {st.session_state.current_topic} | {days_info}

I can help you:
- 🧠 **Explain concepts** — Just ask "{subject_data['example_concept']}"
- ❓ **Socratic mode** — I'll check your understanding first. Stuck? Click the button!
- 📝 **Practice questions** — Quick mock tests

**Try asking: "{subject_data['example_question']}"**"""
    current_messages.append({"role": "assistant", "content": welcome, "msg_type": "welcome"})

for i, message in enumerate(current_messages):
    if message.get("hidden"):
        continue

    msg_type = message.get("msg_type", "default")
    is_correct = message.get("is_correct", False)
    avatar = "🧠" if message["role"] == "assistant" else "🧑‍🎓"

    with st.chat_message(message["role"], avatar=avatar):
        if msg_type == "welcome":
            st.markdown(f"<div class='welcome-box'>{message['content']}</div>", unsafe_allow_html=True)
        elif msg_type == "cheat_sheet":
            st.markdown(f"<div class='cheat-sheet-box'>{message['content']}</div>", unsafe_allow_html=True)
        elif msg_type == "socratic":
            st.markdown(f"<div class='socratic-box'>{message['content']}</div>", unsafe_allow_html=True)
        elif msg_type == "evaluate_answer":
            if is_correct:
                st.markdown(f"<div class='evaluate-correct-box'>{message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='evaluate-wrong-box'>{message['content']}</div>", unsafe_allow_html=True)
        elif msg_type == "stats":
            st.markdown(f"<div class='stats-box'>{message['content']}</div>", unsafe_allow_html=True)
        elif msg_type == "error":
            st.markdown(f"<div class='error-box'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(message["content"])

        if message["role"] == "assistant" and "subject" in message:
            st.markdown(f"<span class='subject-pill'>📚 {message['subject']}</span>", unsafe_allow_html=True)

        # STUCK button
        if (message["role"] == "assistant" and
            message.get("msg_type") == "socratic" and
            not message.get("resolved", False)):
            if st.button("⚡ Stuck? Get the cheat sheet", key=f"stuck_{st.session_state.current_thread}_{i}"):
                message["resolved"] = True
                st.session_state.awaiting_answer = False
                st.session_state.last_socratic_question = None
                weak_key = f"{st.session_state.current_topic}: {message.get('topic', 'General')}"
                st.session_state.weak_areas[weak_key] = st.session_state.weak_areas.get(weak_key, 0) + 1
                trigger = f"[SYSTEM: Student clicked Stuck. Give cheat sheet for: {message.get('topic', 'topic')}]"
                current_messages.append({"role": "user", "content": trigger, "hidden": True, "msg_type": "system_trigger"})
                with st.chat_message("assistant", avatar="🧠"):
                    with st.spinner("Generating cheat sheet..."):
                        answer, _ = get_ai_response(trigger, "direct", message.get("topic", "General"))
                        current_messages.append({"role": "assistant", "content": answer, "msg_type": "cheat_sheet",
                                                 "topic": message.get("topic", "General"),
                                                 "subject": st.session_state.current_topic, "resolved": True})
                st.rerun()

        # SMART FOLLOW-UP BUTTON
        is_last = (i == len(current_messages) - 1)
        if (message["role"] == "assistant" and is_last and
            msg_type not in ("welcome", "socratic", "stats") and
            st.session_state.last_followup_label):
            st.markdown("<div class='followup-btn'>", unsafe_allow_html=True)
            if st.button(st.session_state.last_followup_label, key=f"followup_{i}"):
                followup_prompt = st.session_state.last_followup_prompt
                st.session_state.last_followup_label = None
                st.session_state.last_followup_prompt = None
                current_messages.append({"role": "user", "content": followup_prompt, "msg_type": "user_question"})
                with st.chat_message("assistant", avatar="🧠"):
                    with st.spinner("Thinking..."):
                        answer, mt = get_ai_response(followup_prompt, "direct", followup_prompt[:40])
                        current_messages.append({"role": "assistant", "content": answer, "msg_type": mt,
                                                 "subject": st.session_state.current_topic, "resolved": True})
                        label, prompt_s = generate_followup(answer, st.session_state.current_topic)
                        st.session_state.last_followup_label = label
                        st.session_state.last_followup_prompt = prompt_s
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# PENDING AI REQUESTS
# ============================================================
if st.session_state.pending_ai_request:
    request = st.session_state.pending_ai_request
    st.session_state.pending_ai_request = None
    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner("Thinking..."):
            answer, msg_type = get_ai_response(request["prompt"], request["msg_type"], request["topic"])
            current_messages.append({"role": "assistant", "content": answer, "msg_type": msg_type,
                                     "topic": request["topic"], "subject": st.session_state.current_topic,
                                     "resolved": True, "is_correct": False})
            if msg_type == "socratic":
                st.session_state.awaiting_answer = True
                st.session_state.last_socratic_question = answer
            else:
                label, prompt_s = generate_followup(answer, st.session_state.current_topic)
                st.session_state.last_followup_label = label
                st.session_state.last_followup_prompt = prompt_s
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

    user_msgs = [m for m in current_messages if m["role"] == "user" and not m.get("hidden")]
    if len(user_msgs) == 1:
        st.session_state.original_question = prompt

    # Determine intent
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

    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner("Thinking..."):
            answer, msg_type = get_ai_response(prompt, intent, topic_tag)

            is_correct = False
            if intent == "evaluate_answer":
                is_correct = check_if_correct(answer)
                if is_correct:
                    show_clap_celebration()

            if msg_type == "socratic":
                st.session_state.awaiting_answer = True
                st.session_state.last_socratic_question = answer
                st.session_state.last_followup_label = None
                st.session_state.last_followup_prompt = None
            else:
                label, prompt_s = generate_followup(answer, st.session_state.current_topic)
                st.session_state.last_followup_label = label
                st.session_state.last_followup_prompt = prompt_s

            final_msg_type = "evaluate_answer" if intent == "evaluate_answer" else msg_type
            current_messages.append({
                "role": "assistant", "content": answer,
                "msg_type": final_msg_type, "topic": topic_tag,
                "subject": st.session_state.current_topic,
                "resolved": True, "is_correct": is_correct
            })
    st.rerun()

# ============================================================
# QUICK ACTION BUTTONS
# ============================================================
st.divider()
qa_col1, qa_col2, qa_col3, qa_col4 = st.columns(4)

with qa_col1:
    if st.button("📄 Cheat Sheet", use_container_width=True):
        p = f"Give me a comprehensive cheat sheet for {st.session_state.current_topic} ({st.session_state.exam_goal})"
        current_messages.append({"role": "user", "content": p, "msg_type": "user_question"})
        st.session_state.pending_ai_request = {"prompt": p, "msg_type": "direct", "topic": f"{st.session_state.current_topic} Cheat Sheet"}
        st.rerun()

with qa_col2:
    if st.button("📝 Mock Test", use_container_width=True):
        p = f"Generate 5 practice questions for {st.session_state.current_topic} ({st.session_state.exam_goal}) with answers and explanations"
        current_messages.append({"role": "user", "content": p, "msg_type": "user_question"})
        st.session_state.pending_ai_request = {"prompt": p, "msg_type": "direct", "topic": f"{st.session_state.current_topic} Mock Test"}
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
                prefix = "🧑‍🎓 You" if msg["role"] == "user" else "🧠 FocusFlow"
                chat_text.append(f"{prefix}:\n{msg['content']}")
        export_text = (f"FocusFlow Chat Export\n{'='*50}\nExam: {st.session_state.exam_goal}\n"
                       f"Subject: {st.session_state.current_topic}\nDate: {date.today()}\n{'='*50}\n\n"
                       + "\n\n---\n\n".join(chat_text))
        st.download_button("📥 Download Chat", export_text,
                           file_name=f"focusflow_{st.session_state.current_thread}_{date.today()}.txt",
                           mime="text/plain", use_container_width=True)
