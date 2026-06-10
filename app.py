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
    "pomodoro_active": False,
    "pomodoro_end": None,
    # ENHANCED DAILY CHALLENGE STATE
    "daily_challenge": None,
    "daily_challenge_date": None,
    "daily_challenge_completed": False,
    "challenge_streak": 0,
    "last_challenge_completed_date": None,
    "challenge_history": [],  # List of {date, subject, challenge_text, completed}
    "pending_ai_request": None,
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
    
    # AI Status
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
    
       st.divider()
    
    # ============================================================
    # POMODORO TIMER — FIXED WITH JAVASCRIPT
    # ============================================================
    
    st.markdown("### ⏱️ Focus Timer")
    
    # Start / Stop buttons
    pomo_cols = st.columns(2)
    with pomo_cols[0]:
        if st.button("▶️ 25m", use_container_width=True, key="pomo_start"):
            st.session_state.pomodoro_active = True
            st.session_state.pomodoro_end = datetime.now() + timedelta(minutes=25)
            st.rerun()
    
    with pomo_cols[1]:
        if st.button("⏹️ Stop", use_container_width=True, key="pomo_stop"):
            st.session_state.pomodoro_active = False
            st.session_state.pomodoro_end = None
            st.rerun()
    
    # Timer display
    if st.session_state.pomodoro_active and st.session_state.pomodoro_end:
        remaining = st.session_state.pomodoro_end - datetime.now()
        total_seconds = int(remaining.total_seconds())
        
        if total_seconds <= 0:
            # Timer completed!
            st.session_state.pomodoro_active = False
            st.session_state.total_study_minutes += 25
            st.balloons()
            st.success("🎉 25 min done! Take a 5 min break.")
            st.session_state.pomodoro_end = None
            st.rerun()
        else:
            # Live JavaScript countdown
            mins, secs = divmod(total_seconds, 60)
            
            st.markdown(f"""
            <div style="text-align: center; margin: 12px 0;">
                <div id="pomodoro-timer" style="
                    font-size: 32px; 
                    font-weight: bold; 
                    color: #FF6600;
                    font-family: monospace;
                ">{mins:02d}:{secs:02d}</div>
            </div>
            
            <script>
                (function() {{
                    let totalSeconds = {total_seconds};
                    const timerElement = document.getElementById('pomodoro-timer');
                    
                    const countdown = setInterval(function() {{
                        totalSeconds--;
                        
                        if (totalSeconds <= 0) {{
                            clearInterval(countdown);
                            timerElement.innerHTML = "00:00 ✅";
                            timerElement.style.color = "#4CAF50";
                            setTimeout(function() {{
                                window.parent.postMessage({{type: 'streamlit:run'}}, '*');
                            }}, 1000);
                        }} else {{
                            const m = Math.floor(totalSeconds / 60);
                            const s = totalSeconds % 60;
                            timerElement.innerHTML = 
                                (m < 10 ? '0' : '') + m + ':' + 
                                (s < 10 ? '0' : '') + s;
                        }}
                    }}, 1000);
                }})();
            </script>
            """, unsafe_allow_html=True)
    
    st.divider()
        else:
            st.session_state.pomodoro_active = False
            st.session_state.total_study_minutes += 25
            st.balloons()
            st.success("🎉 25 min done! Take a 5 min break.")
    
    st.divider()
    
    # ============================================================
    # ENHANCED DAILY CHALLENGE WITH PRE-BUILT QUESTIONS
    # ============================================================
    st.markdown("### 🎯 Daily Challenge")
    
    today = date.today()
    
    # Check if yesterday's challenge was missed
    if st.session_state.daily_challenge_date:
        yesterday = today - timedelta(days=1)
        last_challenge_date = st.session_state.daily_challenge_date
        
        if last_challenge_date == yesterday and not st.session_state.daily_challenge_completed:
            if st.session_state.daily_challenge:
                st.session_state.challenge_history.append({
                    "date": str(yesterday),
                    "subject": st.session_state.current_topic,
                    "challenge": st.session_state.daily_challenge,
                    "completed": False
                })
            st.session_state.challenge_streak = 0
            st.session_state.daily_challenge = None
            st.session_state.daily_challenge_date = None
            st.session_state.daily_challenge_completed = False
    
    if st.session_state.daily_challenge_date != today:
        st.session_state.daily_challenge = None
        st.session_state.daily_challenge_completed = False
    
    # CHALLENGE STREAK BADGE
    if st.session_state.challenge_streak > 0:
        flame = "🔥" * min(st.session_state.challenge_streak, 5)
        st.markdown(f"<div class='streak-badge'><span class='streak-flame'>{flame}</span> {st.session_state.challenge_streak} day streak!</div>", unsafe_allow_html=True)
    
    # DISPLAY CHALLENGE
    if st.session_state.daily_challenge and not st.session_state.daily_challenge_completed:
        st.markdown(f"<div class='challenge-box'>{st.session_state.daily_challenge}</div>", unsafe_allow_html=True)
        
        if st.button("✅ Mark as Complete", use_container_width=True, type="primary"):
            st.session_state.daily_challenge_completed = True
            st.session_state.last_challenge_completed_date = today
            
            if st.session_state.last_challenge_completed_date == today - timedelta(days=1):
                st.session_state.challenge_streak += 1
            else:
                st.session_state.challenge_streak = 1
            
            st.session_state.challenge_history.append({
                "date": str(today),
                "subject": st.session_state.current_topic,
                "challenge": st.session_state.daily_challenge,
                "completed": True
            })
            
            st.balloons()
            st.toast("🎉 Challenge completed! Streak: " + str(st.session_state.challenge_streak))
            st.rerun()
    
    elif st.session_state.daily_challenge and st.session_state.daily_challenge_completed:
        st.markdown(f"<div class='challenge-complete'><b>✅ Completed!</b><br>{st.session_state.daily_challenge}<br><br>🎉 Great job! Come back tomorrow for a new challenge.</div>", unsafe_allow_html=True)
        
    else:
        # No challenge generated yet for today
        if st.button("🎯 Generate Today's Challenge", use_container_width=True):
            import random
            
            # If weak areas exist, use AI to create targeted challenge (1 API call)
            if st.session_state.weak_areas:
                weakest_topic = sorted(st.session_state.weak_areas.items(), key=lambda x: x[1], reverse=True)[0][0]
                challenge_text = random.choice([
                    "Create a cheat sheet for {topic}",
                    "Explain {topic} to yourself as if teaching a 5-year-old",
                    "Find 3 previous year questions on {topic} and solve them",
                    "Draw a mind map of {topic} on paper",
                    "Write 5 flashcards for {topic}"
                ]).format(topic=weakest_topic)
                st.session_state.daily_challenge = f"📋 <b>Today's Challenge:</b><br>{challenge_text}<br><br><i>💡 This is based on your weak area: {weakest_topic}</i>"
            
            # Otherwise use pre-built question bank (ZERO API cost)
            else:
                CHALLENGE_BANKS = {
                    "Physics": [
                        {"task": "Solve these 3 problems:", "questions": [
                            "1. A car accelerates from 0 to 20 m/s in 5s. Find acceleration.",
                            "2. A 5kg object is pushed with 10N force. Find acceleration (F=ma).",
                            "3. A ball is thrown upward at 20 m/s. Find max height (g=10 m/s²)."
                        ]},
                        {"task": "Concept check:", "questions": [
                            "1. State Newton's First Law with one real-life example.",
                            "2. Differentiate between speed and velocity.",
                            "3. What is centripetal force? Give an example."
                        ]}
                    ],
                    "Chemistry": [
                        {"task": "Balance these equations:", "questions": [
                            "1. H₂ + O₂ → H₂O",
                            "2. Fe + O₂ → Fe₂O₃",
                            "3. Al + HCl → AlCl₃ + H₂"
                        ]}
                    ],
                    "Maths": [
                        {"task": "Solve these quadratic equations:", "questions": [
                            "1. x² - 5x + 6 = 0",
                            "2. 2x² + 7x + 3 = 0",
                            "3. x² - 4 = 0"
                        ]}
                    ],
                    "Biology": [
                        {"task": "Answer these cell biology questions:", "questions": [
                            "1. Name the powerhouse of the cell and its function.",
                            "2. Differentiate between plant and animal cells (3 differences).",
                            "3. What is osmosis? Give a real-life example."
                        ]}
                    ],
                    "English": [
                        {"task": "Literature analysis:", "questions": [
                            "1. What is the central theme of 'The Road Not Taken'?",
                            "2. Identify 2 literary devices used in the poem.",
                            "3. Why did the poet feel sorry in the poem?"
                        ]}
                    ],
                    "History": [
                        {"task": "Ancient Indian History:", "questions": [
                            "1. Name 2 major cities of the Indus Valley Civilization.",
                            "2. What was the Great Bath used for?",
                            "3. Name the script used by the Harappans."
                        ]},
                        {"task": "World War I:", "questions": [
                            "1. Name 2 immediate causes of WWI.",
                            "2. What was the Treaty of Versailles?",
                            "3. Which countries formed the Triple Alliance?"
                        ]}
                    ],
                    "Other": [
                        {"task": "General practice:", "questions": [
                            "1. Solve: 15 + 27 × 3 - 8",
                            "2. Convert 3/4 to decimal and percentage.",
                            "3. Find the area of a circle with radius 7cm (π=22/7)."
                        ]}
                    ]
                }
                
                subject_bank = CHALLENGE_BANKS.get(st.session_state.current_topic, CHALLENGE_BANKS["Other"])
                selected = random.choice(subject_bank)
                
                questions_html = "<br>".join(selected["questions"])
                st.session_state.daily_challenge = f"""
📋 <b>Today's Challenge: {selected['task']}</b><br><br>
{questions_html}<br><br>
<i>💡 Solve these on paper or in your notebook, then mark complete!</i>
"""
            
            st.session_state.daily_challenge_date = today
            st.session_state.daily_challenge_completed = False
            st.rerun()
    
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
        st.rerun()
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
# AI RESPONSE FUNCTION
# ============================================================

