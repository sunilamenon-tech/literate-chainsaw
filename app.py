import streamlit as st
import requests
from datetime import date, datetime, timedelta
import json
import base64
import time

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
    .parent-card {
        background: white;
        border: 1px solid #F0E6D3;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
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
api_config    = None
vision_config = None

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
            api_config = {"provider": "google", "key": key, "model": "gemini-flash-latest", "url": None}
    except: pass

try:
    key = st.secrets["GOOGLE_API_KEY"]
    if key and len(key) > 10:
        vision_config = {"provider": "google", "key": key, "model": "gemini-flash-latest"}
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
    "parent_analysis": None,
    "app_mode": "🎓 Student",
    # ── Mistake Journal (new) ──
    "mistake_log": [],        # list of individual mistake entries, newest last
    "mistake_clusters": {},   # key -> {count, severity, topic, error_type, last_date, resolved}
    # ── Timed Mock Tests (new) ──
    "mock_test_active": None,     # dict describing the in-progress test, or None
    "mock_test_history": [],      # list of completed test result dicts
    "mock_test_last_result": None,  # most recently completed test, for showing analytics
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


def call_api_large(messages_list, system_prompt, max_tokens=4000):
    """Same as call_api, but with a higher token ceiling for outputs that need more room
    (e.g. a 20-30 question mock test with explanations). Kept as a separate function so
    call_api itself — used everywhere else — is never touched."""
    provider = api_config["provider"]
    model = api_config["model"]
    try:
        if provider == "groq":
            msgs = [{"role": "system", "content": system_prompt}] + messages_list
            payload = {"model": model, "messages": msgs, "temperature": 0.5, "max_tokens": max_tokens}
            headers = {"Authorization": f"Bearer {api_config['key']}", "Content-Type": "application/json"}
            r = requests.post(api_config["url"], json=payload, headers=headers, timeout=60).json()
            if 'choices' in r and r['choices']:
                return r['choices'][0]['message']['content']
            return f"⚠️ Error: {r.get('error', {}).get('message', 'Unknown')}"

        elif provider == "openrouter":
            msgs = [{"role": "system", "content": system_prompt}] + messages_list
            payload = {"model": model, "messages": msgs, "temperature": 0.5, "max_tokens": max_tokens}
            headers = {"Authorization": f"Bearer {api_config['key']}", "Content-Type": "application/json",
                       "HTTP-Referer": "https://focusflow.app", "X-Title": "FocusFlow"}
            r = requests.post(api_config["url"], json=payload, headers=headers, timeout=60).json()
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
            payload = {"contents": google_msgs, "generationConfig": {"temperature": 0.5, "maxOutputTokens": max_tokens}}
            r = requests.post(url, json=payload, timeout=60).json()
            if 'candidates' in r and r['candidates']:
                return r['candidates'][0]['content']['parts'][0]['text']
            return f"⚠️ Error: {r.get('error', {}).get('message', 'Unknown')}"

    except Exception as e:
        return f"❌ Error: {str(e)}"


def extract_json_object(text):
    """Small shared helper for the new features — strips markdown fences and pulls out
    the {...} span before parsing. Existing JSON-extraction code elsewhere (Parent Analyzer,
    mistake classifier) is left exactly as-is; this is only used by new code."""
    clean = text.strip().replace("```json", "").replace("```", "").strip()
    first_brace = clean.find("{")
    last_brace  = clean.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        clean = clean[first_brace:last_brace + 1]
    return json.loads(clean)

# ============================================================
# PARENT TEST ANALYZER
# ============================================================

PARENT_SYSTEM_PROMPT = """You are FocusFlow's Parent Test Analyzer for Indian school students.
Analyze the uploaded test paper carefully — read every question and every answer the student wrote.
Return ONLY a valid JSON object. No markdown fences, no preamble, no extra text.

JSON structure:
{
  "subject": "Mathematics",
  "grade": "Class 9",
  "totalMarks": 40,
  "marksObtained": 26,
  "percentage": 65,
  "overallSummary": "2-3 sentence honest assessment of the student's performance",

  "questionBreakdown": [
    {
      "qNo": "Q1",
      "topic": "Irrational Numbers",
      "marksAllotted": 1,
      "marksObtained": 1,
      "status": "correct",
      "errorType": null,
      "specificMistake": null
    },
    {
      "qNo": "Q3",
      "topic": "Algebraic Identities",
      "marksAllotted": 1,
      "marksObtained": 0,
      "status": "wrong",
      "errorType": "Misread Question",
      "specificMistake": "Student answered B) 58 which is actually the correct value — most likely misread the options or circled the wrong one by mistake"
    },
    {
      "qNo": "Q6",
      "topic": "Algebraic Expressions",
      "marksAllotted": 2,
      "marksObtained": 1,
      "status": "partial",
      "errorType": "Sign Error",
      "specificMistake": "Did not distribute the negative sign correctly — wrote 9x²+12x+4 − 9x²−12x+4 instead of 9x²+12x+4 − (9x²−12x+4)"
    },
    {
      "qNo": "Q8",
      "topic": "Polynomials",
      "marksAllotted": 2,
      "marksObtained": 0,
      "status": "unattempted",
      "errorType": "Unattempted",
      "specificMistake": "Left completely blank — no working shown"
    }
  ],

  "errorSummary": [
    {
      "errorType": "Misread Question",
      "marksLost": 1,
      "questions": ["Q3"],
      "description": "Student knew the answer but marked wrong option"
    },
    {
      "errorType": "Sign Error",
      "marksLost": 1,
      "questions": ["Q6"],
      "description": "Negative sign not distributed properly in bracket expansion"
    },
    {
      "errorType": "Wrong Formula Applied",
      "marksLost": 3,
      "questions": ["Q10"],
      "description": "Used (a+b+c)² + 2(ab+bc+ca) instead of minus"
    },
    {
      "errorType": "Unattempted",
      "marksLost": 2,
      "questions": ["Q8"],
      "description": "Question left blank"
    },
    {
      "errorType": "Topic Avoidance",
      "marksLost": 8,
      "questions": ["Q11"],
      "description": "Graph-based question skipped entirely — possible topic anxiety"
    },
    {
      "errorType": "Presentation Error",
      "marksLost": 1,
      "questions": ["Q12"],
      "description": "Working fully correct but final answer not boxed/highlighted"
    }
  ],

  "strongAreas": [
    {"topic": "Proof Writing", "evidence": "Q9 fully correct — irrational number proof done perfectly"},
    {"topic": "Factorization", "evidence": "Q5 correct — factorized x²+5x+6 accurately"}
  ],

  "weakAreas": [
    {"topic": "Algebraic Identities", "rootCause": "Uses wrong formula — adds instead of subtracts in (a+b+c)² expansion", "severity": "high"},
    {"topic": "Linear Graphs", "rootCause": "Consistently avoids graph-based questions — possible topic anxiety or lack of practice", "severity": "high"},
    {"topic": "Sign Rules in Brackets", "rootCause": "Does not distribute negative sign when expanding brackets", "severity": "medium"}
  ],

  "rootCauseSummary": "The core issues are two specific gaps: wrong identity formulas (adds when should subtract) and complete avoidance of graph questions. Sign errors in bracket expansion are a secondary pattern worth addressing.",

  "sevenDayPlan": [
    {"day": 1, "topic": "Algebraic Identities", "activity": "Rewrite all 8 standard identities with examples, focus on (a+b+c)²", "duration": "30 min"},
    {"day": 2, "topic": "Identity Practice", "activity": "Solve 15 problems applying key identities — self check each answer", "duration": "30 min"},
    {"day": 3, "topic": "Sign Rules in Brackets", "activity": "10 bracket expansion problems focusing only on negative sign distribution", "duration": "25 min"},
    {"day": 4, "topic": "Linear Equations — Table Method", "activity": "Plot 3 linear equations step by step using table of values", "duration": "35 min"},
    {"day": 5, "topic": "Graph Intersection", "activity": "Find intersection points of 2 pairs of lines from their graphs", "duration": "30 min"},
    {"day": 6, "topic": "Mixed Practice", "activity": "5 identity questions + 2 graph questions — timed 20 minutes", "duration": "25 min"},
    {"day": 7, "topic": "Mini Checkpoint", "activity": "8 questions covering only weak areas — self evaluate strictly", "duration": "25 min"}
  ],

  "checkpointTestFocus": ["Algebraic Identities (4 Qs)", "Linear Graphs (3 Qs)", "Sign Errors in Brackets (2 Qs)"],

  "parentTip": "One specific actionable tip the parent can do at home to support this child"
}

CRITICAL RULES:
- Include ALL questions in questionBreakdown — both correct and incorrect ones
- status must be one of: "correct", "wrong", "partial", "unattempted"
- errorType for wrong/partial questions: use ANY label that fits best — do NOT limit to a fixed list.
  Examples: "Misread Question", "Wrong Formula Applied", "Sign Error", "Unattempted",
  "Topic Avoidance", "Calculation Slip", "Incomplete Steps", "Presentation Error",
  "Conceptual Gap", "Rushed Answer", "Copied Wrong Value", "Unit Error",
  "Skipped Steps", "Memory Error", "Overconfidence Error" — or invent a better label.
- specificMistake must name the EXACT error in that specific question — not a generic description
- severity must be: "high", "medium", or "low"
- Always return exactly 7 days in sevenDayPlan
- Return ONLY the JSON object, nothing else"""


def run_parent_analysis(child_name, child_grade, child_subject, extra_notes, uploaded_file):
    """Call the AI API with test paper and return parsed JSON analysis.
    Uses Google Vision if available — reads the image/PDF directly.
    Falls back to Groq text-only if no vision key present.
    """
    context_line = (
        f"Student: {child_name or 'Unknown'}, "
        f"Grade: {child_grade or 'Unknown'}, "
        f"Subject: {child_subject or 'Unknown'}. "
        f"{'Extra context: ' + extra_notes if extra_notes else ''}"
    )

    # ── Google Vision path — actually reads the image/PDF ──
    if vision_config and uploaded_file is not None:
        file_bytes = uploaded_file.read()
        b64        = base64.b64encode(file_bytes).decode()
        media_type = uploaded_file.type

        parts = []
        if media_type.startswith("image"):
            parts.append({"inlineData": {"mimeType": media_type, "data": b64}})
        else:
            parts.append({"inlineData": {"mimeType": "application/pdf", "data": b64}})

        parts.append({"text": (
            f"{context_line}\n\n"
            f"This is the student's actual test paper. "
            f"Read every single question carefully. "
            f"Read exactly what the student wrote as their answer. "
            f"For each question: identify the question number, topic, marks allotted, "
            f"what the student wrote, whether it is correct/wrong/partial/unattempted, "
            f"and the SPECIFIC mistake if wrong. "
            f"Do not generalise — be precise about each question."
        )})

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{vision_config['model']}:generateContent?key={vision_config['key']}"
        )
        payload = {
            "contents": [{"role": "user", "parts": parts}],
            "systemInstruction": {"parts": [{"text": PARENT_SYSTEM_PROMPT}]},
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 8000}
        }

        # ── Retry with backoff for transient errors (503 overload, 429 rate limit) ──
        MAX_RETRIES   = 3
        RETRY_DELAYS  = [3, 8, 15]  # seconds, increasing backoff
        last_error    = None
        result_text   = None

        for attempt in range(MAX_RETRIES):
            r = requests.post(url, json=payload, timeout=90).json()

            if "candidates" in r and r["candidates"]:
                candidate     = r["candidates"][0]
                finish_reason = candidate.get("finishReason", "")
                if "content" not in candidate or "parts" not in candidate["content"]:
                    raise Exception(
                        f"Gemini stopped before producing output (finishReason: {finish_reason}). "
                        f"Try a clearer photo or fewer questions."
                    )
                result_text = candidate["content"]["parts"][0]["text"]
                if finish_reason == "MAX_TOKENS":
                    raise Exception(
                        "The response was cut off because it got too long (too many questions). "
                        "Try uploading a shorter test paper, or split it into sections."
                    )
                break  # success — exit retry loop

            else:
                error_info = r.get("error", {})
                error_code = error_info.get("code", 0)
                error_msg  = error_info.get("message", str(r))
                last_error = f"Google Vision API error: {error_info or r}"

                # Only retry on transient errors: 503 (overloaded) or 429 (rate limited)
                is_transient = error_code in (503, 429)
                if is_transient and attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAYS[attempt]
                    st.toast(
                        f"⏳ Google's AI is busy — retrying in {delay}s "
                        f"(attempt {attempt + 1}/{MAX_RETRIES})...",
                        icon="🔄"
                    )
                    time.sleep(delay)
                    continue
                else:
                    raise Exception(last_error)

        if result_text is None:
            raise Exception(last_error or "Unknown error — no response from Gemini after retries.")

    # ── Groq text-only fallback ──
    else:
        if uploaded_file is not None:
            prompt = (
                f"{context_line}\n\n"
                f"A test paper was uploaded (filename: {uploaded_file.name}) "
                f"but direct image reading is not available. "
                f"Generate a thorough and specific diagnostic analysis based on "
                f"the subject, grade, and context. Include realistic per-question breakdown "
                f"with specific mistake descriptions for each question."
            )
        else:
            prompt = (
                f"{context_line}\n\n"
                f"No file uploaded. Generate a realistic and specific diagnostic analysis "
                f"based on the subject and grade. Include a realistic per-question breakdown."
            )
        result_text = call_api(
            [{"role": "user", "content": prompt}],
            PARENT_SYSTEM_PROMPT
        )

    # ── Robust JSON extraction ──
    clean = result_text.strip().replace("```json", "").replace("```", "").strip()
    # If there's stray text before/after the JSON object, extract just the {...} block
    first_brace = clean.find("{")
    last_brace  = clean.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        clean = clean[first_brace:last_brace + 1]
    try:
        data = json.loads(clean)
    except json.JSONDecodeError as e:
        # Surface the raw text so we can see what went wrong instead of a blind failure
        raise Exception(
            f"Could not parse AI response as JSON ({str(e)}). "
            f"Raw response started with: {clean[:300]}"
        )
    return data


