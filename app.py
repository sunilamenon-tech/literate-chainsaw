import streamlit as st
import requests
from datetime import date, datetime, timedelta
import random
import json
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
    .loss-card {
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
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
# api_config      → used for student chat (Groq preferred — fast & free)
# vision_config   → used for parent analyzer (Google preferred — reads PDFs/images)
# Both are detected independently so they can run side by side.

api_config    = None   # student chat
vision_config = None   # parent analyzer (vision-capable)

# ── Student chat API (Groq → OpenRouter → Google fallback) ──
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

# ── Vision API for parent analyzer (Google preferred → falls back to text-only) ──
try:
    key = st.secrets["GOOGLE_API_KEY"]
    if key and len(key) > 10:
        vision_config = {"provider": "google", "key": key, "model": "gemini-1.5-pro"}
except: pass

if not vision_config:
    # No vision-capable key found — parent analyzer will work in text-only mode
    vision_config = None

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
# PARENT TEST ANALYZER — HELPER FUNCTIONS
# ============================================================

PARENT_SYSTEM_PROMPT = """You are FocusFlow's Parent Test Analyzer for Indian school students.
Analyze the test paper and return ONLY a valid JSON object. No markdown fences, no preamble, no extra text.

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
      "marks": "1/1",
      "status": "correct",
      "topic": "Irrational Numbers",
      "errorType": null,
      "specificMistake": null
    },
    {
      "qNo": "Q3",
      "marks": "0/1",
      "status": "wrong",
      "topic": "Algebraic Identities",
      "errorType": "Misread Question",
      "specificMistake": "Student answered B) 58 which is actually correct — likely misread or circled wrong option"
    },
    {
      "qNo": "Q6",
      "marks": "1/2",
      "status": "partial",
      "topic": "Algebraic Expressions",
      "errorType": "Sign Error",
      "specificMistake": "Failed to distribute negative sign: wrote 9x²+12x+4 − 9x²−12x+4 instead of distributing the minus"
    },
    {
      "qNo": "Q8",
      "marks": "0/2",
      "status": "unattempted",
      "topic": "Polynomials",
      "errorType": "Unattempted",
      "specificMistake": "Left completely blank"
    }
  ],
  "errorSummary": [
    {"errorType": "Misread Question", "count": 1, "marksLost": 1, "questions": ["Q3"]},
    {"errorType": "Sign Error", "count": 1, "marksLost": 1, "questions": ["Q6"]},
    {"errorType": "Wrong Formula Applied", "count": 1, "marksLost": 3, "questions": ["Q10"]},
    {"errorType": "Unattempted", "count": 2, "marksLost": 10, "questions": ["Q8", "Q11"]},
    {"errorType": "Presentation Error", "count": 1, "marksLost": 1, "questions": ["Q12"]}
  ],
  "strongAreas": [
    {"topic": "Proof Writing", "evidence": "Q9 fully correct — irrational number proof done perfectly"}
  ],
  "weakAreas": [
    {"topic": "Algebraic Identities", "rootCause": "Uses wrong formula — adds instead of subtracts in expansion", "severity": "high"},
    {"topic": "Linear Graphs", "rootCause": "Consistently avoids graph-based questions — possible topic anxiety", "severity": "high"}
  ],
  "rootCauseSummary": "The core issue is not Algebra broadly — it is two specific gaps: wrong identity formulas and avoidance of graph questions.",
  "sevenDayPlan": [
    {"day": 1, "topic": "Algebraic Identities", "activity": "Rewrite and memorise all 8 standard identities with examples", "duration": "30 min"},
    {"day": 2, "topic": "Identity Practice", "activity": "Solve 15 problems applying key identities", "duration": "30 min"},
    {"day": 3, "topic": "Sign Rules", "activity": "10 bracket expansion problems focusing on negative sign distribution", "duration": "25 min"},
    {"day": 4, "topic": "Linear Equations Graph", "activity": "Plot 3 linear equations step by step using table of values method", "duration": "35 min"},
    {"day": 5, "topic": "Graph Reading", "activity": "Find intersection points of pairs of lines from graphs", "duration": "30 min"},
    {"day": 6, "topic": "Mixed Practice", "activity": "5 identity questions + 2 graph questions — timed at 20 minutes", "duration": "25 min"},
    {"day": 7, "topic": "Mini Checkpoint", "activity": "Attempt identity and graph questions only — self-evaluate", "duration": "25 min"}
  ],
  "checkpointTestFocus": ["Algebraic Identities (4 Qs)", "Linear Graphs (3 Qs)", "Sign Errors (2 Qs)"],
  "parentTip": "One specific actionable tip the parent can do at home to support this child"
}

Rules:
- status must be one of: "correct", "wrong", "partial", "unattempted"
- errorType can be ANY specific label — do NOT limit to a fixed list. Use whatever fits best:
  "Misread Question", "Wrong Formula Applied", "Sign Error", "Unattempted", "Topic Avoidance",
  "Calculation Slip", "Incomplete Steps", "Presentation Error", "Conceptual Gap",
  "Rushed Answer", "Copied Wrong Value", "Unit Error", "Skipped Steps", etc.
- severity must be: "high", "medium", or "low"
- Always return exactly 7 days in sevenDayPlan
- Include ALL questions in questionBreakdown — correct and wrong
- Return ONLY the JSON object, nothing else"""


def run_parent_analysis(child_name, child_grade, child_subject, extra_notes, uploaded_file):
    """Call the AI API with test paper context and return parsed JSON analysis.
    Uses Google Vision if available (reads image/PDF directly).
    Falls back to Groq text-only if no vision API key is present.
    """

    context_line = (
        f"Student: {child_name or 'Unknown'}, "
        f"Grade: {child_grade or 'Unknown'}, "
        f"Subject: {child_subject or 'Unknown'}. "
        f"{'Extra context: ' + extra_notes if extra_notes else ''}"
    )

    # ── Path 1: Google Vision — reads the actual image/PDF ──
    if vision_config and uploaded_file is not None:
        file_bytes = uploaded_file.read()
        b64        = base64.b64encode(file_bytes).decode()
        media_type = uploaded_file.type

        # Build Gemini parts
        parts = []
        if media_type.startswith("image"):
            parts.append({"inlineData": {"mimeType": media_type, "data": b64}})
        else:
            parts.append({"inlineData": {"mimeType": "application/pdf", "data": b64}})
        parts.append({"text": (
            f"{context_line}\n\n"
            f"This is the student's actual test paper. Read every question and every answer carefully. "
            f"Identify each question number, what was asked, what the student wrote, "
            f"and whether it is correct, wrong, partial, or unattempted. "
            f"Be specific about the exact mistake in each wrong question."
        )})

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{vision_config['model']}:generateContent?key={vision_config['key']}"
        )
        payload = {
            "contents": [{"role": "user", "parts": parts}],
            "systemInstruction": {"parts": [{"text": PARENT_SYSTEM_PROMPT}]},
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2000}
        }
        r    = requests.post(url, json=payload, timeout=60).json()
        if "candidates" in r and r["candidates"]:
            result_text = r["candidates"][0]["content"]["parts"][0]["text"]
        else:
            raise Exception(f"Google Vision API error: {r.get('error', r)}")

    # ── Path 2: Groq text-only fallback ─────────────────────
    else:
        if uploaded_file is not None:
            prompt = (
                f"{context_line}\n\n"
                f"A test paper was uploaded (filename: {uploaded_file.name}) but direct image "
                f"reading is not available. Generate a thorough and specific diagnostic analysis "
                f"based on the subject, grade, and context. Include realistic per-question breakdown."
            )
        else:
            prompt = (
                f"{context_line}\n\n"
                f"No file uploaded. Generate a realistic and specific diagnostic analysis "
                f"based on the subject and grade provided. Include a realistic per-question breakdown."
            )
        result_text = call_api(
            [{"role": "user", "content": prompt}],
            PARENT_SYSTEM_PROMPT
        )

    # ── Parse JSON safely ────────────────────────────────────
    clean = result_text.strip().replace("```json", "").replace("```", "").strip()
    data  = json.loads(clean)
    return data