def get_ai_response(prompt: str, msg_type: str, topic_tag: str, uploaded_image=None):
    try:
        provider = api_config["provider"]
        model = api_config["model"]
        days_left = (st.session_state.test_date - date.today()).days
        crunch_mode = (days_left <= 3 and st.session_state.has_specific_date)
        
        if msg_type == "casual":
            system_prompt = f"""You are FocusFlow, a warm study buddy. The student said: "{prompt}"
Respond conversationally and warmly. If it's a greeting, greet back and briefly mention you're ready to help with {st.session_state.current_topic}.
Keep under 3 sentences. Be encouraging. No study pressure right now."""
            
        elif msg_type == "empathetic":
            system_prompt = f"""The student is struggling emotionally with studying. They said: "{prompt}"
Be deeply empathetic. Acknowledge their feelings genuinely. Share ONE quick motivational tip or breathing technique.
Then gently suggest ONE tiny, manageable next step related to {st.session_state.current_topic}.
Keep it warm, not robotic. Like a caring older sibling, not a teacher."""
            
        elif msg_type == "direct" or crunch_mode:
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
            
        else:
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
        
        if provider == "groq":
            messages = [{"role": "system", "content": system_prompt}]
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            headers = {
                "Authorization": f"Bearer {api_config['key']}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(api_config["url"], json=payload, headers=headers, timeout=30).json()
            
            if 'choices' in response and response['choices']:
                return response['choices'][0]['message']['content'], msg_type
            else:
                error = response.get('error', {}).get('message', 'Unknown error')
                return f"⚠️ Groq Error: {error}", "error"
        
        elif provider == "openrouter":
            messages = [{"role": "system", "content": system_prompt}]
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            headers = {
                "Authorization": f"Bearer {api_config['key']}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://focusflow.app",
                "X-Title": "FocusFlow"
            }
            
            response = requests.post(api_config["url"], json=payload, headers=headers, timeout=30).json()
            
            if 'choices' in response and response['choices']:
                return response['choices'][0]['message']['content'], msg_type
            else:
                error = response.get('error', {}).get('message', 'Unknown error')
                return f"⚠️ OpenRouter Error: {error}", "error"
        
        else:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_config['key']}"
            
            content_parts = [{"text": system_prompt + "\n\nUser: " + prompt}]
            
            payload = {
                "contents": [{"parts": content_parts}],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1000
                }
            }
            
            response = requests.post(url, json=payload, timeout=30).json()
            
            if 'candidates' in response and response['candidates']:
                return response['candidates'][0]['content']['parts'][0]['text'], msg_type
            else:
                error = response.get('error', {}).get('message', 'Unknown API error')
                return f"⚠️ Google Error: {error}", "error"
            
    except requests.exceptions.RequestException as e:
        return f"🌐 Connection error: {str(e)}", "error"
    except Exception as e:
        return f"❌ Error: {str(e)}", "error"