def sync_weak_areas_to_student(data):
    """Push weak areas from parent analysis into student's weak_areas session state."""
    subject_tag  = data.get("subject", "General")
    synced_count = 0
    for area in data.get("weakAreas", []):
        topic    = area.get("topic", "Unknown")
        severity = area.get("severity", "medium")
        weight   = {"high": 3, "medium": 2, "low": 1}.get(severity, 1)
        key      = f"{subject_tag}: {topic}"
        st.session_state.weak_areas[key] = (
            st.session_state.weak_areas.get(key, 0) + weight
        )
        synced_count += 1
    return synced_count


def render_parent_results(data, child_name=""):
    """Render the full analysis results — question-by-question breakdown."""

    name_label = child_name or "Student"
    pct        = data.get("percentage", 0)
    obtained   = data.get("marksObtained", 0)
    total      = data.get("totalMarks", 100)

    # Score banner
    score_color      = "#E8F5E9" if pct >= 75 else "#FFF3E0" if pct >= 50 else "#FFEBEE"
    score_border     = "#2E7D32" if pct >= 75 else "#E65100" if pct >= 50 else "#C62828"
    score_text_color = "#2E7D32" if pct >= 75 else "#E65100" if pct >= 50 else "#C62828"

    st.markdown(
        f"<div style='background:{score_color};border-left:5px solid {score_border};"
        f"padding:18px 20px;border-radius:12px;margin-bottom:16px'>"
        f"<span style='font-size:32px;font-weight:800;color:{score_text_color}'>{pct}%</span>"
        f"&nbsp;&nbsp;<span style='color:#546E7A;font-size:15px'>{obtained}/{total} marks"
        f" &nbsp;·&nbsp; {data.get('subject','')} &nbsp;·&nbsp; {data.get('grade','')}</span>"
        f"<br><br><span style='color:#37474F;font-size:14px;line-height:1.6'>"
        f"{data.get('overallSummary','')}</span></div>",
        unsafe_allow_html=True
    )

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Question Breakdown", "🔍 Root Cause", "📅 7-Day Plan", "💌 Parent Tip"
    ])

    # Status config
    STATUS_CONFIG = {
        "correct":     ("#E8F5E9", "#2E7D32", "✅"),
        "wrong":       ("#FFEBEE", "#C62828", "❌"),
        "partial":     ("#FFF3E0", "#E65100", "⚠️"),
        "unattempted": ("#E3F2FD", "#1565C0", "⏭️"),
    }

    # Dynamic badge color based on error type
    def badge_color(error_type):
        et = (error_type or "").lower()
        if any(x in et for x in ["unattempted", "avoidance", "blank"]):
            return "#E3F2FD", "#1565C0"
        if any(x in et for x in ["sign", "calculation", "slip", "arithmetic"]):
            return "#F3E5F5", "#6A1B9A"
        if any(x in et for x in ["concept", "formula", "wrong formula", "memory"]):
            return "#FFEBEE", "#C62828"
        if any(x in et for x in ["misread", "rushed", "overconfidence", "careless"]):
            return "#FFF8E1", "#F57F17"
        if any(x in et for x in ["presentation", "incomplete", "skipped steps"]):
            return "#ECEFF1", "#37474F"
        return "#FFF3E0", "#E65100"

    # ════════════════════════════════════════════════════
    # TAB 1 — QUESTION BREAKDOWN
    # ════════════════════════════════════════════════════
    with tab1:
        questions = data.get("questionBreakdown", [])
        wrong_qs  = [q for q in questions if q.get("status") != "correct"]
        right_qs  = [q for q in questions if q.get("status") == "correct"]

        # Error summary pills
        error_summary = data.get("errorSummary", [])
        if error_summary:
            st.markdown("**Where did the marks go?**")
            pills_html = ""
            PILL_COLORS = [
                ("#FFEBEE","#C62828"), ("#FFF3E0","#E65100"), ("#E3F2FD","#1565C0"),
                ("#F3E5F5","#6A1B9A"), ("#ECEFF1","#37474F"), ("#FFF8E1","#F57F17"),
                ("#E8F5E9","#2E7D32"), ("#FCE4EC","#880E4F"),
            ]
            for idx, err in enumerate(error_summary):
                bg, fg = PILL_COLORS[idx % len(PILL_COLORS)]
                qs_list = ", ".join(err.get("questions", []))
                pills_html += (
                    f"<span style='background:{bg};color:{fg};padding:5px 14px;"
                    f"border-radius:10px;font-size:12px;font-weight:600;"
                    f"margin:3px;display:inline-block'>"
                    f"{err.get('errorType','')} &nbsp;·&nbsp; "
                    f"−{err.get('marksLost',0)} marks &nbsp;·&nbsp; {qs_list}"
                    f"</span>"
                )
            st.markdown(f"<div style='margin-bottom:20px;line-height:2'>{pills_html}</div>",
                        unsafe_allow_html=True)

        # Wrong / partial / unattempted — shown first
        if wrong_qs:
            st.markdown("**❌ Questions that lost marks — with specific mistakes:**")
            for q in wrong_qs:
                status     = q.get("status", "wrong")
                bg, fg, icon = STATUS_CONFIG.get(status, ("#ECEFF1","#37474F","❓"))
                error_type = q.get("errorType") or "Unknown"
                specific   = q.get("specificMistake") or ""
                topic      = q.get("topic") or ""
                m_allot    = q.get("marksAllotted", "?")
                m_got      = q.get("marksObtained", 0)
                badge_bg, badge_fg = badge_color(error_type)

                st.markdown(
                    f"<div style='background:{bg};border-left:4px solid {fg};"
                    f"border-radius:10px;padding:14px 16px;margin-bottom:10px'>"

                    # Top row: Q number + error badge + marks
                    f"<div style='display:flex;justify-content:space-between;"
                    f"align-items:center;margin-bottom:8px'>"
                    f"<div style='display:flex;align-items:center;gap:10px'>"
                    f"<span style='font-weight:800;font-size:16px;color:{fg}'>"
                    f"{icon} {q.get('qNo','')}</span>"
                    f"<span style='background:{badge_bg};color:{badge_fg};font-size:11px;"
                    f"padding:3px 10px;border-radius:8px;font-weight:700'>{error_type}</span>"
                    f"</div>"
                    f"<span style='font-weight:800;color:{fg};font-size:15px'>"
                    f"{m_got}/{m_allot}</span>"
                    f"</div>"

                    # Topic
                    f"<div style='font-size:12px;color:#546E7A;margin-bottom:6px'>"
                    f"📚 {topic}</div>"

                    # Specific mistake
                    + (
                        f"<div style='background:white;border-radius:6px;"
                        f"padding:8px 12px;font-size:13px;color:#37474F;line-height:1.6'>"
                        f"💬 <b>Exact mistake:</b> {specific}</div>"
                        if specific else ""
                    )
                    + "</div>",
                    unsafe_allow_html=True
                )

        st.markdown("")

        # Correct questions — collapsed
        if right_qs:
            with st.expander(f"✅ {len(right_qs)} question(s) answered correctly", expanded=False):
                for q in right_qs:
                    st.markdown(
                        f"<div style='background:#E8F5E9;border-left:3px solid #2E7D32;"
                        f"border-radius:8px;padding:8px 14px;margin-bottom:6px;"
                        f"display:flex;justify-content:space-between;align-items:center'>"
                        f"<span style='font-weight:700;color:#2E7D32'>"
                        f"✅ {q.get('qNo','')}</span>"
                        f"<span style='color:#546E7A;font-size:13px'>{q.get('topic','')}</span>"
                        f"<span style='font-weight:700;color:#2E7D32'>"
                        f"{q.get('marksObtained','')}/{q.get('marksAllotted','')}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )

        st.markdown("")

        # Strong vs Weak areas
        col_s, col_w = st.columns(2)
        with col_s:
            st.markdown("**✅ Strong areas**")
            for a in data.get("strongAreas", []):
                st.markdown(
                    f"<div style='background:#E8F5E9;padding:10px 12px;"
                    f"border-radius:8px;margin-bottom:6px'>"
                    f"<b style='color:#2E7D32'>{a.get('topic')}</b><br>"
                    f"<span style='font-size:12px;color:#546E7A'>{a.get('evidence')}</span></div>",
                    unsafe_allow_html=True
                )
        with col_w:
            st.markdown("**⚠️ Weak areas**")
            for a in data.get("weakAreas", []):
                sev       = a.get("severity","medium")
                sev_bg    = {"high":"#FFEBEE","medium":"#FFF3E0","low":"#E8F5E9"}.get(sev,"#F5F5F5")
                sev_color = {"high":"#C62828","medium":"#E65100","low":"#2E7D32"}.get(sev,"#546E7A")
                st.markdown(
                    f"<div style='background:{sev_bg};padding:10px 12px;"
                    f"border-radius:8px;margin-bottom:6px'>"
                    f"<b style='color:{sev_color}'>{a.get('topic')}</b> "
                    f"<span style='font-size:11px;color:{sev_color}'>({sev} priority)</span></div>",
                    unsafe_allow_html=True
                )

    # ════════════════════════════════════════════════════
    # TAB 2 — ROOT CAUSE
    # ════════════════════════════════════════════════════
    with tab2:
        st.markdown(
            f"<div style='background:#FFF8E1;border-left:4px solid #FFC107;"
            f"padding:14px 16px;border-radius:8px;margin-bottom:16px'>"
            f"<b style='color:#E65100'>🔍 The real diagnosis</b><br><br>"
            f"<span style='color:#37474F;line-height:1.7'>"
            f"{data.get('rootCauseSummary','')}</span></div>",
            unsafe_allow_html=True
        )

        for a in data.get("weakAreas", []):
            sev       = a.get("severity","medium")
            sev_bg    = {"high":"#FFEBEE","medium":"#FFF3E0","low":"#E8F5E9"}.get(sev,"#F5F5F5")
            sev_color = {"high":"#C62828","medium":"#E65100","low":"#2E7D32"}.get(sev,"#546E7A")
            st.markdown(
                f"<div style='background:white;border:1px solid #F0E6D3;"
                f"border-radius:12px;padding:14px 16px;margin-bottom:10px'>"
                f"<div style='display:flex;justify-content:space-between;"
                f"align-items:center;margin-bottom:8px'>"
                f"<b style='font-size:15px'>{a.get('topic')}</b>"
                f"<span style='background:{sev_bg};color:{sev_color};font-size:11px;"
                f"padding:3px 10px;border-radius:10px;font-weight:600'>{sev} priority</span></div>"
                f"<span style='color:#546E7A;font-size:14px'>"
                f"💡 <b>Root cause:</b> {a.get('rootCause')}</span></div>",
                unsafe_allow_html=True
            )

        st.markdown("**🎯 Checkpoint test after 7 days — focus only on:**")
        chips = " ".join([
            f"<span style='background:#E3F2FD;color:#1565C0;padding:5px 14px;"
            f"border-radius:10px;font-size:13px;margin-right:6px;display:inline-block'>{t}</span>"
            for t in data.get("checkpointTestFocus", [])
        ])
        st.markdown(f"<div style='margin:8px 0'>{chips}</div>", unsafe_allow_html=True)
        st.caption("Test only these topics after Day 7 — not a broad general test. This tells you exactly if the weakness was fixed.")

    # ════════════════════════════════════════════════════
    # TAB 3 — 7-DAY PLAN
    # ════════════════════════════════════════════════════
    with tab3:
        st.markdown(
            f"Targeted plan for **{name_label}** — focused on specific weak areas, not generic revision."
        )
        st.markdown("")
        for day in data.get("sevenDayPlan", []):
            day_num = day.get("day","")
            label   = f"Day {day_num} — {day.get('topic','')}  ·  {day.get('duration','')}"
            with st.expander(label, expanded=(day_num == 1)):
                st.write(day.get("activity",""))

        st.markdown("")
        st.markdown(
            "<div style='background:#E8F5E9;border:1px solid #A5D6A7;"
            "border-radius:10px;padding:14px 16px'>"
            "<b style='color:#2E7D32'>✅ After Day 7</b><br>"
            "<span style='color:#546E7A;font-size:13px'>Run a mini checkpoint test focused "
            "only on the weak areas identified above. If scores improve, the gaps are closed. "
            "If not, repeat Days 1–3.</span></div>",
            unsafe_allow_html=True
        )

    # ════════════════════════════════════════════════════
    # TAB 4 — PARENT TIP
    # ════════════════════════════════════════════════════
    with tab4:
        st.markdown(
            f"<div style='background:#FFF3E0;border:2px solid #FF6600;"
            f"border-radius:16px;padding:24px;text-align:center;margin-bottom:20px'>"
            f"<div style='font-size:48px;margin-bottom:12px'>💌</div>"
            f"<div style='font-weight:700;font-size:16px;color:#1A1A1A;margin-bottom:12px'>"
            f"A note for you, as a parent</div>"
            f"<p style='font-size:15px;color:#37474F;line-height:1.7;margin:0'>"
            f"{data.get('parentTip','')}</p></div>",
            unsafe_allow_html=True
        )

        st.markdown("**🔗 Student profile sync status**")
        subject = data.get("subject","")
        synced  = {k: v for k, v in st.session_state.weak_areas.items() if subject in k}
        if synced:
            st.success(
                f"✅ {len(synced)} weak area(s) synced to the student's FocusFlow profile. "
                f"Daily challenges will now focus on these topics."
            )
            chips_html = " ".join([
                f"<span style='background:#FFE4CC;color:#FF6600;padding:3px 10px;"
                f"border-radius:10px;font-size:12px;margin-right:4px'>{k}</span>"
                for k in synced
            ])
            st.markdown(chips_html, unsafe_allow_html=True)
        else:
            st.info("Weak areas will appear here after analysis is complete.")

        st.markdown("")
        summary_text = (
            f"FocusFlow Test Analysis — {name_label}\n"
            f"{'='*50}\n"
            f"Subject: {data.get('subject')} | Grade: {data.get('grade')}\n"
            f"Score: {obtained}/{total} ({pct}%)\n\n"
            f"QUESTION BREAKDOWN:\n" +
            "\n".join([
                f"{q.get('qNo')}: {q.get('status','').upper()} [{q.get('marksObtained','?')}/{q.get('marksAllotted','?')}]"
                + (f" — {q.get('errorType','')} — {q.get('specificMistake','')}" if q.get('status') != 'correct' else "")
                for q in data.get("questionBreakdown", [])
            ]) +
            f"\n\nROOT CAUSE:\n{data.get('rootCauseSummary','')}\n\n"
            f"7-DAY PLAN:\n" +
            "\n".join([
                f"Day {d.get('day')}: {d.get('topic')} — {d.get('activity')}"
                for d in data.get("sevenDayPlan", [])
            ])
        )
        st.download_button(
            "📋 Download Full Analysis",
            data=summary_text,
            file_name=f"focusflow_analysis_{name_label.replace(' ','_')}_{date.today()}.txt",
            mime="text/plain",
            use_container_width=True
        )


def show_parent_analyzer():
    st.markdown("## 👨‍👩‍👧 Parent Test Analyzer")

    uploaded_file = st.file_uploader(
        "📄 Upload test paper (photo or PDF)",
        type=["jpg", "jpeg", "png", "pdf"],
        help="Clear phone photo works great. Google Vision reads the image directly."
    )
    if uploaded_file:
        if uploaded_file.type.startswith("image"):
            st.image(uploaded_file, caption="Uploaded test paper", use_column_width=True)
        else:
            st.success(f"✅ {uploaded_file.name} uploaded successfully")

    st.markdown("")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        child_name    = st.text_input("Child's name",   placeholder="e.g. Arjun")
    with c2:
        child_grade   = st.text_input("Class / Grade",  placeholder="e.g. Class 9")
    with c3:
        child_subject = st.text_input("Subject",        placeholder="e.g. Mathematics")
    with c4:
        extra_notes   = st.text_input("Extra context",  placeholder="e.g. skipped chapter 3")

    st.markdown("")

    if st.button("🔍 Analyze Test Paper", use_container_width=True, type="primary"):
        if not child_subject:
            st.warning("Please enter at least the subject.")
            return

        with st.spinner("Reading the test paper and diagnosing every question..."):
            try:
                data   = run_parent_analysis(child_name, child_grade, child_subject, extra_notes, uploaded_file)
                st.session_state.parent_analysis   = data
                st.session_state.parent_child_name = child_name
                synced = sync_weak_areas_to_student(data)
                st.toast(f"✅ Done! {synced} weak area(s) synced to student profile.", icon="🎯")
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                return

    if st.session_state.parent_analysis:
        st.divider()
        st.markdown("## 📊 Analysis Results")
        render_parent_results(
            st.session_state.parent_analysis,
            st.session_state.get("parent_child_name","")
        )
        st.divider()
        if st.button("🔄 Analyze a Different Test", use_container_width=True):
            st.session_state.parent_analysis   = None
            st.session_state.parent_child_name = ""
            st.rerun()


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
    if any(s in p for s in ["hate", "panic", "scared", "anxious", "frustrated"]):
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
# MISTAKE JOURNAL — classification engine (NEW, additive)
# ============================================================
MISTAKE_CLASSIFY_SYSTEM_PROMPT = """You are FocusFlow's mistake classifier for a student's Socratic practice answers.
Given the diagnostic question that was asked, the student's answer, and the tutor's explanation of
what was right/wrong, classify the mistake. Return ONLY a valid JSON object, no markdown fences, no extra text.

JSON structure:
{
  "errorType": "Conceptual Gap",
  "specificMistake": "One sentence naming the exact misunderstanding, referencing the actual question/answer",
  "severity": "medium"
}

Rules:
- errorType: pick whichever label fits best. Examples: "Conceptual Gap", "Sign Error", "Calculation Slip",
  "Misread Question", "Wrong Formula Applied", "Rushed Answer", "Memory Error", "Unit Error",
  "Incomplete Steps", "Overconfidence Error" — or invent a better one. Keep it 1-3 words.
- specificMistake: name the EXACT misunderstanding shown by this answer, not a generic description.
- severity: "high" (fundamental gap, needs re-teaching), "medium" (partial understanding, needs practice),
  or "low" (likely a one-off slip).
- Return ONLY the JSON object."""


def classify_mistake(question_text, student_answer, tutor_explanation):
    """Call the AI to classify why a Socratic answer was wrong. Returns dict or None on failure."""
    prompt = (
        f"Diagnostic question asked: {question_text}\n\n"
        f"Student's answer: {student_answer}\n\n"
        f"Tutor's explanation of the correct answer: {tutor_explanation[:600]}"
    )
    result = call_api([{"role": "user", "content": prompt}], MISTAKE_CLASSIFY_SYSTEM_PROMPT)
    try:
        clean = result.strip().replace("```json", "").replace("```", "").strip()
        first_brace = clean.find("{")
        last_brace  = clean.rfind("}")
        if first_brace != -1 and last_brace != -1:
            clean = clean[first_brace:last_brace + 1]
        parsed = json.loads(clean)
        if "errorType" in parsed and "severity" in parsed:
            return parsed
    except Exception:
        pass
    return None


def log_mistake(subject, topic, question_text, student_answer, classification):
    """Append to mistake_log and update the aggregated mistake_clusters. Additive only —
    does not touch st.session_state.weak_areas, which keeps working exactly as before."""
    error_type = classification.get("errorType", "Unknown")
    specific   = classification.get("specificMistake", "")
    severity   = classification.get("severity", "medium")

    entry = {
        "date": str(date.today()),
        "subject": subject,
        "topic": topic,
        "question": question_text,
        "student_answer": student_answer,
        "error_type": error_type,
        "specific_mistake": specific,
        "severity": severity,
        "resolved": False,
    }
    st.session_state.mistake_log.append(entry)

    cluster_key = f"{subject}:{topic}:{error_type}"
    cluster = st.session_state.mistake_clusters.get(cluster_key, {
        "subject": subject, "topic": topic, "error_type": error_type,
        "count": 0, "severity": severity, "resolved": False,
    })
    cluster["count"]      += 1
    cluster["severity"]    = severity  # keep most recent severity read
    cluster["last_date"]   = str(date.today())
    cluster["resolved"]    = False     # a fresh mistake reopens a cluster
    st.session_state.mistake_clusters[cluster_key] = cluster


def resolve_mistake_cluster(cluster_key):
    """Mark a cluster resolved — used once micro-retests exist; safe to call now too."""
    if cluster_key in st.session_state.mistake_clusters:
        st.session_state.mistake_clusters[cluster_key]["resolved"] = True


def mistake_badge_color(error_type):
    """Same idea as the Parent Analyzer's badge_color, kept as an independent copy
    so the Parent Analyzer's own function is never touched."""
    et = (error_type or "").lower()
    if any(x in et for x in ["unattempted", "avoidance", "blank"]):
        return "#E3F2FD", "#1565C0"
    if any(x in et for x in ["sign", "calculation", "slip", "arithmetic"]):
        return "#F3E5F5", "#6A1B9A"
    if any(x in et for x in ["concept", "formula", "wrong formula", "memory"]):
        return "#FFEBEE", "#C62828"
    if any(x in et for x in ["misread", "rushed", "overconfidence", "careless"]):
        return "#FFF8E1", "#F57F17"
    if any(x in et for x in ["presentation", "incomplete", "skipped steps"]):
        return "#ECEFF1", "#37474F"
    return "#FFF3E0", "#E65100"


# ============================================================
# TIMED MOCK TESTS + POST-TEST ANALYTICS (NEW, additive)
# ============================================================

def generate_timed_mock_test(subject, exam_goal, num_questions):
    """Generate a full-length MCQ paper via the AI. Returns a list of question dicts."""
    system_prompt = f"""You are FocusFlow's exam-paper generator for {exam_goal} students.
Generate exactly {num_questions} multiple-choice questions for the subject: {subject},
matching the difficulty and style of real {exam_goal} questions.
Return ONLY a valid JSON object. No markdown fences, no preamble, no extra text.

JSON structure:
{{
  "questions": [
    {{
      "id": "Q1",
      "topic": "short topic name",
      "question": "the question text",
      "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "correct_option": "B",
      "explanation": "1-2 sentence explanation of why B is correct"
    }}
  ]
}}

Rules:
- Exactly {num_questions} questions, numbered Q1 to Q{num_questions}
- Cover a spread of topics within {subject}, not just one topic repeated
- Each question must have exactly 4 options (A-D) and exactly one correct_option
- Return ONLY the JSON object"""

    result = call_api_large(
        [{"role": "user", "content": f"Generate {num_questions} {subject} MCQs for {exam_goal}"}],
        system_prompt,
        max_tokens=min(4000 + num_questions * 60, 8000)
    )
    data = extract_json_object(result)
    questions = data.get("questions", [])
    if not questions:
        raise Exception("No questions were generated — please try again.")
    return questions


def _mt_record_time(qid):
    """on_change callback for each question's radio — approximates time spent per question
    as the gap between consecutive answer selections."""
    active = st.session_state.get("mock_test_active")
    if not active:
        return
    now  = time.time()
    last = active.get("last_interaction_time", active["start_time"])
    active["question_times"][qid] = active["question_times"].get(qid, 0) + max(now - last, 0)
    active["last_interaction_time"] = now


def finish_mock_test():
    """Score the active test, log every wrong answer into the mistake journal
    (reusing classify_mistake / log_mistake exactly as built in Step 1), and store results."""
    active = st.session_state.mock_test_active
    if not active:
        return
    tid       = active["test_id"]
    questions = active["questions"]
    neg       = active["negative_marking"]
    marks_correct = 4
    marks_wrong   = -1 if neg else 0

    breakdown, topic_time = [], {}
    total_obtained = total_max = 0
    correct_count = wrong_count = unattempted_count = 0

    for idx, q in enumerate(questions):
        qid         = q.get("id", f"Q{idx+1}")
        options     = q.get("options", {})
        correct_opt = q.get("correct_option", "")
        topic       = q.get("topic", "General")
        key         = f"mt_{tid}_{qid}"

        selected_label = st.session_state.get(key, "— Not answered —")
        selected_opt = None
        if selected_label and selected_label != "— Not answered —":
            selected_opt = selected_label.split(")")[0].strip()

        total_max += marks_correct
        t_spent = round(active["question_times"].get(qid, 0), 1)
        topic_time[topic] = round(topic_time.get(topic, 0) + t_spent, 1)

        if selected_opt is None:
            status, marks = "unattempted", 0
            unattempted_count += 1
        elif selected_opt == correct_opt:
            status, marks = "correct", marks_correct
            correct_count += 1
        else:
            status, marks = "wrong", marks_wrong
            wrong_count += 1

        total_obtained += marks
        breakdown.append({
            "id": qid, "topic": topic, "status": status,
            "selected": selected_opt, "correct_option": correct_opt,
            "time_spent": t_spent, "marks": marks,
            "question": q.get("question", ""), "explanation": q.get("explanation", ""),
        })

        # Feed the mistake journal — same functions used by Socratic mode, untouched.
        if status == "wrong":
            try:
                classification = classify_mistake(
                    q.get("question", ""),
                    f"Selected {selected_opt}) {options.get(selected_opt, '')}",
                    f"Correct answer is {correct_opt}) {options.get(correct_opt, '')}. {q.get('explanation', '')}"
                )
                if classification:
                    log_mistake(active["subject"], topic, q.get("question", ""), selected_label, classification)
            except Exception:
                pass

    attempted = correct_count + wrong_count
    accuracy  = round((correct_count / attempted) * 100, 1) if attempted > 0 else 0

    result = {
        "test_id": tid, "subject": active["subject"], "exam_goal": active["exam_goal"],
        "date": str(date.today()), "total_questions": len(questions),
        "correct": correct_count, "wrong": wrong_count, "unattempted": unattempted_count,
        "accuracy": accuracy, "marks_obtained": total_obtained, "marks_max": total_max,
        "duration_minutes": active["duration_minutes"],
        "time_used_seconds": round(time.time() - active["start_time"], 1),
        "topic_time": topic_time, "breakdown": breakdown,
    }
    st.session_state.mock_test_history.append(result)
    st.session_state.mock_test_last_result = result
    st.session_state.mock_test_active = None


def render_active_test(active):
    elapsed   = time.time() - active["start_time"]
    remaining = active["duration_minutes"] * 60 - elapsed

    if remaining <= 0:
        st.warning("⏰ Time's up! Auto-submitting your test...")
        finish_mock_test()
        st.rerun()
        return

    mins, secs = divmod(int(remaining), 60)
    st.markdown(f"<div class='streak-badge'>⏱️ {mins:02d}:{secs:02d} remaining</div>", unsafe_allow_html=True)
    st.caption("Timer updates each time you answer a question. Negative marking: "
               + ("ON (-1 per wrong)" if active["negative_marking"] else "OFF"))

    tid = active["test_id"]
    for idx, q in enumerate(active["questions"]):
        qid = q.get("id", f"Q{idx+1}")
        st.markdown(f"**{qid}. {q.get('question','')}**")
        options = q.get("options", {})
        option_labels = ["— Not answered —"] + [f"{k}) {v}" for k, v in options.items()]
        st.radio(
            "Choose answer", option_labels, key=f"mt_{tid}_{qid}",
            label_visibility="collapsed", on_change=_mt_record_time, args=(qid,)
        )
        st.markdown("---")

    if st.button("✅ Submit Test", use_container_width=True, type="primary", key=f"submit_{tid}"):
        finish_mock_test()
        st.rerun()


def render_mock_test_results(result):
    pct = round((result["marks_obtained"] / result["marks_max"]) * 100, 1) if result["marks_max"] else 0
    score_bg = "#E8F5E9" if pct >= 75 else "#FFF3E0" if pct >= 50 else "#FFEBEE"
    score_fg = "#2E7D32" if pct >= 75 else "#E65100" if pct >= 50 else "#C62828"

    st.markdown(
        f"<div style='background:{score_bg};border-left:5px solid {score_fg};"
        f"padding:16px 18px;border-radius:12px;margin-bottom:14px'>"
        f"<span style='font-size:28px;font-weight:800;color:{score_fg}'>"
        f"{result['marks_obtained']}/{result['marks_max']}</span>"
        f"&nbsp;&nbsp;<span style='color:#546E7A;font-size:14px'>({pct}%) · "
        f"{result['subject']} · {result['total_questions']} questions</span></div>",
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("✅ Correct", result["correct"])
    c2.metric("❌ Wrong", result["wrong"])
    c3.metric("⏭️ Unattempted", result["unattempted"])
    c4.metric("🎯 Accuracy", f"{result['accuracy']}%")

    tab1, tab2 = st.tabs(["📋 Question Review", "⏱️ Time Analysis"])

    with tab1:
        for q in result["breakdown"]:
            if q["status"] == "correct":
                bg, fg, icon = "#E8F5E9", "#2E7D32", "✅"
            elif q["status"] == "wrong":
                bg, fg, icon = "#FFEBEE", "#C62828", "❌"
            else:
                bg, fg, icon = "#E3F2FD", "#1565C0", "⏭️"
            st.markdown(
                f"<div style='background:{bg};border-left:4px solid {fg};border-radius:8px;"
                f"padding:10px 14px;margin-bottom:8px'>"
                f"<b style='color:{fg}'>{icon} {q['id']}</b> "
                f"<span style='font-size:12px;color:#546E7A'>· {q['topic']} · {q['time_spent']}s · {q['marks']:+d} marks</span>"
                f"<div style='font-size:13px;color:#37474F;margin-top:4px'>{q['question']}</div>"
                + (f"<div style='font-size:12px;color:#546E7A;margin-top:4px'>💬 {q['explanation']}</div>"
                   if q["status"] != "correct" and q["explanation"] else "")
                + "</div>", unsafe_allow_html=True
            )

    with tab2:
        total_time_used = sum(q["time_spent"] for q in result["breakdown"])
        avg_time = round(total_time_used / len(result["breakdown"]), 1) if result["breakdown"] else 0
        st.markdown(f"**Average time per question:** {avg_time}s &nbsp;·&nbsp; "
                    f"**Allotted:** {result['duration_minutes']} min")

        st.markdown("**Time spent by topic**")
        if result["topic_time"]:
            max_t = max(result["topic_time"].values()) or 1
            for topic, t in sorted(result["topic_time"].items(), key=lambda x: -x[1]):
                width_pct = max(int((t / max_t) * 100), 4)
                st.markdown(
                    f"<div style='margin-bottom:6px'>"
                    f"<span style='font-size:12px;color:#546E7A'>{topic} — {t}s</span>"
                    f"<div style='background:#FFE4CC;border-radius:6px;height:10px;width:{width_pct}%'></div>"
                    f"</div>", unsafe_allow_html=True
                )

        slow_wrong = [q for q in result["breakdown"]
                      if q["status"] == "wrong" and q["time_spent"] > avg_time]
        if slow_wrong:
            st.warning(
                f"⚠️ You spent above-average time on {len(slow_wrong)} question(s) you still got "
                f"wrong ({', '.join(q['id'] for q in slow_wrong)}) — worth reviewing your approach, "
                f"not just the concept."
            )
        fast_wrong = [q for q in result["breakdown"]
                      if q["status"] == "wrong" and q["time_spent"] < avg_time * 0.5]
        if fast_wrong:
            st.info(
                f"💡 {len(fast_wrong)} question(s) were answered quickly but wrong "
                f"({', '.join(q['id'] for q in fast_wrong)}) — possible rushed/careless errors, "
                f"not necessarily a concept gap."
            )


def render_job_landing(current_topic, exam_goal):
    """The new homepage decision, matching the 'Choose a Task' split from the Whimsical flow.
    Pure UI on top of existing session state and actions — no new data model, and every
    button here either points at an existing feature or reuses an existing action exactly."""
    st.markdown("#### What do you need right now?")
    c1, c2, c3 = st.columns(3)

    with c1:
        example_q = SUBJECT_CONTENT.get(current_topic, SUBJECT_CONTENT["Other"])["example_question"]
        st.markdown(
            "<div class='socratic-box'><b>❓ Got a doubt?</b><br>"
            "<span style='font-size:13px'>Type it in the chat box below — I'll check your "
            f"understanding first, then explain fully. Try: \"{example_q}\"</span></div>",
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            "<div class='challenge-box'><b>📝 Want to practice?</b><br>"
            "<span style='font-size:13px'>Quick daily quiz, or a full timed test.</span></div>",
            unsafe_allow_html=True
        )
        pc1, pc2 = st.columns(2)
        with pc1:
            if st.button("🎯 Daily", use_container_width=True, key="land_daily"):
                st.session_state.daily_force_open = True
                st.rerun()
        with pc2:
            if st.button("⏱️ Timed", use_container_width=True, key="land_timed"):
                st.session_state.mt_force_open = True
                st.rerun()

    with c3:
        st.markdown(
            "<div class='cheat-sheet-box'><b>📄 Need quick notes?</b><br>"
            "<span style='font-size:13px'>Instant structured cheat sheet.</span></div>",
            unsafe_allow_html=True
        )
        if st.button("📄 Get Cheat Sheet", use_container_width=True, key="land_notes"):
            p = f"Give me a comprehensive cheat sheet for {current_topic} ({exam_goal})"
            current_messages = st.session_state.threads[st.session_state.current_thread]
            current_messages.append({"role": "user", "content": p, "msg_type": "user_question"})
            st.session_state.pending_ai_request = {
                "prompt": p, "msg_type": "direct", "topic": f"{current_topic} Cheat Sheet"
            }
            st.rerun()


def render_daily_challenge_section(current_topic):
    """Surfaces the Daily Challenge in the main area too, next to the Timed Mock Test.
    Reads/mutates the exact same session_state keys the sidebar already uses — the sidebar
    generates the challenge and is left completely untouched; this is a second place to
    view and complete the same challenge, not a duplicate generator."""
    force_open = st.session_state.get("daily_force_open", False)
    if force_open:
        st.session_state.daily_force_open = False  # consume it — only forces open once
    with st.expander("🎯 Daily Challenge", expanded=force_open):
        if st.session_state.daily_challenge_completed:
            st.markdown(
                "<div class='challenge-complete'>✅ <b>Today's challenge done!</b><br>"
                "🎉 Come back tomorrow for a new one!</div>",
                unsafe_allow_html=True
            )
        elif st.session_state.daily_challenge:
            st.markdown(f"<div class='challenge-box'>{st.session_state.daily_challenge}</div>",
                        unsafe_allow_html=True)
            if st.button("✅ Mark as Complete", use_container_width=True, type="primary",
                         key="mainarea_mark_complete"):
                today = date.today()
                st.session_state.daily_challenge_completed = True
                st.session_state.challenge_streak += 1
                st.session_state.challenge_history.append(
                    {"date": str(today), "subject": current_topic, "completed": True})
                st.balloons()
                st.toast(f"🎉 Challenge done! Streak: {st.session_state.challenge_streak}")
                st.rerun()
        else:
            st.caption("Your Daily Challenge is generating in the sidebar — check back in a moment.")


def render_timed_mock_test_section(exam_goal, current_topic):
    """Top-level entry point for this feature — a self-contained expander, inserted once
    in the Student main area. Doesn't touch the chat code around it."""
    has_active = st.session_state.mock_test_active is not None
    force_open = st.session_state.get("mt_force_open", False)  # NEW: set by the landing cards
    if force_open:
        st.session_state.mt_force_open = False  # consume it — only forces open once
    with st.expander("⏱️ Full-Length Timed Mock Test", expanded=has_active or force_open):
        if st.session_state.mock_test_active is not None:
            render_active_test(st.session_state.mock_test_active)
        elif st.session_state.mock_test_last_result is not None:
            render_mock_test_results(st.session_state.mock_test_last_result)
            if st.button("🔄 Take Another Mock Test", use_container_width=True):
                st.session_state.mock_test_last_result = None
                st.rerun()
        else:
            st.caption("Simulate real exam conditions — timed, with negative marking, "
                       "and full analytics after you submit.")
            c1, c2, c3 = st.columns(3)
            with c1:
                num_q = st.selectbox("Number of questions", [10, 15, 20, 25, 30], index=1, key="mt_num_q")
            with c2:
                duration = st.number_input("Duration (minutes)", min_value=5, max_value=180,
                                            value=num_q * 2, step=5, key="mt_duration")
            with c3:
                neg_marking = st.checkbox("Negative marking (-1/wrong)",
                                           value=(exam_goal in ["JEE Main", "NEET"]), key="mt_neg")
            if st.button("🚀 Start Timed Mock Test", use_container_width=True, type="primary"):
                with st.spinner("Building your test paper..."):
                    try:
                        qs = generate_timed_mock_test(current_topic, exam_goal, num_q)
                        st.session_state.mock_test_active = {
                            "test_id": str(int(time.time())),
                            "subject": current_topic, "exam_goal": exam_goal,
                            "questions": qs, "start_time": time.time(),
                            "last_interaction_time": time.time(),
                            "duration_minutes": duration, "negative_marking": neg_marking,
                            "question_times": {},
                        }
                        st.rerun()
                    except Exception as e:
                        st.error(f"Couldn't generate the test: {e}")


# ============================================================
# MAIN AI RESPONSE
# ============================================================
def get_ai_response(prompt: str, msg_type: str, topic_tag: str):
    days_left  = (st.session_state.test_date - date.today()).days
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
- End EXACTLY with: "Take your time! If you're stuck, click the ⚡ button below 👇"

Format:
Quick check before I explain — [question]?
A) option  B) option  C) option  D) option

