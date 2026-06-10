import streamlit as st
import requests
from datetime import datetime, timedelta

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="FocusFlow — AI Study Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
defaults = {
    "messages": {},           # subject -> list of {role, content}
    "current_subject": "Physics",
    "pomodoro_active": False,
    "pomodoro_end": None,
    "total_study_minutes": 0,
    "streak_days": 0,
    "sessions_today": 0,
    "pending_ai_request": None,
    "last_response_was_question": False,
    "api_key": "",
    "api_provider": "openrouter",  # "openrouter" or "google"
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

SUBJECTS = ["Physics", "Chemistry", "Mathematics", "Biology", "English", "History", "Geography"]

# ============================================================
# API HELPERS
# ============================================================
def call_openrouter(messages, system_prompt, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://focusflow.streamlit.app",
        "X-Title": "FocusFlow",
    }
    payload = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "max_tokens": 1024,
    }
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions",
                          headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ API error: {str(e)}"


def call_google(messages, system_prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    history = []
    for m in messages:
        history.append({"role": "user" if m["role"] == "user" else "model",
                         "parts": [{"text": m["content"]}]})
    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": history,
    }
    try:
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"❌ API error: {str(e)}"


def get_ai_response(user_message, subject, intent="auto"):
    api_key = st.session_state.api_key
    if not api_key:
        return "⚠️ No API key set. Please add your key in the sidebar settings."

    system_prompt = f"""You are FocusFlow, an expert AI tutor helping Indian students (JEE, NEET, Boards) study {subject}.

Your teaching style depends on intent:
- "socratic": Ask ONE diagnostic question to check understanding before explaining. End with a question mark.
- "direct": Give a clear, concise explanation immediately. No question at the end.
- "cheat_sheet": Give a quick summary/cheat sheet with key formulas or concepts.
- "casual": Respond conversationally and friendly.
- "empathetic": Acknowledge the student's feelings first, then gently redirect to studying.

Current intent: {intent}

Keep responses focused, encouraging, and appropriate for Indian school/competitive exam students."""

    history = st.session_state.messages.get(subject, [])
    history_for_api = history[-10:]  # Last 10 messages for context
    history_for_api.append({"role": "user", "content": user_message})

    if st.session_state.api_provider == "google":
        return call_google(history_for_api, system_prompt, api_key)
    else:
        return call_openrouter(history_for_api, system_prompt, api_key)