# ============================================================
# SUBJECT-SPECIFIC WELCOME CONTENT
# ============================================================

SUBJECT_CONTENT = {
    "Physics": {
        "example_concept": "Explain Newton's Laws of Motion",
        "example_question": "What is Newton's First Law?"
    },
    "Chemistry": {
        "example_concept": "Explain balancing chemical equations",
        "example_question": "How do I balance chemical equations?"
    },
    "Maths": {
        "example_concept": "Explain quadratic equations",
        "example_question": "How do I solve quadratic equations?"
    },
    "Biology": {
        "example_concept": "Explain Photosynthesis",
        "example_question": "What is photosynthesis?"
    },
    "English": {
        "example_concept": "Explain the theme of 'The Road Not Taken'",
        "example_question": "What is the theme of 'The Road Not Taken'?"
    },
    "History": {
        "example_concept": "Explain the causes of World War I",
        "example_question": "What were the main causes of World War I?"
    },
    "Other": {
        "example_concept": "Explain the Pythagorean Theorem",
        "example_question": "What is the Pythagorean Theorem?"
    }
}

# ============================================================
# DISPLAY CHAT
# ============================================================

current_messages = st.session_state.threads[st.session_state.current_thread]

days_left = (st.session_state.test_date - date.today()).days

# Welcome message if thread is empty
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
    
    current_messages.append({
        "role": "assistant",
        "content": welcome,
        "msg_type": "welcome"
    })