Take your time! If you're stuck, click the ⚡ button below 👇"""

    history.append({"role": "user", "content": prompt})
    return call_api(history, system_prompt), msg_type

# ============================================================
# WELCOME CONTENT
# ============================================================
SUBJECT_CONTENT = {
    "Physics":   {"example_concept": "Explain Newton's Laws of Motion",         "example_question": "What is Newton's First Law?"},
    "Chemistry": {"example_concept": "Explain balancing chemical equations",     "example_question": "How do I balance chemical equations?"},
    "Maths":     {"example_concept": "Explain quadratic equations",              "example_question": "How do I solve quadratic equations?"},
    "Biology":   {"example_concept": "Explain Photosynthesis",                   "example_question": "What is photosynthesis?"},
    "English":   {"example_concept": "Explain the theme of 'The Road Not Taken'","example_question": "What is the theme of 'The Road Not Taken'?"},
    "History":   {"example_concept": "Explain the causes of World War I",        "example_question": "What were the main causes of World War I?"},
    "Other":     {"example_concept": "Explain the Pythagorean Theorem",          "example_question": "What is the Pythagorean Theorem?"}
}

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:

    st.markdown("### 👤 Mode")
    app_mode = st.radio(
        "", ["🎓 Student", "👨‍👩‍👧 Parent"],
        horizontal=True, label_visibility="collapsed", key="app_mode"
    )
    st.divider()

    # ── PARENT SIDEBAR ───────────────────────────────────
    if app_mode == "👨‍👩‍👧 Parent":

        st.markdown("### 📋 How it works")
        st.markdown(
            "<div style='background:#FFF3E0;border-left:3px solid #FF6600;"
            "padding:12px 14px;border-radius:8px;font-size:13px;line-height:1.8'>"
            "📄 <b>Step 1</b> — Upload your child's test paper<br>"
            "🧒 <b>Step 2</b> — Enter name, class &amp; subject<br>"
            "✨ <b>Step 3</b> — Get a full diagnosis in seconds"
            "</div>",
            unsafe_allow_html=True
        )
        st.divider()

        st.markdown("### 📊 Last Analysis")
        if st.session_state.parent_analysis:
            d     = st.session_state.parent_analysis
            child = st.session_state.get("parent_child_name", "Student")
            pct   = d.get("percentage", 0)
            sc    = "#2E7D32" if pct >= 75 else "#E65100" if pct >= 50 else "#C62828"
            st.markdown(
                f"<div style='background:white;border:1px solid #F0E6D3;"
                f"border-radius:10px;padding:12px 14px'>"
                f"<div style='font-weight:700;font-size:14px'>{child}</div>"
                f"<div style='font-size:13px;color:#546E7A;margin-top:2px'>"
                f"{d.get('subject','')} &nbsp;·&nbsp; {d.get('grade','')}</div>"
                f"<div style='font-size:22px;font-weight:800;color:{sc};margin-top:6px'>"
                f"{pct}% &nbsp;"
                f"<span style='font-size:13px;font-weight:400;color:#546E7A'>"
                f"{d.get('marksObtained',0)}/{d.get('totalMarks',0)} marks</span></div>"
                f"<div style='font-size:11px;color:#9E9E9E;margin-top:4px'>"
                f"Analyzed on {date.today().strftime('%d %b %Y')}</div></div>",
                unsafe_allow_html=True
            )
        else:
            st.caption("No analysis run yet. Upload a test paper to get started.")

        st.divider()
        st.markdown("### 🔌 AI Status")
        st.success(f"✅ {api_config['provider'].upper()}")
        if vision_config:
            st.success("✅ GOOGLE (Vision)")
            st.caption("PDFs & images: Gemini reads them directly")
        else:
            st.warning("⚠️ No vision API key")
            st.caption("Add GOOGLE_API_KEY to Streamlit secrets for image reading")

    # ── STUDENT SIDEBAR ──────────────────────────────────
    else:
        st.markdown("### 🎯 Your Goal")
        exam_goal = st.selectbox("Exam/Goal",
            ["JEE Main","NEET","10th Boards","12th Boards","UPSC","Other"],
            index=["JEE Main","NEET","10th Boards","12th Boards","UPSC","Other"].index(st.session_state.exam_goal))
        current_topic = st.selectbox("Subject",
            ["Physics","Chemistry","Maths","Biology","English","History","Other"],
            index=["Physics","Chemistry","Maths","Biology","English","History","Other"].index(st.session_state.current_topic))

        if exam_goal == "Other":
            has_date = st.radio("Choose one:",
                ["Yes, I have a test date","No, just learning"],
                index=0 if st.session_state.has_specific_date else 1,
                label_visibility="collapsed")
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
            if days_left <= 3:   st.error(f"🚨 {days_left} days left! CRUNCH MODE")
            elif days_left <= 14: st.warning(f"⏰ {days_left} days left")
            else:                 st.info(f"📅 {days_left} days left")

        if st.button("🔄 Update Context", use_container_width=True):
            st.session_state.exam_goal    = exam_goal
            st.session_state.current_topic = current_topic
            st.session_state.test_date    = test_date
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
            st.session_state.study_streak  += 1
            st.session_state.last_study_date = today
        elif st.session_state.last_study_date != today:
            st.session_state.study_streak   = 1
            st.session_state.last_study_date = today
        st.markdown(f"<div class='streak-badge'>🔥 {st.session_state.study_streak} day streak</div>",
                    unsafe_allow_html=True)

        st.divider()
        st.markdown("### ⚠️ Focus Areas")
        if st.session_state.weak_areas:
            for topic, count in sorted(st.session_state.weak_areas.items(),
                                       key=lambda x: x[1], reverse=True)[:5]:
                st.markdown(f"<span class='weak-area-tag'>{topic} ({count})</span>",
                            unsafe_allow_html=True)
        else:
            st.caption("Keep studying to see your focus areas!")

        # ── Mistake Journal (NEW) ──
        st.divider()
        st.markdown("### 🧾 Mistake Journal")
        active_clusters = {
            k: v for k, v in st.session_state.mistake_clusters.items()
            if not v.get("resolved", False) and v.get("subject") == current_topic
        }
        if active_clusters:
            sev_rank = {"high": 0, "medium": 1, "low": 2}
            sorted_clusters = sorted(
                active_clusters.items(),
                key=lambda kv: (sev_rank.get(kv[1]["severity"], 1), -kv[1]["count"])
            )
            for key, c in sorted_clusters[:5]:
                bg, fg = mistake_badge_color(c["error_type"])
                st.markdown(
                    f"<div style='background:{bg};border-radius:8px;padding:6px 10px;"
                    f"margin-bottom:4px;font-size:12px'>"
                    f"<b style='color:{fg}'>{c['error_type']}</b> · {c['topic']} "
                    f"<span style='color:#9E9E9E'>×{c['count']}</span></div>",
                    unsafe_allow_html=True
                )
            with st.expander("📖 View all logged mistakes"):
                for entry in reversed(st.session_state.mistake_log[-15:]):
                    if entry["subject"] != current_topic:
                        continue
                    st.markdown(
                        f"**{entry['error_type']}** · {entry['topic']}  \n"
                        f"<span style='font-size:12px;color:#546E7A'>{entry['specific_mistake']}</span>",
                        unsafe_allow_html=True
                    )
                    st.caption(entry["date"])
        else:
            st.caption("No mistakes logged yet for this subject — they'll show up here after Socratic answers you get wrong.")

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
        st.markdown("### 🎯 Daily Challenge")
        today = date.today()

        if st.session_state.daily_challenge_date != today:
            st.session_state.daily_challenge          = None
            st.session_state.daily_challenge_completed = False
            st.session_state.daily_challenge_subject   = None

        if (st.session_state.daily_challenge_subject and
                st.session_state.daily_challenge_subject != current_topic):
            st.session_state.daily_challenge          = None
            st.session_state.daily_challenge_completed = False
            st.session_state.daily_challenge_subject   = None

        if st.session_state.daily_challenge_date:
            yesterday = today - timedelta(days=1)
            if (st.session_state.daily_challenge_date == yesterday and
                    not st.session_state.daily_challenge_completed):
                st.session_state.challenge_streak = 0

        if st.session_state.challenge_streak > 0:
            flame = "🔥" * min(st.session_state.challenge_streak, 5)
            st.markdown(
                f"<div class='streak-badge'>{flame} {st.session_state.challenge_streak} day challenge streak!</div>",
                unsafe_allow_html=True)

        if not st.session_state.daily_challenge and not st.session_state.daily_challenge_completed:
            with st.spinner("📝 Generating today's challenge..."):
                challenge_text = generate_daily_challenge(current_topic, exam_goal)
                st.session_state.daily_challenge        = challenge_text
                st.session_state.daily_challenge_date   = today
                st.session_state.daily_challenge_subject = current_topic

        if st.session_state.daily_challenge and not st.session_state.daily_challenge_completed:
            st.markdown(f"<div class='challenge-box'>{st.session_state.daily_challenge}</div>",
                        unsafe_allow_html=True)
            if st.button("✅ Mark as Complete", use_container_width=True, type="primary"):
                st.session_state.daily_challenge_completed = True
                st.session_state.challenge_streak         += 1
                st.session_state.challenge_history.append(
                    {"date": str(today), "subject": current_topic, "completed": True})
                st.balloons()
                st.toast(f"🎉 Challenge done! Streak: {st.session_state.challenge_streak}")
                st.rerun()
        elif st.session_state.daily_challenge_completed:
            st.markdown(
                "<div class='challenge-complete'>✅ <b>Today's challenge done!</b><br>"
                "🎉 Come back tomorrow for a new one!</div>",
                unsafe_allow_html=True)

        if st.session_state.challenge_history:
            st.divider()
            st.markdown("### 📊 This Week")
            this_week = [c for c in st.session_state.challenge_history
                         if datetime.strptime(c["date"],"%Y-%m-%d").date() >= today - timedelta(days=7)]
            done = sum(1 for c in this_week if c["completed"])
            st.markdown(f"✅ **{done}/7** challenges completed this week")

        st.divider()
        if st.button("🗑️ Clear This Chat", use_container_width=True):
            st.session_state.threads[st.session_state.current_thread] = []
            st.session_state.awaiting_answer       = False
            st.session_state.last_socratic_question = None
            st.session_state.original_question      = None
            st.session_state.last_followup_label    = None
            st.session_state.last_followup_prompt   = None
            st.rerun()

        st.session_state._sidebar_exam_goal  = exam_goal
        st.session_state._sidebar_topic      = current_topic
        st.session_state._sidebar_test_date  = test_date