def sync_weak_areas_to_student(data):
    """Push weak areas from parent analysis into student's weak_areas session state."""
    subject_tag = data.get("subject", "General")
    synced_count = 0
    for area in data.get("weakAreas", []):
        topic = area.get("topic", "Unknown")
        severity = area.get("severity", "medium")
        weight = {"high": 3, "medium": 2, "low": 1}.get(severity, 1)
        key = f"{subject_tag}: {topic}"
        st.session_state.weak_areas[key] = (
            st.session_state.weak_areas.get(key, 0) + weight
        )
        synced_count += 1
    return synced_count


def render_parent_results(data, child_name=""):
    """Render the full analysis results UI — question-by-question breakdown."""

    name_label = child_name or "Student"
    pct        = data.get("percentage", 0)
    obtained   = data.get("marksObtained", 0)
    total      = data.get("totalMarks", 100)

    # ── Score banner ─────────────────────────────────────
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

    # ── Tabs ─────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Question Breakdown", "🔍 Root Cause", "📅 7-Day Plan", "💌 Parent Tip"])

    STATUS_CONFIG = {
        "correct":     ("#E8F5E9", "#2E7D32", "✅", "Correct"),
        "wrong":       ("#FFEBEE", "#C62828", "❌", "Wrong"),
        "partial":     ("#FFF3E0", "#E65100", "⚠️", "Partial"),
        "unattempted": ("#E3F2FD", "#1565C0", "⏭️", "Not attempted"),
    }

    # ════════════════════════════════════════════════════
    # TAB 1 — QUESTION BREAKDOWN
    # ════════════════════════════════════════════════════
    with tab1:

        questions = data.get("questionBreakdown", [])
        wrong_qs  = [q for q in questions if q.get("status") != "correct"]
        right_qs  = [q for q in questions if q.get("status") == "correct"]

        # Error summary pills at the top
        error_summary = data.get("errorSummary", [])
        if error_summary:
            st.markdown("**Where did the marks go?**")
            pills_html = ""
            PILL_COLORS = [
                ("#FFEBEE","#C62828"), ("#FFF3E0","#E65100"), ("#E3F2FD","#1565C0"),
                ("#F3E5F5","#6A1B9A"), ("#ECEFF1","#37474F"), ("#FFF8E1","#F57F17"),
                ("#E8F5E9","#2E7D32"),
            ]
            for idx, err in enumerate(error_summary):
                bg, fg = PILL_COLORS[idx % len(PILL_COLORS)]
                qs_list = ", ".join(err.get("questions", []))
                pills_html += (
                    f"<span style='background:{bg};color:{fg};padding:5px 12px;"
                    f"border-radius:10px;font-size:12px;font-weight:600;margin:3px;display:inline-block'>"
                    f"{err.get('errorType','')} &nbsp;·&nbsp; "
                    f"−{err.get('marksLost',0)} marks &nbsp;·&nbsp; {qs_list}"
                    f"</span>"
                )
            st.markdown(f"<div style='margin-bottom:16px'>{pills_html}</div>", unsafe_allow_html=True)

        # Wrong / partial questions first
        if wrong_qs:
            st.markdown("**❌ Questions that lost marks:**")
            for q in wrong_qs:
                status = q.get("status", "wrong")
                bg, fg, icon, label = STATUS_CONFIG.get(status, ("#ECEFF1","#37474F","❓","Unknown"))
                error_type    = q.get("errorType") or ""
                specific      = q.get("specificMistake") or ""
                topic         = q.get("topic") or ""
                marks         = q.get("marks","")

                # Error type badge color
                badge_colors = {
                    "Unattempted":         ("#E3F2FD","#1565C0"),
                    "Topic Avoidance":     ("#E3F2FD","#1565C0"),
                    "Sign Error":          ("#F3E5F5","#6A1B9A"),
                    "Calculation Slip":    ("#F3E5F5","#6A1B9A"),
                    "Wrong Formula Applied":("#FFEBEE","#C62828"),
                    "Conceptual Gap":      ("#FFEBEE","#C62828"),
                    "Misread Question":    ("#FFF8E1","#F57F17"),
                    "Presentation Error":  ("#ECEFF1","#37474F"),
                }
                badge_bg, badge_fg = badge_colors.get(error_type, ("#FFF3E0","#E65100"))

                st.markdown(
                    f"<div style='background:{bg};border-left:4px solid {fg};"
                    f"border-radius:10px;padding:12px 16px;margin-bottom:8px'>"
                    f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px'>"
                    f"<span style='font-weight:700;font-size:15px;color:{fg}'>{icon} {q.get('qNo','')}</span>"
                    f"<div style='display:flex;gap:8px;align-items:center'>"
                    f"<span style='background:{badge_bg};color:{badge_fg};font-size:11px;"
                    f"padding:2px 10px;border-radius:8px;font-weight:600'>{error_type}</span>"
                    f"<span style='font-weight:700;color:{fg};font-size:14px'>{marks}</span>"
                    f"</div></div>"
                    f"<div style='font-size:12px;color:#546E7A;margin-bottom:4px'>📚 {topic}</div>"
                    + (f"<div style='font-size:13px;color:#37474F;line-height:1.5'>"
                       f"💬 {specific}</div>" if specific else "")
                    + "</div>",
                    unsafe_allow_html=True
                )

        st.markdown("")

        # Correct questions — collapsed
        if right_qs:
            with st.expander(f"✅ {len(right_qs)} questions answered correctly", expanded=False):
                for q in right_qs:
                    st.markdown(
                        f"<div style='background:#E8F5E9;border-left:3px solid #2E7D32;"
                        f"border-radius:8px;padding:8px 14px;margin-bottom:6px;"
                        f"display:flex;justify-content:space-between'>"
                        f"<span style='font-weight:600;color:#2E7D32'>{q.get('qNo','')}</span>"
                        f"<span style='color:#546E7A;font-size:13px'>{q.get('topic','')}</span>"
                        f"<span style='font-weight:700;color:#2E7D32'>{q.get('marks','')}</span>"
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
                    f"<div style='background:#E8F5E9;padding:10px 12px;border-radius:8px;margin-bottom:6px'>"
                    f"<b style='color:#2E7D32'>{a.get('topic')}</b><br>"
                    f"<span style='font-size:12px;color:#546E7A'>{a.get('evidence')}</span></div>",
                    unsafe_allow_html=True
                )
        with col_w:
            st.markdown("**⚠️ Weak areas**")
            for a in data.get("weakAreas", []):
                sev = a.get("severity","medium")
                sev_bg    = {"high":"#FFEBEE","medium":"#FFF3E0","low":"#E8F5E9"}.get(sev,"#F5F5F5")
                sev_color = {"high":"#C62828","medium":"#E65100","low":"#2E7D32"}.get(sev,"#546E7A")
                st.markdown(
                    f"<div style='background:{sev_bg};padding:10px 12px;border-radius:8px;margin-bottom:6px'>"
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
            f"<span style='color:#37474F;line-height:1.7'>{data.get('rootCauseSummary','')}</span></div>",
            unsafe_allow_html=True
        )
        for a in data.get("weakAreas", []):
            sev = a.get("severity","medium")
            sev_bg    = {"high":"#FFEBEE","medium":"#FFF3E0","low":"#E8F5E9"}.get(sev,"#F5F5F5")
            sev_color = {"high":"#C62828","medium":"#E65100","low":"#2E7D32"}.get(sev,"#546E7A")
            st.markdown(
                f"<div style='background:white;border:1px solid #F0E6D3;"
                f"border-radius:12px;padding:14px 16px;margin-bottom:10px'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px'>"
                f"<b style='font-size:15px'>{a.get('topic')}</b>"
                f"<span style='background:{sev_bg};color:{sev_color};font-size:11px;"
                f"padding:3px 10px;border-radius:10px;font-weight:600'>{sev} priority</span></div>"
                f"<span style='color:#546E7A;font-size:14px'>💡 <b>Root cause:</b> {a.get('rootCause')}</span></div>",
                unsafe_allow_html=True
            )
        st.markdown("**🎯 Checkpoint test after 7 days — focus only on:**")
        chips = " ".join([
            f"<span style='background:#E3F2FD;color:#1565C0;padding:5px 14px;"
            f"border-radius:10px;font-size:13px;margin-right:6px'>{t}</span>"
            for t in data.get("checkpointTestFocus", [])
        ])
        st.markdown(chips + "<br>", unsafe_allow_html=True)
        st.caption("After the 7-day plan, test only these topics — not a broad general test.")

    # ════════════════════════════════════════════════════
    # TAB 3 — 7-DAY PLAN
    # ════════════════════════════════════════════════════
    with tab3:
        st.markdown(f"Targeted plan for **{name_label}** — focused on specific weak areas, not generic revision.")
        st.markdown("")
        for day in data.get("sevenDayPlan", []):
            day_num = day.get("day","")
            label   = f"Day {day_num} — {day.get('topic','')}  ·  {day.get('duration','')}"
            with st.expander(label, expanded=(day_num == 1)):
                st.write(day.get("activity",""))
        st.markdown("")
        st.markdown(
            "<div style='background:#E8F5E9;border:1px solid #A5D6A7;border-radius:10px;"
            "padding:14px 16px'><b style='color:#2E7D32'>✅ After Day 7</b><br>"
            "<span style='color:#546E7A;font-size:13px'>Run a mini checkpoint test focused only on the "
            "weak areas identified. If scores improve, the gaps are closed. "
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
                f"Daily challenges will automatically focus on these topics."
            )
            for k in synced:
                st.markdown(
                    f"<span style='background:#FFE4CC;color:#FF6600;padding:3px 10px;"
                    f"border-radius:10px;font-size:12px;margin-right:4px'>{k}</span>",
                    unsafe_allow_html=True
                )
        else:
            st.info("Weak areas will appear here after analysis is complete.")
        st.markdown("")
        summary_lines = [
            f"FocusFlow Test Analysis — {name_label}",
            "="*50,
            f"Subject: {data.get('subject')} | Grade: {data.get('grade')}",
            f"Score: {obtained}/{total} ({pct}%)",
            "",
            "QUESTION BREAKDOWN:",
        ]
        for q in data.get("questionBreakdown", []):
            if q.get("status") != "correct":
                summary_lines.append(
                    f"{q.get('qNo')}: {q.get('marks')} [{q.get('errorType','')}] — {q.get('specificMistake','')}"
                )
        summary_lines += [
            "",
            "WEAK AREAS:",
            *[f"• {a.get('topic')}: {a.get('rootCause')}" for a in data.get("weakAreas",[])],
            "",
            f"ROOT CAUSE: {data.get('rootCauseSummary','')}",
            "",
            "7-DAY PLAN:",
            *[f"Day {d.get('day')}: {d.get('topic')} — {d.get('activity')}" for d in data.get("sevenDayPlan",[])],
        ]
        st.download_button(
            "📋 Download Full Analysis",
            data="\n".join(summary_lines),
            file_name=f"focusflow_analysis_{name_label.replace(' ','_')}_{date.today()}.txt",
            mime="text/plain",
            use_container_width=True
        )


