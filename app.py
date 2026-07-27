import React, { useState, useEffect, useRef } from "react";
import {
  Flame, ChevronRight, ChevronLeft, Check, X, BookOpen, MessageCircleQuestion,
  StickyNote, Clock, Sparkles, Trophy, Target, ArrowRight, User, GraduationCap,
  RotateCcw, Home
} from "lucide-react";

const FONT_LINK = "https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap";

const SUBJECTS = {
  JEE: ["Physics", "Chemistry", "Mathematics"],
  NEET: ["Physics", "Chemistry", "Biology"],
};

const DAILY_QUESTIONS = [
  { q: "What is the SI unit of electric current?", options: ["Volt", "Ampere", "Ohm", "Watt"], answer: 1 },
  { q: "Which law states F = ma?", options: ["Newton's 1st Law", "Newton's 2nd Law", "Newton's 3rd Law", "Law of Gravitation"], answer: 1 },
  { q: "The pH of a neutral solution at 25°C is:", options: ["0", "7", "14", "1"], answer: 1 },
  { q: "Derivative of sin(x) is:", options: ["cos(x)", "-cos(x)", "-sin(x)", "tan(x)"], answer: 0 },
  { q: "Mitochondria is known as the:", options: ["Brain of the cell", "Powerhouse of the cell", "Skin of the cell", "Storehouse of the cell"], answer: 1 },
];

function PhoneFrame({ children }) {
  return (
    <div style={{ fontFamily: "'Inter', sans-serif" }} className="min-h-full w-full flex items-center justify-center py-8 px-4">
      <div
        className="relative w-[380px] h-[760px] rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col"
        style={{ background: "#FAFAFF", border: "8px solid #1B1B3D" }}
      >
        {/* notch */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-6 bg-[#1B1B3D] rounded-b-2xl z-20" />
        <div className="flex-1 overflow-y-auto overflow-x-hidden relative">{children}</div>
      </div>
    </div>
  );
}

function TopStatus({ streak }) {
  return (
    <div className="flex items-center justify-between px-5 pt-8 pb-2 text-xs" style={{ color: "#1B1B3D99" }}>
      <span className="font-semibold">9:41</span>
      <div className="flex items-center gap-1 bg-[#FFC93C22] px-2 py-1 rounded-full">
        <Flame size={13} color="#FF6B4A" fill="#FF6B4A" />
        <span className="font-bold" style={{ color: "#1B1B3D" }}>{streak}</span>
      </div>
    </div>
  );
}

function Screen({ children }) {
  return <div className="px-6 pb-8 flex flex-col min-h-full animate-[fadein_.25s_ease]">{children}</div>;
}

function BigButton({ children, onClick, variant = "primary", icon, disabled }) {
  const styles = {
    primary: { background: "#7C5CFC", color: "#fff" },
    coral: { background: "#FF6B4A", color: "#fff" },
    outline: { background: "#fff", color: "#1B1B3D", border: "2px solid #1B1B3D22" },
    mint: { background: "#2DD4A7", color: "#fff" },
  };
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{ ...styles[variant], fontFamily: "'Baloo 2', sans-serif", opacity: disabled ? 0.5 : 1 }}
      className="w-full py-3.5 rounded-2xl font-semibold text-base flex items-center justify-center gap-2 shadow-md active:scale-95 transition-transform"
    >
      {icon} {children}
    </button>
  );
}

function BackBar({ onBack, label }) {
  return (
    <button onClick={onBack} className="flex items-center gap-1 text-sm font-semibold mb-4 mt-1" style={{ color: "#7C5CFC", fontFamily: "'Baloo 2', sans-serif" }}>
      <ChevronLeft size={18} /> {label || "Back"}
    </button>
  );
}

function ProgressDots({ step, total }) {
  return (
    <div className="flex gap-1.5 mb-6">
      {Array.from({ length: total }).map((_, i) => (
        <div key={i} className="h-1.5 rounded-full flex-1" style={{ background: i <= step ? "#7C5CFC" : "#7C5CFC22" }} />
      ))}
    </div>
  );
}