# ============================================================
# MAIN AREA — STUDENT MODE
# ============================================================
if app_mode == "🎓 Student":

    exam_goal     = st.session_state.get("_sidebar_exam_goal",  st.session_state.exam_goal)
    current_topic = st.session_state.get("_sidebar_topic",      st.session_state.current_topic)
    test_date     = st.session_state.get("_sidebar_test_date",  st.session_state.test_date)

    current_messages = st.session_state.threads[st.session_state.current_thread]
    days_left        = (st.session_state.test_date - date.today()).days

    render_job_landing(current_topic, exam_goal)               # NEW — additive, self-contained
    st.divider()
    render_daily_challenge_section(current_topic)              # NEW — additive, self-contained
    render_timed_mock_test_section(exam_goal, current_topic)  # NEW — additive, self-contained
    st.divider()

    for i, message in enumerate(current_messages):
        if message.get("hidden"):
            continue

        msg_type   = message.get("msg_type", "default")
        is_correct = message.get("is_correct", False)
        avatar     = "🧠" if message["role"] == "assistant" else "🧑‍🎓"

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

            if (message["role"] == "assistant" and
                    message.get("msg_type") == "socratic" and
                    not message.get("resolved", False)):
                if st.button("⚡ Stuck? Get the cheat sheet",
                             key=f"stuck_{st.session_state.current_thread}_{i}"):
                    message["resolved"] = True
                    st.session_state.awaiting_answer        = False
                    st.session_state.last_socratic_question  = None
                    weak_key = f"{st.session_state.current_topic}: {message.get('topic','General')}"
                    st.session_state.weak_areas[weak_key] = st.session_state.weak_areas.get(weak_key, 0) + 1
                    trigger = f"[SYSTEM: Student clicked Stuck. Give cheat sheet for: {message.get('topic','topic')}]"
                    current_messages.append({"role":"user","content":trigger,"hidden":True,"msg_type":"system_trigger"})
                    with st.chat_message("assistant", avatar="🧠"):
                        with st.spinner("Generating cheat sheet..."):
                            answer, _ = get_ai_response(trigger, "direct", message.get("topic","General"))
                            current_messages.append({
                                "role":"assistant","content":answer,"msg_type":"cheat_sheet",
                                "topic":message.get("topic","General"),
                                "subject":st.session_state.current_topic,"resolved":True})
                    st.rerun()

            is_last = (i == len(current_messages) - 1)
            if (message["role"] == "assistant" and is_last and
                    msg_type not in ("welcome","socratic","stats") and
                    st.session_state.last_followup_label):
                st.markdown("<div class='followup-btn'>", unsafe_allow_html=True)
                if st.button(st.session_state.last_followup_label, key=f"followup_{i}"):
                    followup_prompt = st.session_state.last_followup_prompt
                    st.session_state.last_followup_label  = None
                    st.session_state.last_followup_prompt = None
                    current_messages.append({"role":"user","content":followup_prompt,"msg_type":"user_question"})
                    with st.chat_message("assistant", avatar="🧠"):
                        with st.spinner("Thinking..."):
                            answer, mt = get_ai_response(followup_prompt, "direct", followup_prompt[:40])
                            current_messages.append({
                                "role":"assistant","content":answer,"msg_type":mt,
                                "subject":st.session_state.current_topic,"resolved":True})
                            label, prompt_s = generate_followup(answer, st.session_state.current_topic)
                            st.session_state.last_followup_label  = label
                            st.session_state.last_followup_prompt = prompt_s
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.pending_ai_request:
        request = st.session_state.pending_ai_request
        st.session_state.pending_ai_request = None
        with st.chat_message("assistant", avatar="🧠"):
            with st.spinner("Thinking..."):
                answer, msg_type = get_ai_response(request["prompt"], request["msg_type"], request["topic"])
                current_messages.append({
                    "role":"assistant","content":answer,"msg_type":msg_type,
                    "topic":request["topic"],"subject":st.session_state.current_topic,
                    "resolved":True,"is_correct":False})
                if msg_type == "socratic":
                    st.session_state.awaiting_answer        = True
                    st.session_state.last_socratic_question  = answer
                else:
                    label, prompt_s = generate_followup(answer, st.session_state.current_topic)
                    st.session_state.last_followup_label  = label
                    st.session_state.last_followup_prompt = prompt_s
        st.rerun()

    if prompt := st.chat_input("Ask a question..."):
        today = date.today()
        if st.session_state.last_study_date != today:
            st.session_state.study_streak   += 1
            st.session_state.last_study_date = today

        current_messages.append({"role":"user","content":prompt,"msg_type":"user_question"})

        user_msgs = [m for m in current_messages if m["role"]=="user" and not m.get("hidden")]
        if len(user_msgs) == 1:
            st.session_state.original_question = prompt

        if st.session_state.awaiting_answer and st.session_state.last_socratic_question:
            intent    = "evaluate_answer"
            socratic_question_full = st.session_state.last_socratic_question  # NEW: kept for mistake journal
            topic_tag = st.session_state.last_socratic_question[:40]
            st.session_state.awaiting_answer        = False
            st.session_state.last_socratic_question  = None
            for msg in reversed(current_messages):
                if msg.get("msg_type") == "socratic" and not msg.get("resolved", False):
                    msg["resolved"] = True
                    break
        else:
            intent    = detect_intent(prompt)
            topic_tag = prompt[:40]
            socratic_question_full = None  # NEW: only relevant for evaluate_answer

        with st.chat_message("assistant", avatar="🧠"):
            with st.spinner("Thinking..."):
                answer, msg_type = get_ai_response(prompt, intent, topic_tag)

                is_correct = False
                if intent == "evaluate_answer":
                    is_correct = check_if_correct(answer)
                    if is_correct:
                        show_clap_celebration()
                    else:
                        # NEW: mistake journal — classify and log the wrong answer, silently.
                        # Wrapped in try/except so a classification failure never breaks the chat.
                        try:
                            classification = classify_mistake(
                                socratic_question_full or topic_tag, prompt, answer
                            )
                            if classification:
                                log_mistake(
                                    st.session_state.current_topic, topic_tag,
                                    socratic_question_full or topic_tag, prompt, classification
                                )
                        except Exception:
                            pass

                if msg_type == "socratic":
                    st.session_state.awaiting_answer        = True
                    st.session_state.last_socratic_question  = answer
                    st.session_state.last_followup_label    = None
                    st.session_state.last_followup_prompt   = None
                else:
                    label, prompt_s = generate_followup(answer, st.session_state.current_topic)
                    st.session_state.last_followup_label  = label
                    st.session_state.last_followup_prompt = prompt_s

                final_msg_type = "evaluate_answer" if intent == "evaluate_answer" else msg_type
                current_messages.append({
                    "role":"assistant","content":answer,
                    "msg_type":final_msg_type,"topic":topic_tag,
                    "subject":st.session_state.current_topic,
                    "resolved":True,"is_correct":is_correct
                })
        st.rerun()

    st.divider()
    qa_col1, qa_col2, qa_col3, qa_col4 = st.columns(4)

    with qa_col1:
        if st.button("📄 Cheat Sheet", use_container_width=True):
            p = f"Give me a comprehensive cheat sheet for {st.session_state.current_topic} ({st.session_state.exam_goal})"
            current_messages.append({"role":"user","content":p,"msg_type":"user_question"})
            st.session_state.pending_ai_request = {"prompt":p,"msg_type":"direct","topic":f"{st.session_state.current_topic} Cheat Sheet"}
            st.rerun()

    with qa_col2:
        if st.button("📝 Mock Test", use_container_width=True):
            p = f"Generate 5 practice questions for {st.session_state.current_topic} ({st.session_state.exam_goal}) with answers and explanations"
            current_messages.append({"role":"user","content":p,"msg_type":"user_question"})
            st.session_state.pending_ai_request = {"prompt":p,"msg_type":"direct","topic":f"{st.session_state.current_topic} Mock Test"}
            st.rerun()

    with qa_col3:
        if st.button("📊 My Stats", use_container_width=True):
            total_msgs  = sum(len(msgs) for msgs in st.session_state.threads.values())
            weak_topics = list(st.session_state.weak_areas.keys())[:3]
            focus_time  = st.session_state.total_study_minutes
            stats_msg   = f"""📊 Your FocusFlow Stats

🔥 **Study Streak:** {st.session_state.study_streak} days
⏱️ **Focus Time:** {focus_time} minutes ({focus_time // 60}h {focus_time % 60}m)
💬 **Total Messages:** {total_msgs}
⚠️ **Focus Areas:** {', '.join(weak_topics) if weak_topics else 'None yet — keep going!'}

Keep crushing it! 🚀"""
            current_messages.append({"role":"assistant","content":stats_msg,"msg_type":"stats","subject":"System"})
            st.rerun()

    with qa_col4:
        if st.button("💾 Export", use_container_width=True):
            chat_text = []
            for msg in current_messages:
                if not msg.get("hidden"):
                    prefix = "🧑‍🎓 You" if msg["role"]=="user" else "🧠 FocusFlow"
                    chat_text.append(f"{prefix}:\n{msg['content']}")
            export_text = (
                f"FocusFlow Chat Export\n{'='*50}\n"
                f"Exam: {st.session_state.exam_goal}\n"
                f"Subject: {st.session_state.current_topic}\n"
                f"Date: {date.today()}\n{'='*50}\n\n"
                + "\n\n---\n\n".join(chat_text)
            )
            st.download_button(
                "📥 Download Chat", export_text,
                file_name=f"focusflow_{st.session_state.current_thread}_{date.today()}.txt",
                mime="text/plain", use_container_width=True
            )

# ============================================================
# MAIN AREA — PARENT MODE
# ============================================================
else:
    show_parent_analyzer()