def show_parent_analyzer():
    """Main Parent Analyzer page — rendered when mode is Parent."""

    st.markdown("## 👨‍👩‍👧 Parent Test Analyzer")

    # ── Step 1: Upload ───────────────────────────────────
    uploaded_file = st.file_uploader(
        "📄 Upload test paper (photo or PDF)",
        type=["jpg", "jpeg", "png", "pdf"],
        help="Clear phone photo works great. If Google API key is added, the AI reads the image directly."
    )
    if uploaded_file:
        if uploaded_file.type.startswith("image"):
            st.image(uploaded_file, caption="Uploaded test paper", use_column_width=True)
        else:
            st.success(f"✅ {uploaded_file.name} uploaded successfully")

    st.markdown("")

    # ── Step 2: Context ──────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        child_name    = st.text_input("Child's name", placeholder="e.g. Arjun")
    with c2:
        child_grade   = st.text_input("Class / Grade", placeholder="e.g. Class 7")
    with c3:
        child_subject = st.text_input("Subject", placeholder="e.g. Mathematics")
    with c4:
        extra_notes   = st.text_input("Extra context", placeholder="e.g. skipped chapter 3")

    st.markdown("")

    if st.button("🔍 Analyze Test Paper", use_container_width=True, type="primary"):
        if not child_subject:
            st.warning("Please enter at least the subject so the AI can generate a relevant analysis.")
            return

        with st.spinner("Diagnosing gaps and building your child's improvement plan..."):
            try:
                data = run_parent_analysis(
                    child_name, child_grade, child_subject, extra_notes, uploaded_file
                )
                st.session_state.parent_analysis = data
                st.session_state.parent_child_name = child_name

                # Sync weak areas to student profile
                synced = sync_weak_areas_to_student(data)
                st.toast(
                    f"✅ Analysis complete! {synced} weak area(s) synced to "
                    f"{child_name or 'the student'}'s profile.",
                    icon="🎯"
                )

            except json.JSONDecodeError:
                st.error("The AI returned an unexpected response. Please try again.")
                return
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                return

    # ── Show results if available ────────────────────────
    if st.session_state.parent_analysis:
        st.divider()
        st.markdown("## 📊 Analysis Results")
        render_parent_results(
            st.session_state.parent_analysis,
            st.session_state.get("parent_child_name", "")
        )

        st.divider()
        if st.button("🔄 Analyze a Different Test", use_container_width=True):
            st.session_state.parent_analysis = None
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

    # ── MODE TOGGLE — always visible at top ──────────────
    st.markdown("### 👤 Mode")
    app_mode = st.radio(
        "",
        ["🎓 Student", "👨‍👩‍👧 Parent"],
        horizontal=True,
        label_visibility="collapsed",
        key="app_mode"
    )
    st.divider()

    # ════════════════════════════════════════════════════
    # PARENT SIDEBAR — clean, minimal, parent-relevant only
    # ════════════════════════════════════════════════════
    if app_mode == "👨‍👩‍👧 Parent":

        # How it works
        st.markdown("### 📋 How it works")
        st.markdown(
            "<div style='background:#FFF3E0;border-left:3px solid #FF6600;"
            "padding:12px 14px;border-radius:8px;font-size:13px;line-height:1.8'>"
            "📄 <b>Step 1</b> — Upload your child's test paper<br>"
            "🧒 <b>Step 2</b> — Enter child's name, class & subject<br>"
            "✨ <b>Step 3</b> — Get a full diagnosis in seconds"
            "</div>",
            unsafe_allow_html=True
        )

        st.divider()

        # Last analysis summary
        st.markdown("### 📊 Last Analysis")
        if st.session_state.parent_analysis:
            data = st.session_state.parent_analysis
            child = st.session_state.get("parent_child_name", "Student")
            pct   = data.get("percentage", 0)
            score_color = "#2E7D32" if pct >= 75 else "#E65100" if pct >= 50 else "#C62828"
            st.markdown(
                f"<div style='background:white;border:1px solid #F0E6D3;"
                f"border-radius:10px;padding:12px 14px'>"
                f"<div style='font-weight:700;font-size:14px;color:#1A1A1A'>{child}</div>"
                f"<div style='font-size:13px;color:#546E7A;margin-top:2px'>"
                f"{data.get('subject','')} &nbsp;·&nbsp; {data.get('grade','')}</div>"
                f"<div style='font-size:22px;font-weight:800;color:{score_color};margin-top:6px'>"
                f"{pct}% &nbsp;"
                f"<span style='font-size:13px;font-weight:400;color:#546E7A'>"
                f"{data.get('marksObtained',0)}/{data.get('totalMarks',0)} marks</span></div>"
                f"<div style='font-size:11px;color:#9E9E9E;margin-top:4px'>"
                f"Analyzed on {date.today().strftime('%d %b %Y')}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
        else:
            st.caption("No analysis run yet. Upload a test paper to get started.")

        st.divider()

        # AI Status
        st.markdown("### 🔌 AI Status")
        st.success(f"✅ {api_config['provider'].upper()}")
        if vision_config:
            st.success("✅ GOOGLE (Vision)")
            st.caption("PDFs & images: Gemini reads them directly")
        else:
            st.warning("⚠️ No vision API key")
            st.caption("Add GOOGLE_API_KEY to Streamlit secrets for PDF/image reading")

    # ════════════════════════════════════════════════════
    # STUDENT SIDEBAR — full original experience
    # ════════════════════════════════════════════════════
    else:
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

        # Keep exam_goal/current_topic/test_date accessible for student main area
        # (these are only defined inside the else block so we set them on session state)
        st.session_state._sidebar_exam_goal    = exam_goal
        st.session_state._sidebar_topic        = current_topic
        st.session_state._sidebar_test_date    = test_date

# ============================================================
# MAIN AREA — STUDENT MODE
# ============================================================
if app_mode == "🎓 Student":

    # Read values set by the student sidebar
    exam_goal     = st.session_state.get("_sidebar_exam_goal",  st.session_state.exam_goal)
    current_topic = st.session_state.get("_sidebar_topic",      st.session_state.current_topic)
    test_date     = st.session_state.get("_sidebar_test_date",  st.session_state.test_date)

    # u2500u2500 DISPLAY CHAT u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500u2500
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

    # ── PENDING AI REQUESTS ───────────────────────────────
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

    # ── CHAT INPUT ────────────────────────────────────────
    if prompt := st.chat_input("Ask a question..."):
        today = date.today()
        if st.session_state.last_study_date != today:
            st.session_state.study_streak += 1
            st.session_state.last_study_date = today

        current_messages.append({"role": "user", "content": prompt, "msg_type": "user_question"})

        user_msgs = [m for m in current_messages if m["role"] == "user" and not m.get("hidden")]
        if len(user_msgs) == 1:
            st.session_state.original_question = prompt

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

    # ── QUICK ACTION BUTTONS ──────────────────────────────
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

# ============================================================
# MAIN AREA — PARENT MODE
# ============================================================
else:
    show_parent_analyzer()