export default function FocusFlowPrototype() {
  const [screen, setScreen] = useState("welcome");
  const [history, setHistory] = useState([]);
  const [profile, setProfile] = useState({ name: "", grade: "", exam: "", subjects: [] });
  const [streak, setStreak] = useState(4);
  const [dailyIdx, setDailyIdx] = useState(0);
  const [dailySelected, setDailySelected] = useState(null);
  const [dailyCorrect, setDailyCorrect] = useState(0);
  const [mockConfig, setMockConfig] = useState({ topic: "", questions: 10, duration: 15, negMarking: true });
  const [mockTimeLeft, setMockTimeLeft] = useState(0);
  const [doubtText, setDoubtText] = useState("");
  const [diagAnswer, setDiagAnswer] = useState(null);
  const [diagOutcome, setDiagOutcome] = useState(null);
  const [notesSubject, setNotesSubject] = useState("");

  const timerRef = useRef(null);

  const go = (s) => { setHistory((h) => [...h, screen]); setScreen(s); };
  const back = () => {
    setHistory((h) => {
      const nh = [...h];
      const prev = nh.pop();
      if (prev) setScreen(prev);
      return nh;
    });
  };

  useEffect(() => {
    if (screen === "mockTest") {
      setMockTimeLeft(mockConfig.duration * 60);
      timerRef.current = setInterval(() => {
        setMockTimeLeft((t) => {
          if (t <= 1) { clearInterval(timerRef.current); return 0; }
          return t - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timerRef.current);
    // eslint-disable-next-line
  }, [screen]);

  const fmtTime = (s) => `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;

  const resetAll = () => {
    setScreen("welcome");
    setHistory([]);
    setProfile({ name: "", grade: "", exam: "", subjects: [] });
    setDailyIdx(0); setDailySelected(null); setDailyCorrect(0);
    setDoubtText(""); setDiagAnswer(null); setDiagOutcome(null); setNotesSubject("");
  };

  return (
    <>
      <link rel="stylesheet" href={FONT_LINK} />
      <style>{`
        @keyframes fadein { from { opacity: 0; transform: translateY(6px);} to { opacity: 1; transform: translateY(0);} }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 0px; }
      `}</style>
      <div style={{ background: "#EDEBFF", minHeight: "100vh" }}>
        <PhoneFrame>

          {/* ===================== WELCOME / SIGN UP ===================== */}
          {screen === "welcome" && (
            <Screen>
              <div className="flex-1 flex flex-col items-center justify-center text-center gap-4">
                <div className="w-20 h-20 rounded-3xl flex items-center justify-center mb-2" style={{ background: "linear-gradient(135deg,#7C5CFC,#FF6B4A)" }}>
                  <Flame size={40} color="#fff" fill="#fff" />
                </div>
                <h1 style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="text-3xl font-extrabold">FocusFlow</h1>
                <p className="text-sm px-6" style={{ color: "#1B1B3D99" }}>Your daily companion for JEE & NEET — practice, doubts, and revision, gamified.</p>
              </div>
              <div className="flex flex-col gap-3 mt-6">
                <BigButton onClick={() => go("basicDetails")} icon={<Sparkles size={18} />}>Sign Up</BigButton>
                <BigButton variant="outline" onClick={() => go("home")}>Log In</BigButton>
              </div>
            </Screen>
          )}

          {/* ===================== BASIC DETAILS ===================== */}
          {screen === "basicDetails" && (
            <Screen>
              <TopStatus streak={streak} />
              <BackBar onBack={back} />
              <ProgressDots step={0} total={4} />
              <h2 style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="text-2xl font-bold mb-1">Tell us about you</h2>
              <p className="text-sm mb-6" style={{ color: "#1B1B3D99" }}>Just the basics to get started.</p>

              <label className="text-xs font-semibold mb-1" style={{ color: "#1B1B3D99" }}>NAME</label>
              <div className="flex items-center gap-2 rounded-xl px-4 py-3 mb-4" style={{ background: "#fff", border: "2px solid #1B1B3D14" }}>
                <User size={16} color="#7C5CFC" />
                <input
                  value={profile.name}
                  onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                  placeholder="e.g. Aarav Sharma"
                  className="flex-1 outline-none text-sm bg-transparent"
                  style={{ color: "#1B1B3D" }}
                />
              </div>

              <label className="text-xs font-semibold mb-1" style={{ color: "#1B1B3D99" }}>GRADE</label>
              <div className="flex gap-2 mb-8">
                {["11th", "12th", "Dropper"].map((g) => (
                  <button
                    key={g}
                    onClick={() => setProfile({ ...profile, grade: g })}
                    className="flex-1 py-2.5 rounded-xl text-sm font-semibold"
                    style={{
                      fontFamily: "'Baloo 2', sans-serif",
                      background: profile.grade === g ? "#7C5CFC" : "#fff",
                      color: profile.grade === g ? "#fff" : "#1B1B3D",
                      border: "2px solid " + (profile.grade === g ? "#7C5CFC" : "#1B1B3D14"),
                    }}
                  >{g}</button>
                ))}
              </div>

              <div className="mt-auto">
                <BigButton disabled={!profile.name || !profile.grade} onClick={() => go("chooseExam")} icon={<ArrowRight size={18} />}>Continue</BigButton>
              </div>
            </Screen>
          )}

          {/* ===================== CHOOSE EXAM ===================== */}
          {screen === "chooseExam" && (
            <Screen>
              <TopStatus streak={streak} />
              <BackBar onBack={back} />
              <ProgressDots step={1} total={4} />
              <h2 style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="text-2xl font-bold mb-1">Which exam are you targeting?</h2>
              <p className="text-sm mb-6" style={{ color: "#1B1B3D99" }}>This shapes everything we show you.</p>

              <div className="flex flex-col gap-3">
                {[
                  { key: "JEE", desc: "Physics · Chemistry · Mathematics", color: "#7C5CFC" },
                  { key: "NEET", desc: "Physics · Chemistry · Biology", color: "#FF6B4A" },
                ].map((e) => (
                  <button
                    key={e.key}
                    onClick={() => setProfile({ ...profile, exam: e.key, subjects: [] })}
                    className="text-left p-4 rounded-2xl flex items-center gap-3"
                    style={{
                      background: profile.exam === e.key ? `${e.color}18` : "#fff",
                      border: `2px solid ${profile.exam === e.key ? e.color : "#1B1B3D14"}`,
                    }}
                  >
                    <div className="w-11 h-11 rounded-xl flex items-center justify-center" style={{ background: e.color }}>
                      <GraduationCap size={22} color="#fff" />
                    </div>
                    <div>
                      <div style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="font-bold text-lg">{e.key}</div>
                      <div className="text-xs" style={{ color: "#1B1B3D99" }}>{e.desc}</div>
                    </div>
                  </button>
                ))}
              </div>

              <div className="mt-auto pt-6">
                <BigButton disabled={!profile.exam} onClick={() => go("chooseSubjects")} icon={<ArrowRight size={18} />}>Continue</BigButton>
              </div>
            </Screen>
          )}

          {/* ===================== CHOOSE SUBJECTS ===================== */}
          {screen === "chooseSubjects" && (
            <Screen>
              <TopStatus streak={streak} />
              <BackBar onBack={back} />
              <ProgressDots step={2} total={4} />
              <h2 style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="text-2xl font-bold mb-1">Pick your subjects</h2>
              <p className="text-sm mb-6" style={{ color: "#1B1B3D99" }}>Based on {profile.exam || "your exam"}. Select all that apply.</p>

              <div className="flex flex-col gap-3">
                {(SUBJECTS[profile.exam] || []).map((s) => {
                  const active = profile.subjects.includes(s);
                  return (
                    <button
                      key={s}
                      onClick={() =>
                        setProfile((p) => ({
                          ...p,
                          subjects: active ? p.subjects.filter((x) => x !== s) : [...p.subjects, s],
                        }))
                      }
                      className="flex items-center justify-between p-4 rounded-2xl"
                      style={{ background: active ? "#2DD4A718" : "#fff", border: `2px solid ${active ? "#2DD4A7" : "#1B1B3D14"}` }}
                    >
                      <span style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="font-semibold">{s}</span>
                      <div className="w-6 h-6 rounded-full flex items-center justify-center" style={{ background: active ? "#2DD4A7" : "#1B1B3D0D" }}>
                        {active && <Check size={14} color="#fff" />}
                      </div>
                    </button>
                  );
                })}
              </div>

              <div className="mt-auto pt-6">
                <BigButton disabled={profile.subjects.length === 0} onClick={() => go("profileCreated")} icon={<ArrowRight size={18} />}>Continue</BigButton>
              </div>
            </Screen>
          )}

          {/* ===================== PROFILE CREATED ===================== */}
          {screen === "profileCreated" && (
            <Screen>
              <div className="flex-1 flex flex-col items-center justify-center text-center gap-4">
                <div className="w-20 h-20 rounded-full flex items-center justify-center" style={{ background: "#2DD4A7" }}>
                  <Check size={40} color="#fff" strokeWidth={3} />
                </div>
                <h2 style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="text-2xl font-bold">You're all set, {profile.name.split(" ")[0] || "there"}!</h2>
                <p className="text-sm px-8" style={{ color: "#1B1B3D99" }}>Your {profile.exam} profile is ready with {profile.subjects.join(", ")}.</p>
              </div>
              <BigButton onClick={() => go("home")} variant="mint" icon={<Home size={18} />}>Go to Home</BigButton>
            </Screen>
          )}

          {/* ===================== HOME / CHOOSE A TASK ===================== */}
          {screen === "home" && (
            <Screen>
              <TopStatus streak={streak} />
              <div className="mt-2 mb-6">
                <h2 style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="text-2xl font-bold">Hey {profile.name.split(" ")[0] || "Champ"} 👋</h2>
                <p className="text-sm" style={{ color: "#1B1B3D99" }}>What are we tackling today?</p>
              </div>

              <div className="flex flex-col gap-3">
                <button onClick={() => go("practiceMode")} className="p-4 rounded-2xl flex items-center gap-3 text-left" style={{ background: "linear-gradient(135deg,#7C5CFC,#9B7CFF)" }}>
                  <div className="w-11 h-11 rounded-xl bg-white/20 flex items-center justify-center"><Target size={22} color="#fff" /></div>
                  <div>
                    <div style={{ fontFamily: "'Baloo 2', sans-serif" }} className="font-bold text-white">Practice</div>
                    <div className="text-xs text-white/80">Daily challenge or timed mock test</div>
                  </div>
                </button>
                <button onClick={() => go("doubtType")} className="p-4 rounded-2xl flex items-center gap-3 text-left" style={{ background: "linear-gradient(135deg,#FF6B4A,#FF9270)" }}>
                  <div className="w-11 h-11 rounded-xl bg-white/20 flex items-center justify-center"><MessageCircleQuestion size={22} color="#fff" /></div>
                  <div>
                    <div style={{ fontFamily: "'Baloo 2', sans-serif" }} className="font-bold text-white">Doubt Solving</div>
                    <div className="text-xs text-white/80">Get a doubt cleared, step by step</div>
                  </div>
                </button>
                <button onClick={() => go("notesSubject")} className="p-4 rounded-2xl flex items-center gap-3 text-left" style={{ background: "linear-gradient(135deg,#2DD4A7,#5CE0BE)" }}>
                  <div className="w-11 h-11 rounded-xl bg-white/20 flex items-center justify-center"><StickyNote size={22} color="#fff" /></div>
                  <div>
                    <div style={{ fontFamily: "'Baloo 2', sans-serif" }} className="font-bold text-white">Quick Notes</div>
                    <div className="text-xs text-white/80">Fast revision cheat sheets</div>
                  </div>
                </button>
              </div>

              <div className="mt-6 p-4 rounded-2xl flex items-center gap-3" style={{ background: "#FFC93C22" }}>
                <Flame size={26} color="#FF6B4A" fill="#FF6B4A" />
                <div>
                  <div style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="font-bold text-sm">{streak}-day streak!</div>
                  <div className="text-xs" style={{ color: "#1B1B3D99" }}>Keep it going — do today's challenge.</div>
                </div>
              </div>

              <button onClick={resetAll} className="text-xs mt-6 flex items-center justify-center gap-1 mx-auto" style={{ color: "#1B1B3D66" }}>
                <RotateCcw size={12} /> Restart prototype
              </button>
            </Screen>
          )}

          {/* ===================== PRACTICE MODE LANDING ===================== */}
          {screen === "practiceMode" && (
            <Screen>
              <TopStatus streak={streak} />
              <BackBar onBack={back} label="Home" />
              <h2 style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="text-2xl font-bold mb-1">Practice Mode</h2>
              <p className="text-sm mb-6" style={{ color: "#1B1B3D99" }}>Choose how you want to practice.</p>

              <button onClick={() => { setDailyIdx(0); setDailySelected(null); setDailyCorrect(0); go("dailyChallenge"); }} className="p-4 rounded-2xl flex items-center gap-3 text-left mb-3" style={{ background: "#fff", border: "2px solid #1B1B3D14" }}>
                <div className="w-11 h-11 rounded-xl flex items-center justify-center" style={{ background: "#FFC93C" }}><Sparkles size={20} color="#1B1B3D" /></div>
                <div>
                  <div style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="font-bold">Daily Challenge</div>
                  <div className="text-xs" style={{ color: "#1B1B3D99" }}>5 questions · untimed · based on your profile</div>
                </div>
              </button>

              <button onClick={() => go("configureTest")} className="p-4 rounded-2xl flex items-center gap-3 text-left" style={{ background: "#fff", border: "2px solid #1B1B3D14" }}>
                <div className="w-11 h-11 rounded-xl flex items-center justify-center" style={{ background: "#7C5CFC" }}><Clock size={20} color="#fff" /></div>
                <div>
                  <div style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="font-bold">Timed Mock Test</div>
                  <div className="text-xs" style={{ color: "#1B1B3D99" }}>Pick a chapter, set the clock</div>
                </div>
              </button>
            </Screen>
          )}

          {/* ===================== DAILY CHALLENGE - QUESTION ===================== */}
          {screen === "dailyChallenge" && (
            <Screen>
              <TopStatus streak={streak} />
              <BackBar onBack={() => go("practiceMode")} label="Exit" />
              <ProgressDots step={dailyIdx} total={5} />
              <div className="text-xs font-semibold mb-2" style={{ color: "#7C5CFC" }}>QUESTION {dailyIdx + 1} OF 5</div>
              <h2 style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="text-xl font-bold mb-6">{DAILY_QUESTIONS[dailyIdx].q}</h2>

              <div className="flex flex-col gap-3">
                {DAILY_QUESTIONS[dailyIdx].options.map((opt, i) => {
                  const isSel = dailySelected === i;
                  const isAns = DAILY_QUESTIONS[dailyIdx].answer === i;
                  let bg = "#fff", border = "#1B1B3D14", textColor = "#1B1B3D";
                  if (dailySelected !== null) {
                    if (isAns) { bg = "#2DD4A718"; border = "#2DD4A7"; }
                    else if (isSel) { bg = "#FF6B4A18"; border = "#FF6B4A"; }
                  }
                  return (
                    <button key={i} disabled={dailySelected !== null} onClick={() => { setDailySelected(i); if (i === DAILY_QUESTIONS[dailyIdx].answer) setDailyCorrect((c) => c + 1); }}
                      className="p-3.5 rounded-xl text-left text-sm font-medium" style={{ background: bg, border: `2px solid ${border}`, color: textColor }}>
                      {opt}
                    </button>
                  );
                })}
              </div>

              <div className="mt-auto pt-6">
                {dailySelected !== null && (
                  dailyIdx < 4 ? (
                    <BigButton onClick={() => { setDailyIdx((i) => i + 1); setDailySelected(null); }} icon={<ChevronRight size={18} />}>Next Question</BigButton>
                  ) : (
                    <BigButton variant="mint" onClick={() => { setStreak((s) => s + 1); go("dailyDone"); }} icon={<Check size={18} />}>Finish Challenge</BigButton>
                  )
                )}
              </div>
            </Screen>
          )}

          {/* ===================== DAILY CHALLENGE - DONE ===================== */}
          {screen === "dailyDone" && (
            <Screen>
              <div className="flex-1 flex flex-col items-center justify-center text-center gap-3">
                <Flame size={64} color="#FF6B4A" fill="#FF6B4A" />
                <h2 style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="text-2xl font-bold">Streak Updated!</h2>
                <div style={{ fontFamily: "'Baloo 2', sans-serif", color: "#FF6B4A" }} className="text-4xl font-extrabold">{streak} days 🔥</div>
                <p className="text-sm px-8" style={{ color: "#1B1B3D99" }}>You got {dailyCorrect}/5 correct today. Nice work!</p>
              </div>
              <BigButton onClick={() => go("home")} icon={<Home size={18} />}>Back to Home</BigButton>
            </Screen>
          )}

          {/* ===================== CONFIGURE TEST ===================== */}
          {screen === "configureTest" && (
            <Screen>
              <TopStatus streak={streak} />
              <BackBar onBack={() => go("practiceMode")} />
              <h2 style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="text-2xl font-bold mb-1">Configure Test</h2>
              <p className="text-sm mb-6" style={{ color: "#1B1B3D99" }}>Set up your mock test.</p>

              <label className="text-xs font-semibold mb-2 block" style={{ color: "#1B1B3D99" }}>CHAPTER / TOPIC</label>
              <div className="flex flex-wrap gap-2 mb-5">
                {["Kinematics", "Thermodynamics", "Organic Chem", "Calculus"].map((t) => (
                  <button key={t} onClick={() => setMockConfig({ ...mockConfig, topic: t })}
                    className="px-3 py-2 rounded-xl text-xs font-semibold"
                    style={{ fontFamily: "'Baloo 2', sans-serif", background: mockConfig.topic === t ? "#7C5CFC" : "#fff", color: mockConfig.topic === t ? "#fff" : "#1B1B3D", border: `2px solid ${mockConfig.topic === t ? "#7C5CFC" : "#1B1B3D14"}` }}>
                    {t}
                  </button>
                ))}
              </div>

              <label className="text-xs font-semibold mb-2 block" style={{ color: "#1B1B3D99" }}>NUMBER OF QUESTIONS: {mockConfig.questions}</label>
              <input type="range" min={5} max={30} step={5} value={mockConfig.questions} onChange={(e) => setMockConfig({ ...mockConfig, questions: +e.target.value })} className="w-full mb-5" style={{ accentColor: "#7C5CFC" }} />

              <label className="text-xs font-semibold mb-2 block" style={{ color: "#1B1B3D99" }}>DURATION: {mockConfig.duration} min</label>
              <input type="range" min={5} max={60} step={5} value={mockConfig.duration} onChange={(e) => setMockConfig({ ...mockConfig, duration: +e.target.value })} className="w-full mb-5" style={{ accentColor: "#7C5CFC" }} />

              <button onClick={() => setMockConfig({ ...mockConfig, negMarking: !mockConfig.negMarking })} className="flex items-center justify-between p-3.5 rounded-xl mb-6" style={{ background: "#fff", border: "2px solid #1B1B3D14" }}>
                <span className="text-sm font-semibold" style={{ color: "#1B1B3D" }}>Negative Marking</span>
                <div className="w-10 h-6 rounded-full relative transition-colors" style={{ background: mockConfig.negMarking ? "#7C5CFC" : "#1B1B3D22" }}>
                  <div className="w-4 h-4 rounded-full bg-white absolute top-1 transition-all" style={{ left: mockConfig.negMarking ? "22px" : "4px" }} />
                </div>
              </button>

              <div className="mt-auto">
                <BigButton disabled={!mockConfig.topic} onClick={() => go("mockTest")} variant="coral" icon={<Clock size={18} />}>Start Test</BigButton>
              </div>
            </Screen>
          )}

          {/* ===================== MOCK TEST (TIMED) ===================== */}
          {screen === "mockTest" && (
            <Screen>
              <div className="flex items-center justify-between mt-8 mb-6">
                <span style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="font-bold">{mockConfig.topic}</span>
                <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full" style={{ background: mockTimeLeft < 30 ? "#FF6B4A22" : "#7C5CFC22" }}>
                  <Clock size={14} color={mockTimeLeft < 30 ? "#FF6B4A" : "#7C5CFC"} />
                  <span className="text-sm font-bold" style={{ color: mockTimeLeft < 30 ? "#FF6B4A" : "#7C5CFC", fontFamily: "'Baloo 2', sans-serif" }}>{fmtTime(mockTimeLeft)}</span>
                </div>
              </div>

              <div className="rounded-2xl p-5 mb-4" style={{ background: "#fff", border: "2px solid #1B1B3D14" }}>
                <div className="text-xs font-semibold mb-2" style={{ color: "#7C5CFC" }}>QUESTION 1 OF {mockConfig.questions}</div>
                <p className="text-sm font-medium" style={{ color: "#1B1B3D" }}>A body moving with constant velocity has acceleration equal to:</p>
                <div className="flex flex-col gap-2 mt-4">
                  {["Zero", "Constant non-zero", "Increasing", "Depends on mass"].map((o, i) => (
                    <button key={i} className="p-3 rounded-xl text-left text-sm" style={{ background: "#FAFAFF", border: "2px solid #1B1B3D0F", color: "#1B1B3D" }}>{o}</button>
                  ))}
                </div>
              </div>
              <p className="text-xs text-center mb-4" style={{ color: "#1B1B3D66" }}>({mockConfig.questions - 1} more questions in the full test — prototype shows sample)</p>

              <div className="mt-auto">
                <BigButton variant="coral" onClick={() => { clearInterval(timerRef.current); go("mockScore"); }} icon={<Check size={18} />}>Submit Test</BigButton>
              </div>
            </Screen>
          )}

          {/* ===================== MOCK TEST SCORE ===================== */}
          {screen === "mockScore" && (
            <Screen>
              <div className="flex-1 flex flex-col items-center justify-center text-center gap-3">
                <Trophy size={60} color="#FFC93C" fill="#FFC93C" />
                <h2 style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="text-2xl font-bold">Score + Analytics</h2>
                <div style={{ fontFamily: "'Baloo 2', sans-serif", color: "#7C5CFC" }} className="text-4xl font-extrabold">7/{mockConfig.questions}</div>
                <div className="flex gap-4 mt-2">
                  <div className="text-center"><div className="text-lg font-bold" style={{ color: "#2DD4A7" }}>7</div><div className="text-xs" style={{ color: "#1B1B3D99" }}>Correct</div></div>
                  <div className="text-center"><div className="text-lg font-bold" style={{ color: "#FF6B4A" }}>3</div><div className="text-xs" style={{ color: "#1B1B3D99" }}>Wrong</div></div>
                </div>
                <div className="mt-4 px-5 py-3 rounded-xl text-xs" style={{ background: "#FF6B4A18", color: "#1B1B3D" }}>
                  Wrong answers logged to your <b>Mistake Journal</b> for review.
                </div>
              </div>
              <BigButton onClick={() => go("home")} icon={<Home size={18} />}>Back to Home</BigButton>
            </Screen>
          )}

          {/* ===================== DOUBT SOLVING - TYPE DOUBT ===================== */}
          {screen === "doubtType" && (
            <Screen>
              <TopStatus streak={streak} />
              <BackBar onBack={back} label="Home" />
              <h2 style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="text-2xl font-bold mb-1">What's your doubt?</h2>
              <p className="text-sm mb-6" style={{ color: "#1B1B3D99" }}>Type it out — we'll check your understanding first.</p>

              <textarea
                value={doubtText}
                onChange={(e) => setDoubtText(e.target.value)}
                placeholder="e.g. Why does resistance increase with temperature in conductors?"
                className="w-full h-32 p-4 rounded-2xl text-sm outline-none resize-none"
                style={{ background: "#fff", border: "2px solid #1B1B3D14", color: "#1B1B3D" }}
              />

              <div className="mt-auto pt-6">
                <BigButton disabled={!doubtText.trim()} onClick={() => go("diagnosticQ")} variant="coral" icon={<ArrowRight size={18} />}>Submit Doubt</BigButton>
              </div>
            </Screen>
          )}

          {/* ===================== DIAGNOSTIC QUESTION ===================== */}
          {screen === "diagnosticQ" && (
            <Screen>
              <TopStatus streak={streak} />
              <BackBar onBack={() => go("doubtType")} />
              <div className="text-xs font-semibold mb-2" style={{ color: "#FF6B4A" }}>DIAGNOSTIC CHECK</div>
              <h2 style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="text-xl font-bold mb-6">Before we explain — try this related question:</h2>

              <div className="rounded-2xl p-5 mb-4" style={{ background: "#fff", border: "2px solid #1B1B3D14" }}>
                <p className="text-sm font-medium mb-4" style={{ color: "#1B1B3D" }}>As temperature increases, resistance of a metallic conductor:</p>
                <div className="flex flex-col gap-2">
                  {[{ t: "Increases", correct: true }, { t: "Decreases", correct: false }, { t: "Stays the same", correct: false }].map((o, i) => (
                    <button key={i} onClick={() => { setDiagAnswer(i); setDiagOutcome(o.correct ? "correct" : "wrong"); }}
                      className="p-3 rounded-xl text-left text-sm font-medium" style={{ background: "#FAFAFF", border: "2px solid #1B1B3D0F", color: "#1B1B3D" }}>
                      {o.t}
                    </button>
                  ))}
                </div>
              </div>

              {diagOutcome && (
                <div className="mt-auto pt-4">
                  <BigButton variant={diagOutcome === "correct" ? "mint" : "coral"} onClick={() => go("doubtResult")} icon={<ArrowRight size={18} />}>Continue</BigButton>
                </div>
              )}
            </Screen>
          )}

          {/* ===================== DOUBT RESULT (CORRECT / WRONG) ===================== */}
          {screen === "doubtResult" && (
            <Screen>
              <TopStatus streak={streak} />
              {diagOutcome === "correct" ? (
                <div className="flex-1 flex flex-col items-center justify-center text-center gap-3">
                  <div className="w-16 h-16 rounded-full flex items-center justify-center" style={{ background: "#2DD4A7" }}>
                    <Check size={32} color="#fff" strokeWidth={3} />
                  </div>
                  <div style={{ fontFamily: "'Baloo 2', sans-serif", color: "#2DD4A7" }} className="font-bold text-lg">Nice! You got it right 🎉</div>
                  <div className="rounded-2xl p-4 mt-3 text-left text-sm" style={{ background: "#fff", border: "2px solid #1B1B3D14", color: "#1B1B3D99" }}>
                    <b style={{ color: "#1B1B3D" }}>Concept explained in depth:</b><br />
                    As temperature rises, ion vibrations increase, causing more collisions with electrons — this raises resistance in metallic conductors.
                  </div>
                  <div className="text-sm font-semibold mt-2" style={{ color: "#2DD4A7", fontFamily: "'Baloo 2', sans-serif" }}>Doubt Resolved ✓</div>
                </div>
              ) : (
                <div className="flex-1 flex flex-col items-center justify-center text-center gap-3">
                  <div className="w-16 h-16 rounded-full flex items-center justify-center" style={{ background: "#FF6B4A" }}>
                    <X size={32} color="#fff" strokeWidth={3} />
                  </div>
                  <div style={{ fontFamily: "'Baloo 2', sans-serif", color: "#FF6B4A" }} className="font-bold text-lg">Not quite — let's break it down</div>
                  <div className="rounded-2xl p-4 mt-3 text-left text-sm" style={{ background: "#fff", border: "2px solid #1B1B3D14", color: "#1B1B3D99" }}>
                    <b style={{ color: "#1B1B3D" }}>Answer explained:</b><br />
                    Resistance actually <i>increases</i> with temperature in metals — more thermal vibration means more electron collisions.
                  </div>
                  <div className="px-4 py-2 rounded-xl text-xs mt-2" style={{ background: "#FF6B4A18", color: "#1B1B3D" }}>Logged to Mistake Journal</div>
                </div>
              )}
              <BigButton onClick={() => go("home")} icon={<Home size={18} />}>Back to Home</BigButton>
            </Screen>
          )}

          {/* ===================== QUICK NOTES - PICK SUBJECT ===================== */}
          {screen === "notesSubject" && (
            <Screen>
              <TopStatus streak={streak} />
              <BackBar onBack={back} label="Home" />
              <h2 style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="text-2xl font-bold mb-1">Quick Notes</h2>
              <p className="text-sm mb-6" style={{ color: "#1B1B3D99" }}>Pick a subject for a fast cheat sheet.</p>

              <button onClick={() => { setNotesSubject((profile.subjects[0]) || "Physics"); go("cheatSheet"); }} className="p-4 rounded-2xl flex items-center justify-between mb-4" style={{ background: "#2DD4A718", border: "2px solid #2DD4A7" }}>
                <span style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="font-semibold">Use Current One ({profile.subjects[0] || "Physics"})</span>
                <ArrowRight size={18} color="#2DD4A7" />
              </button>

              <div className="flex flex-col gap-2">
                {(profile.subjects.length ? profile.subjects : ["Physics", "Chemistry", "Mathematics"]).map((s) => (
                  <button key={s} onClick={() => { setNotesSubject(s); go("cheatSheet"); }} className="p-3.5 rounded-xl text-left text-sm font-semibold" style={{ background: "#fff", border: "2px solid #1B1B3D14", color: "#1B1B3D" }}>
                    {s}
                  </button>
                ))}
              </div>
            </Screen>
          )}

          {/* ===================== CHEAT SHEET ===================== */}
          {screen === "cheatSheet" && (
            <Screen>
              <TopStatus streak={streak} />
              <BackBar onBack={() => go("notesSubject")} />
              <div className="text-xs font-semibold mb-1" style={{ color: "#2DD4A7" }}>{notesSubject?.toUpperCase()}</div>
              <h2 style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="text-xl font-bold mb-5">Newton's Second Law</h2>

              <div className="rounded-2xl p-4 mb-3" style={{ background: "#fff", border: "2px solid #1B1B3D14" }}>
                <div className="text-xs font-bold mb-1" style={{ color: "#7C5CFC" }}>CORE CONCEPT</div>
                <p className="text-sm" style={{ color: "#1B1B3D" }}>The rate of change of momentum of a body is directly proportional to the applied force, in the direction of the force.</p>
              </div>
              <div className="rounded-2xl p-4 mb-3" style={{ background: "#fff", border: "2px solid #1B1B3D14" }}>
                <div className="text-xs font-bold mb-1" style={{ color: "#FF6B4A" }}>FORMULA</div>
                <p className="text-lg font-bold" style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }}>F = m · a</p>
              </div>
              <div className="rounded-2xl p-4 mb-6" style={{ background: "#fff", border: "2px solid #1B1B3D14" }}>
                <div className="text-xs font-bold mb-1" style={{ color: "#2DD4A7" }}>EXAMPLE</div>
                <p className="text-sm" style={{ color: "#1B1B3D" }}>A 2kg block accelerating at 3 m/s² needs a net force of 6N.</p>
              </div>

              <div className="mt-auto">
                <BigButton variant="mint" onClick={() => go("notesDone")} icon={<Check size={18} />}>Done Revising</BigButton>
              </div>
            </Screen>
          )}

          {/* ===================== QUICK NOTES DONE ===================== */}
          {screen === "notesDone" && (
            <Screen>
              <div className="flex-1 flex flex-col items-center justify-center text-center gap-3">
                <BookOpen size={56} color="#2DD4A7" />
                <h2 style={{ fontFamily: "'Baloo 2', sans-serif", color: "#1B1B3D" }} className="text-2xl font-bold">Quick Notes Done ✓</h2>
                <p className="text-sm px-8" style={{ color: "#1B1B3D99" }}>Nice refresh! Come back anytime for a quick revision.</p>
              </div>
              <BigButton onClick={() => go("home")} icon={<Home size={18} />}>Back to Home</BigButton>
            </Screen>
          )}

        </PhoneFrame>
      </div>
    </>
  );
}