# Render messages
for i, message in enumerate(current_messages):
    with st.chat_message(message["role"]):
        
        msg_type = message.get("msg_type", "default")
        if msg_type == "welcome":
            st.markdown(f"<div class='welcome-box'>{message['content']}</div>", unsafe_allow_html=True)
        elif msg_type == "cheat_sheet":
            st.markdown(f"<div class='cheat-sheet-box'>{message['content']}</div>", unsafe_allow_html=True)
        elif msg_type == "socratic":
            st.markdown(f"<div class='socratic-box'>{message['content']}</div>", unsafe_allow_html=True)
        elif msg_type == "stats":
            st.markdown(f"<div class='stats-box'>{message['content']}</div>", unsafe_allow_html=True)
        elif msg_type == "error":
            st.markdown(f"<div class='error-box'>{message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(message["content"])
        
        if message["role"] == "assistant" and "subject" in message:
            st.markdown(f"<span class='subject-pill'>📚 {message['subject']}</span>", unsafe_allow_html=True)
        
        # "STUCK?" BUTTON
        if (message["role"] == "assistant" and
            message.get("msg_type") == "socratic" and
            not message.get("resolved", False)):
            
            if st.button("⚡ Stuck? Get the cheat sheet", key=f"stuck_btn_{st.session_state.current_thread}_{i}"):
                message["resolved"] = True
                
                weak_key = f"{st.session_state.current_topic}: {message.get('topic', 'General')}"
                st.session_state.weak_areas[weak_key] = st.session_state.weak_areas.get(weak_key, 0) + 1
                
                trigger_prompt = f"[SYSTEM: Student clicked 'Stuck' on Socratic question about: {message.get('topic', 'topic')}. Provide direct, structured cheat sheet with: 1) Core concept 2) Key formula/steps 3) Common mistake 4) Quick example. Be concise.]"
                
                current_messages.append({
                    "role": "user",
                    "content": trigger_prompt,
                    "hidden": True,
                    "msg_type": "system_trigger"
                })
                
                with st.chat_message("assistant"):
                    with st.spinner('Generating cheat sheet...'):
                        answer, _ = get_ai_response(trigger_prompt, "direct", message.get('topic', 'General'))
                        current_messages.append({
                            "role": "assistant",
                            "content": answer,
                            "msg_type": "cheat_sheet",
                            "topic": message.get('topic', 'General'),
                            "subject": st.session_state.current_topic,
                            "resolved": True
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
# PROCESS PENDING AI REQUESTS
# ============================================================

if st.session_state.pending_ai_request:
    request = st.session_state.pending_ai_request
    st.session_state.pending_ai_request = None
    
    with st.chat_message("assistant"):
        with st.spinner('Thinking...'):
            answer, msg_type = get_ai_response(
                request["prompt"],
                request["msg_type"],
                request["topic"],
                uploaded_image if request.get("has_image") else None
            )
            
            current_messages.append({
                "role": "assistant",
                "content": answer,
                "msg_type": msg_type,
                "topic": request["topic"],
                "subject": st.session_state.current_topic,
                "resolved": True if msg_type != "socratic" else False
            })
    st.rerun()

# ============================================================
# CHAT INPUT
# ============================================================

if prompt := st.chat_input("Ask a question..."):
    
    today = date.today()
    if st.session_state.last_study_date != today:
        st.session_state.study_streak += 1
        st.session_state.last_study_date = today
    
    current_messages.append({
        "role": "user",
        "content": prompt,
        "msg_type": "user_question"
    })
    
    intent = detect_intent(prompt)
    topic_tag = prompt[:40]
    
    with st.chat_message("assistant"):
        with st.spinner('Thinking...'):
            answer, msg_type = get_ai_response(prompt, intent, topic_tag, uploaded_image)
            
            current_messages.append({
                "role": "assistant",
                "content": answer,
                "msg_type": msg_type,
                "topic": topic_tag,
                "subject": st.session_state.current_topic,
                "resolved": False if msg_type == "socratic" else True
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
        current_messages.append({
            "role": "user",
            "content": cheat_prompt,
            "msg_type": "user_question"
        })
        st.session_state.pending_ai_request = {
            "prompt": cheat_prompt,
            "msg_type": "direct",
            "topic": f"{st.session_state.current_topic} Cheat Sheet",
            "has_image": False
        }
        st.rerun()

with qa_col2:
    if st.button("📝 Mock Test", use_container_width=True):
        mock_prompt = f"Generate 5 practice questions for {st.session_state.current_topic} ({st.session_state.exam_goal}) with answers and explanations"
        current_messages.append({
            "role": "user",
            "content": mock_prompt,
            "msg_type": "user_question"
        })
        st.session_state.pending_ai_request = {
            "prompt": mock_prompt,
            "msg_type": "direct",
            "topic": f"{st.session_state.current_topic} Mock Test",
            "has_image": False
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