def detect_intent(message: str) -> str:
    msg = message.lower().strip()
    empathy_words = ["stressed", "tired", "anxious", "scared", "worried", "can't", "cannot", "hate", "hate this", "give up"]
    casual_words = ["hello", "hi", "hey", "thanks", "thank you", "ok", "okay", "cool", "bye", "lol"]
    direct_words = ["explain", "what is", "define", "how does", "tell me", "show me", "summarize", "give me"]
    cheat_words = ["cheat sheet", "quick notes", "formula", "key points", "summary", "stuck"]

    if any(w in msg for w in empathy_words):
        return "empathetic"
    if any(w in msg for w in casual_words) and len(msg.split()) < 6:
        return "casual"
    if any(w in msg for w in cheat_words):
        return "cheat_sheet"
    if any(w in msg for w in direct_words):
        return "direct"
    return "socratic"

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.title("🎯 FocusFlow")
    st.caption("AI-Powered Study Assistant")

    st.divider()

    # --- API Settings ---
    with st.expander("⚙️ API Settings", expanded=not bool(st.session_state.api_key)):
        provider = st.radio("Provider", ["OpenRouter (Free)", "Google AI Studio"],
                            index=0 if st.session_state.api_provider == "openrouter" else 1)
        st.session_state.api_provider = "openrouter" if "OpenRouter" in provider else "google"

        key_input = st.text_input(
            "API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder="sk-or-v1-... or AIzaSy...",
        )
        if key_input != st.session_state.api_key:
            st.session_state.api_key = key_input

        if st.session_state.api_provider == "openrouter":
            st.caption("Get free key → [openrouter.ai/keys](https://openrouter.ai/keys)")
        else:
            st.caption("Get key → [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)")

    st.divider()

    # --- Subject Selector ---
    st.markdown("### 📚 Subject")
    selected = st.selectbox("Choose subject", SUBJECTS,
                             index=SUBJECTS.index(st.session_state.current_subject))
    if selected != st.session_state.current_subject:
        st.session_state.current_subject = selected
        st.rerun()

    if selected not in st.session_state.messages:
        st.session_state.messages[selected] = []

    st.divider()

    # ============================================================
    # POMODORO TIMER — WORKING WITH JAVASCRIPT
    # ============================================================
    st.markdown("### ⏱️ Focus Timer")

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
            st.session_state.sessions_today += 1
            st.session_state.pomodoro_end = None
            st.balloons()
            st.success("🎉 25 min done! Take a 5 min break.")
            st.rerun()
        else:
            mins, secs = divmod(total_seconds, 60)

            st.markdown(f"""
            <div style="text-align: center; margin: 12px 0;">
                <div id="pomodoro-timer" style="
                    font-size: 36px;
                    font-weight: bold;
                    color: #FF6600;
                    font-family: monospace;
                    letter-spacing: 2px;
                ">{mins:02d}:{secs:02d}</div>
                <div style="font-size: 12px; color: #888; margin-top: 4px;">Focus session in progress 🔥</div>
            </div>

            <script>
                (function() {{
                    let totalSeconds = {total_seconds};
                    const timerEl = document.getElementById('pomodoro-timer');
                    if (!timerEl) return;

                    const tick = setInterval(function() {{
                        totalSeconds--;
                        if (totalSeconds <= 0) {{
                            clearInterval(tick);
                            timerEl.innerHTML = "00:00 ✅";
                            timerEl.style.color = "#4CAF50";
                            // Trigger Streamlit rerun to show celebration
                            setTimeout(function() {{
                                window.parent.postMessage({{type: 'streamlit:run'}}, '*');
                            }}, 800);
                        }} else {{
                            const m = Math.floor(totalSeconds / 60);
                            const s = totalSeconds % 60;
                            timerEl.innerHTML =
                                (m < 10 ? '0' : '') + m + ':' +
                                (s < 10 ? '0' : '') + s;
                        }}
                    }}, 1000);
                }})();
            </script>
            """, unsafe_allow_html=True)
    else:
        st.caption("Start a 25-minute Pomodoro session 🍅")

    st.divider()

    # --- Stats ---
    st.markdown("### 📊 My Stats")
    col1, col2 = st.columns(2)
    col1.metric("Focus Time", f"{st.session_state.total_study_minutes} min")
    col2.metric("Sessions", st.session_state.sessions_today)

    st.divider()

    # --- Clear chat ---
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages[st.session_state.current_subject] = []
        st.session_state.last_response_was_question = False
        st.rerun()

# ============================================================
# MAIN CHAT AREA
# ============================================================
subject = st.session_state.current_subject

st.title(f"📖 {subject}")
st.caption("Ask anything — I'll guide you step by step using the Socratic method.")

# Show chat history
chat_history = st.session_state.messages.get(subject, [])
for msg in chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# "Stuck?" button — appears after a Socratic question
if st.session_state.last_response_was_question and chat_history:
    if st.button("🆘 Stuck? Get a cheat sheet", key="stuck_btn"):
        st.session_state.pending_ai_request = "cheat_sheet"
        st.session_state.last_response_was_question = False
        st.rerun()

# Process pending AI request (from "Stuck?" button)
if st.session_state.pending_ai_request:
    intent = st.session_state.pending_ai_request
    st.session_state.pending_ai_request = None
    with st.chat_message("assistant"):
        with st.spinner("Generating cheat sheet..."):
            response = get_ai_response("Give me a cheat sheet for what we just discussed.", subject, intent)
        st.markdown(response)
    st.session_state.messages[subject].append({"role": "assistant", "content": response})
    st.session_state.last_response_was_question = False
    st.rerun()

# Chat input
user_input = st.chat_input(f"Ask about {subject}...")

if user_input:
    # Add user message to history
    if subject not in st.session_state.messages:
        st.session_state.messages[subject] = []
    st.session_state.messages[subject].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Check if timer expired during this interaction
    if st.session_state.pomodoro_active and st.session_state.pomodoro_end:
        if datetime.now() >= st.session_state.pomodoro_end:
            st.session_state.pomodoro_active = False
            st.session_state.total_study_minutes += 25
            st.session_state.sessions_today += 1
            st.session_state.pomodoro_end = None
            st.balloons()
            st.success("🎉 25 min done! Take a 5 min break.")

    # Detect intent and get AI response
    intent = detect_intent(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_ai_response(user_input, subject, intent)
        st.markdown(response)

    st.session_state.messages[subject].append({"role": "assistant", "content": response})

    # Track if response ends with a question (for "Stuck?" button)
    st.session_state.last_response_was_question = (
        intent == "socratic" and response.strip().endswith("?")
    )

    st.rerun()
