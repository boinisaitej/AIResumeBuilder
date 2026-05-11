import streamlit as st
import json, os, re, time
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project directory (not the current working dir) and
# override any pre-existing empty vars so users can edit .env without restarting.
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(_ENV_PATH, override=True)

st.set_page_config(
    page_title="AI Resume Builder",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=Inter:wght@300;400;500;600&display=swap');

:root {
  --tx:#111827; --mu:#6B7280; --bd:#D1D5DB;
  --s1:#F9FAFB; --s2:#F3F4F6; --s3:#E5E7EB;
}
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
  font-family: 'Inter', sans-serif !important;
  background: #fff !important;
  color: #111827 !important;
}
h1,h2,h3,h4 { font-family: 'Syne', sans-serif !important; }
.stApp { background: #fff !important; }
.main .block-container {
  padding: 1.2rem 2rem 3rem !important;
  max-width: 1100px !important;
}
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ════════════════════════════════════════════
   SIDEBAR — force dark theme
   ════════════════════════════════════════════ */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div > div,
[data-testid="stSidebar"] > div > div > div {
  background-color: #111827 !important;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown span,
[data-testid="stSidebar"] .stMarkdown div,
[data-testid="stSidebar"] .stMarkdown small,
[data-testid="stSidebar"] .stMarkdown a,
[data-testid="stSidebar"] .stMarkdown li,
[data-testid="stSidebar"] .element-container p {
  color: #D1D5DB !important;
}
[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] .stMarkdown h4 {
  color: #F9FAFB !important;
}
[data-testid="stSidebar"] .stMarkdown code {
  background: #1F2937 !important;
  color: #D1D5DB !important;
  padding: 1px 5px;
  border-radius: 4px;
}
[data-testid="stSidebar"] hr {
  border-color: #374151 !important;
  margin: 8px 0 !important;
}
/* Sidebar labels */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stTextArea label,
[data-testid="stSidebar"] .stTextInput label {
  color: #9CA3AF !important;
  font-size: .72rem !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: .05em !important;
}
/* Sidebar text area */
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] .stTextArea textarea {
  background-color: #1F2937 !important;
  border: 1.5px solid #374151 !important;
  color: #F9FAFB !important;
  border-radius: 8px !important;
  font-size: .85rem !important;
  caret-color: #F9FAFB !important;
}
[data-testid="stSidebar"] textarea:focus,
[data-testid="stSidebar"] .stTextArea textarea:focus {
  border-color: #6C63FF !important;
  box-shadow: 0 0 0 2px rgba(108,99,255,.3) !important;
  outline: none !important;
}
[data-testid="stSidebar"] textarea::placeholder {
  color: #6B7280 !important;
}
/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
  background-color: #1F2937 !important;
  border: 1.5px solid #374151 !important;
  color: #D1D5DB !important;
  border-radius: 8px !important;
  width: 100% !important;
  font-size: .82rem !important;
  padding: .45rem .8rem !important;
  font-weight: 600 !important;
  transition: all .18s !important;
  cursor: pointer !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background-color: #374151 !important;
  border-color: #6C63FF !important;
  color: #fff !important;
}

/* ════════════════════════════════════════════
   MAIN AREA — INPUTS
   ════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
  background: #fff !important;
  border: 1.5px solid #D1D5DB !important;
  color: #111827 !important;
  border-radius: 8px !important;
  font-family: 'Inter', sans-serif !important;
  font-size: .9rem !important;
  transition: border-color .2s, box-shadow .2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: #6C63FF !important;
  box-shadow: 0 0 0 3px rgba(108,99,255,.1) !important;
}
.stTextInput label, .stTextArea label,
.stNumberInput label, .stSelectbox label, .stFileUploader label {
  color: #6B7280 !important;
  font-size: .74rem !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: .05em !important;
}
[data-baseweb="select"] > div {
  background: #fff !important;
  border: 1.5px solid #D1D5DB !important;
  border-radius: 8px !important;
  color: #111827 !important;
}
[data-baseweb="popover"] ul { background: #fff !important; }
[data-baseweb="option"] { background: #fff !important; color: #111827 !important; }
[data-baseweb="option"]:hover { background: #F3F4F6 !important; }
[data-baseweb="select"] input { color: #111827 !important; }
[data-baseweb="select"] span { color: #111827 !important; }

/* ════════════════════════════════════════════
   BUTTONS — BLACK DEFAULT
   ════════════════════════════════════════════ */
.stButton > button {
  background: #111827 !important;
  color: #fff !important;
  border: none !important;
  border-radius: 8px !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 600 !important;
  font-size: .85rem !important;
  padding: .5rem 1.1rem !important;
  cursor: pointer !important;
  transition: all .18s !important;
  width: 100% !important;
}
.stButton > button:hover {
  background: #1F2937 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 14px rgba(0,0,0,.22) !important;
}
.stButton > button:disabled {
  background: #E5E7EB !important;
  color: #9CA3AF !important;
  transform: none !important;
  box-shadow: none !important;
}
.btn-g .stButton > button { background: #059669 !important; }
.btn-g .stButton > button:hover { background: #047857 !important; }
.btn-r .stButton > button { background: #DC2626 !important; }
.btn-r .stButton > button:hover { background: #B91C1C !important; }
.btn-a .stButton > button { background: #D97706 !important; }
.btn-a .stButton > button:hover { background: #B45309 !important; }
.btn-b .stButton > button { background: #1D4ED8 !important; }
.btn-b .stButton > button:hover { background: #1E40AF !important; }
.btn-t .stButton > button { background: #0D9488 !important; }
.btn-t .stButton > button:hover { background: #0F766E !important; }

.stDownloadButton > button {
  background: #111827 !important;
  color: #fff !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  width: 100% !important;
  padding: .5rem 1.1rem !important;
  transition: all .18s !important;
}
.stDownloadButton > button:hover {
  background: #1F2937 !important;
  transform: translateY(-1px) !important;
}

/* ════════════════════════════════════════════
   CARDS & SECTIONS
   ════════════════════════════════════════════ */
.sec-title {
  font-family: 'Syne', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: .8rem;
  padding-bottom: .5rem;
  border-bottom: 2px solid #111827;
}
.entry-card {
  background: #F9FAFB;
  border: 1px solid #D1D5DB;
  border-radius: 10px;
  padding: 1rem 1.2rem;
  margin-bottom: .8rem;
  transition: border-color .2s;
}
.entry-card:hover { border-color: #6B7280; }
.skill-row {
  background: #F9FAFB;
  border: 1px solid #D1D5DB;
  border-radius: 10px;
  padding: .75rem 1rem;
  margin-bottom: .6rem;
  transition: border-color .2s;
}
.skill-row:hover { border-color: #6B7280; }

/* ════════════════════════════════════════════
   STATUS BOXES
   ════════════════════════════════════════════ */
.box-ok   { background:#F0FDF4; border:1px solid #86EFAC; border-radius:8px; padding:.6rem 1rem; font-size:.82rem; color:#166534; margin:.4rem 0; }
.box-warn { background:#FFFBEB; border:1px solid #FCD34D; border-radius:8px; padding:.6rem 1rem; font-size:.82rem; color:#92400E; margin:.4rem 0; }
.box-err  { background:#FEF2F2; border:1px solid #FECACA; border-radius:8px; padding:.6rem 1rem; font-size:.82rem; color:#991B1B; margin:.4rem 0; }
.box-info { background:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:.6rem 1rem; font-size:.82rem; color:#1E40AF; margin:.4rem 0; }

/* ════════════════════════════════════════════
   WORKFLOW STEPS
   ════════════════════════════════════════════ */
.wf-step {
  display: flex;
  align-items: center;
  gap: .7rem;
  padding: .55rem .9rem;
  border-radius: 9px;
  border: 1px solid #D1D5DB;
  background: #fff;
  margin-bottom: .3rem;
  transition: all .3s;
}
.wf-run  { border-color: #6C63FF !important; background: #F5F3FF !important; }
.wf-done { border-color: #059669 !important; background: #F0FDF4 !important; }
.wf-err  { border-color: #DC2626 !important; background: #FEF2F2 !important; }
.wf-icon { font-size: 1.1rem; }
.wf-label { font-weight: 700; font-size: .85rem; color: #111827; }
.wf-desc  { font-size: .73rem; color: #6B7280; margin-top: 1px; }
.wf-badge {
  display: inline-block;
  padding: 1px 8px;
  border-radius: 20px;
  font-size: .67rem;
  font-weight: 700;
  margin-left: 6px;
}
.b-wait { background:#F3F4F6; color:#6B7280; }
.b-run  { background:#EDE9FE; color:#5B21B6; }
.b-done { background:#DCFCE7; color:#166534; }
.b-err  { background:#FEE2E2; color:#991B1B; }

/* ════════════════════════════════════════════
   ATS BOX
   ════════════════════════════════════════════ */
.ats-box {
  background: #F9FAFB;
  border: 1px solid #D1D5DB;
  border-radius: 12px;
  padding: 1.3rem;
  text-align: center;
  margin-bottom: 1rem;
}

/* ════════════════════════════════════════════
   TEMPLATE CARDS
   ════════════════════════════════════════════ */
.tmpl-card {
  border: 2px solid #D1D5DB;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all .22s;
  background: #fff;
  margin-bottom: .4rem;
}
.tmpl-card:hover {
  border-color: #111827;
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 8px 24px rgba(0,0,0,.12);
}
.tmpl-card.sel { border-color: #111827; box-shadow: 0 0 0 3px rgba(17,24,39,.15); }

/* ════════════════════════════════════════════
   SKILL BAR
   ════════════════════════════════════════════ */
.sk-bar { margin-bottom: .55rem; }
.sk-bar-top { display:flex; justify-content:space-between; font-size:.78rem; margin-bottom:3px; color:#111827; }
.sk-bar-bg  { background:#E5E7EB; border-radius:99px; height:5px; overflow:hidden; }
.sk-bar-fill { height:5px; border-radius:99px; }

/* ════════════════════════════════════════════
   ROADMAP & INSIGHT CARDS
   ════════════════════════════════════════════ */
.insight-card {
  background: #fff;
  border: 1px solid #D1D5DB;
  border-radius: 10px;
  padding: 1rem 1.2rem;
  margin-bottom: .8rem;
}
.insight-title {
  font-family: 'Syne', sans-serif;
  font-size: .9rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: .5rem;
  padding-bottom: .4rem;
  border-bottom: 1px solid #E5E7EB;
}
.role-chip {
  display: inline-block;
  background: #F3F4F6;
  border: 1px solid #D1D5DB;
  border-radius: 20px;
  padding: 3px 10px;
  font-size: .78rem;
  color: #374151;
  font-weight: 500;
  margin: 2px 3px;
}
.skill-chip {
  display: inline-block;
  background: #EFF6FF;
  border: 1px solid #BFDBFE;
  border-radius: 20px;
  padding: 3px 10px;
  font-size: .78rem;
  color: #1E40AF;
  font-weight: 500;
  margin: 2px 3px;
}

/* ════════════════════════════════════════════
   POST BOX
   ════════════════════════════════════════════ */
.post-box {
  background: #F9FAFB;
  border: 1px solid #D1D5DB;
  border-radius: 10px;
  padding: 1.2rem;
  white-space: pre-wrap;
  line-height: 1.85;
  font-size: .92rem;
  color: #111827;
}

/* ════════════════════════════════════════════
   PREVIEW BOX
   ════════════════════════════════════════════ */
.preview-box {
  background: #fff;
  border: 1px solid #D1D5DB;
  border-radius: 10px;
  padding: 1.5rem 2rem;
  color: #111827;
  line-height: 1.7;
}
.preview-box h1, .preview-box h2, .preview-box h3 {
  color: #111827 !important;
  font-family: 'Syne', sans-serif !important;
}
.preview-box p, .preview-box li, .preview-box span {
  color: #111827 !important;
}

/* ════════════════════════════════════════════
   UPLOAD ANALYSIS
   ════════════════════════════════════════════ */
.analysis-box {
  background: #fff;
  border: 1px solid #D1D5DB;
  border-radius: 10px;
  padding: 1.2rem 1.5rem;
  color: #111827;
  line-height: 1.75;
  font-size: .9rem;
}
.analysis-box h1, .analysis-box h2,
.analysis-box h3, .analysis-box h4 {
  color: #111827 !important;
  margin-top: 1rem;
}
.analysis-box p, .analysis-box li { color: #111827 !important; }
.analysis-box strong { color: #111827 !important; }
.analysis-box * { color: #111827 !important; }

/* ════════════════════════════════════════════
   TABS
   ════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
  background: #F3F4F6 !important;
  border-radius: 10px !important;
  padding: 3px !important;
  gap: 3px !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: #6B7280 !important;
  border-radius: 7px !important;
  padding: .4rem .85rem !important;
  font-weight: 600 !important;
  font-size: .84rem !important;
}
.stTabs [aria-selected="true"] {
  background: #111827 !important;
  color: #fff !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.2rem !important; }

.stProgress > div > div > div {
  background: #111827 !important;
  border-radius: 99px !important;
}

hr { border-color: #D1D5DB !important; }
.div { border: none; border-top: 1px solid #D1D5DB; margin: 1.5rem 0; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #F9FAFB; }
::-webkit-scrollbar-thumb { background: #D1D5DB; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #6B7280; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# API KEY MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────
def load_env_keys():
    """Load Gemini API keys from environment OR Streamlit secrets (deploy)."""
    keys = []
    # 1. Environment variables (.env)
    for i in range(1, 9):
        k = os.getenv(f"GOOGLE_API_KEY_{i}", "").strip()
        if k:
            keys.append(k)
    single = os.getenv("GOOGLE_API_KEY", "").strip()
    if single and single not in keys:
        keys.append(single)

    # 2. Streamlit Cloud secrets fallback
    try:
        for i in range(1, 9):
            k = (st.secrets.get(f"GOOGLE_API_KEY_{i}", "") or "").strip()
            if k and k not in keys:
                keys.append(k)
        single2 = (st.secrets.get("GOOGLE_API_KEY", "") or "").strip()
        if single2 and single2 not in keys:
            keys.append(single2)
    except Exception:
        # st.secrets raises if no secrets file exists — that's fine.
        pass

    return keys


def get_next_key():
    exhausted = st.session_state.get("exhausted_keys", set())
    for k in st.session_state.get("ui_extra_keys", []):
        if k.strip() and k.strip() not in exhausted:
            return k.strip()
    for k in st.session_state.get("env_keys", []):
        if k.strip() and k.strip() not in exhausted:
            return k.strip()
    return None


def mark_key_exhausted(key):
    if key:
        st.session_state.exhausted_keys.add(key.strip())


def count_keys():
    exhausted = st.session_state.get("exhausted_keys", set())
    all_k = []
    for k in st.session_state.get("ui_extra_keys", []) + st.session_state.get("env_keys", []):
        if k.strip() and k.strip() not in all_k:
            all_k.append(k.strip())
    active = [k for k in all_k if k not in exhausted]
    return len(active), len(all_k)


def is_quota_error(e):
    msg = str(e).lower()
    return any(x in msg for x in ["quota", "429", "exhausted", "resource_exhausted", "rate"])


def _extract_text(content) -> str:
    """Normalize Gemini's content (string OR list of content-parts) to plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict):
                if c.get("type") == "text" and "text" in c:
                    parts.append(c["text"])
                elif "text" in c:
                    parts.append(c["text"])
            elif isinstance(c, str):
                parts.append(c)
        return "\n".join(p for p in parts if p)
    return str(content)


def _run_chatbot_turn(
    *,
    history_key: str,
    user_input: str,
    resume_text: str,
    ats_analysis: str,
    ats_score,
    job_description: str,
):
    """Append user msg, call the RAG chatbot, append assistant reply."""
    from agents.chat_agent import chat_about_resume
    from agents.llm import LLMClient

    st.session_state[history_key].append({"role": "user", "content": user_input})
    try:
        all_keys = (st.session_state.get("ui_extra_keys", [])
                    + st.session_state.get("env_keys", []))
        client = LLMClient(all_keys)
        client.exhausted = set(st.session_state.get("exhausted_keys", set()))
        reply = chat_about_resume(
            user_message=user_input,
            history=st.session_state[history_key][:-1],
            resume_text=resume_text,
            ats_analysis=ats_analysis,
            ats_score=ats_score,
            job_description=job_description,
            llm_client=client,
        )
        st.session_state.exhausted_keys = set(client.exhausted)
    except Exception as e:
        reply = f"⚠️ {e}"
    st.session_state[history_key].append({"role": "assistant", "content": reply})


def render_ats_chatbot(
    *,
    history_key: str,
    resume_text: str,
    ats_analysis: str,
    ats_score,
    job_description: str = "",
    button_label: str = "💬 Chat about ATS",
    suggested_label: str = "💡 Quick questions — click to auto-ask",
):
    """Right-aligned popover-style chatbot.

    A floating "Chat about ATS" button is placed in a narrow right column.
    Clicking opens a popover that holds the full chat — RAG-grounded on the
    user's resume.
    """
    from agents.chat_agent import SUGGESTED_QUESTIONS

    if history_key not in st.session_state or not isinstance(st.session_state[history_key], list):
        st.session_state[history_key] = []

    # Layout: empty spacer + right-aligned popover button
    _sp, btn_col = st.columns([5, 2])
    pending_key = f"_pending_{history_key}"

    with btn_col:
        st.markdown('<div class="btn-b">', unsafe_allow_html=True)
        # Older streamlit versions may lack popover — fall back to inline
        popover = getattr(st, "popover", None)
        if popover is not None:
            container = popover(button_label, use_container_width=True)
        else:
            with st.expander(button_label, expanded=False):
                container = st.container()
        st.markdown('</div>', unsafe_allow_html=True)

    with container:
        # Quick-question chips — click sends straight to LLM
        st.markdown(
            f"<p style='font-size:.78rem;color:#6B7280;margin:.2rem 0 .4rem;'>{esc(suggested_label)}</p>",
            unsafe_allow_html=True,
        )
        for i, sq in enumerate(SUGGESTED_QUESTIONS[:6]):
            if st.button(sq, key=f"{history_key}_sug_{i}", use_container_width=True):
                st.session_state[pending_key] = sq
                st.rerun()

        st.markdown("<hr style='margin:.5rem 0;'/>", unsafe_allow_html=True)

        # Render past conversation
        if not st.session_state[history_key]:
            st.markdown(
                "<p style='color:#9CA3AF;font-size:.8rem;font-style:italic;'>"
                "Ask anything about your ATS score, missing keywords, or improvements. "
                "Replies cite real excerpts from your resume (RAG).</p>",
                unsafe_allow_html=True,
            )
        for turn in st.session_state[history_key]:
            with st.chat_message(turn.get("role", "user")):
                st.markdown(turn.get("content", ""))

        # User input
        user_input = st.chat_input("Type your question…", key=f"{history_key}_input")

        # Handle pending quick-question auto-send
        if not user_input and st.session_state.get(pending_key):
            user_input = st.session_state.pop(pending_key)

        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Searching your resume + thinking…"):
                    _run_chatbot_turn(
                        history_key=history_key,
                        user_input=user_input,
                        resume_text=resume_text,
                        ats_analysis=ats_analysis,
                        ats_score=ats_score,
                        job_description=job_description,
                    )
                # Show the just-appended reply
                last = st.session_state[history_key][-1]
                if last.get("role") == "assistant":
                    st.markdown(last.get("content", ""))

        # Clear button
        if st.session_state[history_key]:
            if st.button("🗑 Clear chat", key=f"{history_key}_clear", use_container_width=True):
                st.session_state[history_key] = []
                st.rerun()


def call_llm(prompt: str, temperature: float = 0.3, use_flash_lite: bool = False) -> str:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage

    model_name = "gemini-flash-lite-latest" if use_flash_lite else "gemini-2.5-flash"

    for _ in range(8):
        key = get_next_key()
        if not key:
            raise RuntimeError("NO_KEYS")
        try:
            m = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=key,
                temperature=temperature,
                request_timeout=90,
            )
            return _extract_text(m.invoke([HumanMessage(content=prompt)]).content)
        except Exception as e:
            if is_quota_error(e):
                mark_key_exhausted(key)
                continue
            raise
    raise RuntimeError("ALL_EXHAUSTED")


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
def init():
    # env_keys is refreshed from disk on every rerun (below) — defaults here only
    # cover the first-load case.
    defs = {
        "env_keys":         [],
        "ui_extra_keys":    [],
        "exhausted_keys":   set(),
        "show_key_panel":   True,
        "personal_info":    {"first_name":"","last_name":"","location":"","mobile":"","email":"","linkedin":"","github":""},
        "education":        [],
        "experience":       [],
        "skills":           [],
        "projects":         [],
        "certifications":   [],
        "job_description":  "",
        "wf_statuses":      {f"a{i}":"wait" for i in range(1,7)},
        "agent_results":    {},
        "selected_template":0,
        "resume_pdf_bytes": None,
        "resume_filename":  "",
        "ats_score":        None,
        "pipeline_ran":     False,
        "show_hitl":        False,
        "human_approved":   False,
        "show_preview":     False,
        "post_content":     "",
        "upload_text":      "",
        "upload_analysis":  "",
        "upload_ats":       None,
        "opt_pdf":          None,
        "opt_draft":        "",
        "opt_fname":        "",
        "show_opt_preview": False,
        "auto_regenerate":  False,
        "insights":         {},
        # Interview questions (per tab)
        "iq_build_pdf":     None,
        "iq_build_set":     None,
        "iq_build_fname":   "",
        "iq_upload_pdf":    None,
        "iq_upload_set":    None,
        "iq_upload_fname":  "",
        # Extracted profile from uploaded resume (Pydantic → dict)
        "upload_profile":   None,
        "upload_missing":   [],
        # Chatbot history (per tab)
        "chat_build":       [],
        "chat_upload":      [],
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

init()

# ─────────────────────────────────────────────────────────────────────────────
# AUTH GATE — log in / sign up required (can be disabled by setting
# REQUIRE_LOGIN=false in the environment for local-only development)
# ─────────────────────────────────────────────────────────────────────────────
_auth_user = None
if os.getenv("REQUIRE_LOGIN", "true").lower() not in ("0", "false", "no"):
    try:
        from auth import require_login, render_logout_chip
        _auth_name, _auth_user = require_login()  # blocks page render until logged in
        render_logout_chip()
    except ModuleNotFoundError as _e:
        st.warning(
            f"⚠️ Auth dependencies missing ({_e}). "
            f"Install with: `pip install bcrypt` — or set `REQUIRE_LOGIN=false` in .env to skip."
        )

# Always refresh env_keys from .env on every rerun. If new keys appeared on
# disk, they take effect without needing to restart Streamlit.
_fresh_env_keys = load_env_keys()
if _fresh_env_keys != st.session_state.get("env_keys"):
    st.session_state.env_keys = _fresh_env_keys
    # Newly-added keys aren't exhausted by definition
    st.session_state.exhausted_keys = {
        k for k in st.session_state.get("exhausted_keys", set())
        if k in (_fresh_env_keys + st.session_state.get("ui_extra_keys", []))
    }

esc = lambda t: str(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h3 style='color:#F9FAFB;font-family:Syne,sans-serif;margin:0 0 2px;font-size:1.1rem;'>🚀 Resume Builder</h3>"
        "<p style='color:#6B7280;font-size:.73rem;margin:0 0 10px;'>AI-Powered · Google Gemini</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<hr/>", unsafe_allow_html=True)

    # Key counts
    active_c, total_c = count_keys()
    exhausted_c = total_c - active_c

    if total_c == 0:
        st.markdown(
            "<div style='background:#1C0A0A;border:1px solid #7F1D1D;border-radius:8px;"
            "padding:.55rem .85rem;font-size:.76rem;color:#FCA5A5;margin-bottom:.6rem;'>"
            "⚠️ No API keys.<br/>Paste keys below or add to <code>.env</code></div>",
            unsafe_allow_html=True,
        )
        # Auto-open panel when no keys
        st.session_state.show_key_panel = True
    elif active_c == 0:
        st.markdown(
            "<div style='background:#1C0A0A;border:1px solid #7F1D1D;border-radius:8px;"
            "padding:.55rem .85rem;font-size:.76rem;color:#FCA5A5;margin-bottom:.6rem;'>"
            "🔴 All keys exhausted.<br/>Paste new keys below.</div>",
            unsafe_allow_html=True,
        )
        st.session_state.show_key_panel = True
    else:
        st.markdown(
            f"<div style='background:#052E16;border:1px solid #166534;border-radius:8px;"
            f"padding:.55rem .85rem;font-size:.76rem;color:#86EFAC;margin-bottom:.6rem;'>"
            f"🟢 {active_c} active key{'s' if active_c!=1 else ''}"
            f"{'  🔴 '+str(exhausted_c)+' exhausted' if exhausted_c else ''}</div>",
            unsafe_allow_html=True,
        )

    # Key panel
    st.markdown(
        "<p style='color:#9CA3AF;font-size:.71rem;margin:.5rem 0 .3rem;line-height:1.5;'>"
        "One key per line. Keys rotate automatically.<br/>"
        "<a href='https://aistudio.google.com/app/apikey' target='_blank' style='color:#818CF8;'>Get free keys →</a></p>",
        unsafe_allow_html=True,
    )

    current_text = "\n".join([k for k in st.session_state.ui_extra_keys if k not in st.session_state.exhausted_keys])
    pasted = st.text_area(
        "Paste API Keys",
        value=current_text,
        height=110,
        key="sb_keys_area",
        placeholder="AIzaSy...\nAIzaSy...",
        label_visibility="collapsed",
    )

    col_save, col_clear = st.columns(2)
    with col_save:
        if st.button("💾 Save", key="sb_save", use_container_width=True):
            new_keys = []
            for line in pasted.replace(",", "\n").split("\n"):
                k = line.strip()
                if k and len(k) > 10:
                    new_keys.append(k)
            st.session_state.ui_extra_keys = new_keys
            st.session_state.exhausted_keys = set()
            for k in new_keys:
                st.session_state.exhausted_keys.discard(k)
            st.rerun()

    with col_clear:
        if st.button("🗑 Clear", key="sb_clear", use_container_width=True):
            st.session_state.ui_extra_keys = []
            st.session_state.exhausted_keys = set()
            st.rerun()

        if st.session_state.env_keys:
            st.markdown(
                f"<p style='color:#4B5563;font-size:.69rem;margin-top:.4rem;'>"
                f"📁 {len(st.session_state.env_keys)} key(s) from .env</p>",
                unsafe_allow_html=True,
            )

    st.markdown("<hr/>", unsafe_allow_html=True)

    # Info
    st.markdown(
        "<div style='font-size:.7rem;color:#4B5563;line-height:1.75;'>"
        "<b style='color:#6B7280;'>API Key Info</b><br/>"
        "• 1 full run ≈ 10 LLM calls<br/>"
        "• Free tier ≈ 10–15 calls/min<br/>"
        "• Keys auto-rotate on exhaustion<br/>"
        "• Recommend 2–4 keys<br/>"
        "• Set in <code>.env</code>:<br/>"
        "&nbsp;&nbsp;<code>GOOGLE_API_KEY_1=AIza…</code>"
        "</div>",
        unsafe_allow_html=True,
    )

    # Architecture badges
    try:
        from agents.tracing import is_active as _langsmith_active
        _ls_on = _langsmith_active()
    except Exception:
        _ls_on = False
    _ls_chip = (
        f"<span style='background:#052E16;border:1px solid #166534;color:#86EFAC;"
        f"border-radius:99px;padding:2px 8px;font-size:.65rem;font-weight:700;'>"
        f"LangSmith ON</span>"
        if _ls_on else
        f"<span style='background:#1F2937;border:1px solid #374151;color:#9CA3AF;"
        f"border-radius:99px;padding:2px 8px;font-size:.65rem;font-weight:700;'>"
        f"LangSmith OFF</span>"
    )
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:.7rem;color:#4B5563;line-height:1.85;'>"
        "<b style='color:#6B7280;'>Architecture</b><br/>"
        "<span style='background:#1E1B4B;border:1px solid #4338CA;color:#A5B4FC;"
        "border-radius:99px;padding:2px 8px;font-size:.65rem;font-weight:700;'>"
        "LangGraph</span> "
        "<span style='background:#172554;border:1px solid #1D4ED8;color:#93C5FD;"
        "border-radius:99px;padding:2px 8px;font-size:.65rem;font-weight:700;'>"
        "Chroma RAG</span> "
        f"{_ls_chip}"
        "<br/><span style='color:#6B7280;font-size:.68rem;'>"
        "6 agents · structured outputs · key rotation</span>"
        "</div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# WORKFLOW RENDERER
# ─────────────────────────────────────────────────────────────────────────────
WF_DEFS = [
    ("🎯","Agent 1 — Skill Intake",       "Receives & categorizes technical skills by domain"),
    ("🔍","Agent 2 — Skill Analysis",      "Analyzes relevance, gaps, market demand"),
    ("📝","Agent 3 — Resume Writer",       "Writes ATS-optimized resume via LLM"),
    ("✅","Agent 4 — ATS Scorer",          "Scores 0-100 using Gemini Flash Lite"),
    ("📁","Agent 5 — README Generator",   "Creates GitHub README workspace file"),
    ("💡","Agent 6 — Skill Roadmap",      "Role-based 3/6/12-month learning roadmap"),
]

def render_wf() -> str:
    html = "<div style='margin:.6rem 0;'>"
    for i,(icon,label,desc) in enumerate(WF_DEFS):
        s = st.session_state.wf_statuses.get(f"a{i+1}","wait")
        step_cls = f"wf-step { {'run':'wf-run','done':'wf-done','err':'wf-err'}.get(s,'') }"
        bdg_cls  = {"run":"b-run","done":"b-done","err":"b-err"}.get(s,"b-wait")
        bdg_txt  = {"run":"⏳ Running…","done":"✅ Done","err":"❌ Error"}.get(s,"○ Waiting")
        bg = {"run":"#F5F3FF","done":"#F0FDF4","err":"#FEF2F2"}.get(s,"#fff")
        bc = {"run":"#6C63FF","done":"#059669","err":"#DC2626"}.get(s,"#D1D5DB")
        html += (
            f"<div style='display:flex;align-items:center;gap:.65rem;padding:.5rem .9rem;"
            f"border-radius:9px;border:1px solid {bc};background:{bg};margin-bottom:.3rem;'>"
            f"<span style='font-size:1.1rem;'>{icon}</span>"
            f"<div style='flex:1;'>"
            f"<span style='font-weight:700;font-size:.84rem;color:#111827;'>{label}</span>"
            f"<span class='wf-badge {bdg_cls}'>{bdg_txt}</span><br/>"
            f"<span style='font-size:.72rem;color:#6B7280;'>{desc}</span>"
            f"</div></div>"
        )
    html += "</div>"
    return html


# ─────────────────────────────────────────────────────────────────────────────
# PAGE TITLE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<h2 style='font-family:Syne,sans-serif;font-size:1.8rem;font-weight:800;"
    "color:#111827;margin:0 0 .15rem;'>Resume Builder</h2>"
    "<p style='color:#6B7280;font-size:.88rem;margin:0 0 1.4rem;'>"
    "AI-powered · Fill your details and generate a professional resume</p>",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_build, tab_upload = st.tabs(["📝 Build Resume","📤 Analyze Existing Resume"])


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — BUILD
# ═════════════════════════════════════════════════════════════════════════════
with tab_build:

    # ── TOP-OF-TAB RAG CHATBOT — visible immediately, uses latest generated resume context ──
    render_ats_chatbot(
        history_key="chat_build",
        resume_text=st.session_state.get("agent_results", {}).get("resume_draft", "") or "",
        ats_analysis=st.session_state.get("agent_results", {}).get("ats_result", "") or "",
        ats_score=st.session_state.get("ats_score"),
        job_description=(st.session_state.get("job_description") or "").strip(),
        button_label="💬 RAG Coach — ask about your resume",
    )

    # ── Personal Info ──────────────────────────────────────────────────────────
    st.markdown("<div class='sec-title'>👤 Personal Information</div>", unsafe_allow_html=True)
    pi = st.session_state.personal_info
    c1,c2,c3 = st.columns(3)
    with c1: pi["first_name"] = st.text_input("First Name *", pi["first_name"], key="pi_fn")
    with c2: pi["last_name"]  = st.text_input("Last Name *",  pi["last_name"],  key="pi_ln")
    with c3: pi["location"]   = st.text_input("Location",     pi["location"],   key="pi_loc")
    c4,c5,c6,c7 = st.columns(4)
    with c4: pi["mobile"]   = st.text_input("Mobile",        pi["mobile"],   key="pi_mob")
    with c5: pi["email"]    = st.text_input("Email *",        pi["email"],    key="pi_em")
    with c6: pi["linkedin"] = st.text_input("LinkedIn URL",   pi["linkedin"], key="pi_li")
    with c7: pi["github"]   = st.text_input("GitHub URL",     pi["github"],   key="pi_gh")
    st.markdown('<hr class="div"/>', unsafe_allow_html=True)

    # ── Education ──────────────────────────────────────────────────────────────
    st.markdown("<div class='sec-title'>🎓 Education</div>", unsafe_allow_html=True)
    if not st.session_state.education:
        st.markdown("<div class='box-warn'>No education added yet.</div>", unsafe_allow_html=True)
    for i,edu in enumerate(st.session_state.education):
        st.markdown("<div class='entry-card'>", unsafe_allow_html=True)
        a,b,c,d = st.columns([2.5,2.5,1,.65])
        with a: st.session_state.education[i]["degree"]     = st.text_input("Degree",   edu["degree"],     key=f"ed_d_{i}")
        with b: st.session_state.education[i]["college"]    = st.text_input("College",  edu["college"],    key=f"ed_c_{i}")
        with c: st.session_state.education[i]["score"]      = st.text_input("CGPA/%",   edu["score"],      key=f"ed_s_{i}")
        with d:
            st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="btn-r">', unsafe_allow_html=True)
            if st.button("🗑", key=f"del_edu_{i}", use_container_width=True):
                st.session_state.education.pop(i); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        e,f,g = st.columns(3)
        with e: st.session_state.education[i]["start_date"] = st.text_input("Start Date", edu["start_date"], key=f"ed_sd_{i}")
        with f: st.session_state.education[i]["end_date"]   = st.text_input("End Date",   edu["end_date"],   key=f"ed_ed_{i}")
        with g: st.session_state.education[i]["location"]   = st.text_input("Location",   edu["location"],   key=f"ed_l_{i}")
        st.markdown("</div>", unsafe_allow_html=True)
    # Add button at bottom-left
    add_edu_col, _ = st.columns([2,5])
    with add_edu_col:
        st.markdown('<div class="btn-g">', unsafe_allow_html=True)
        if st.button("➕ Add Education", key="add_edu", use_container_width=True):
            st.session_state.education.append({"degree":"","college":"","score":"","start_date":"","end_date":"","location":""})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<hr class="div"/>', unsafe_allow_html=True)

    # ── Work Experience ────────────────────────────────────────────────────────
    st.markdown("<div class='sec-title'>💼 Work Experience</div>", unsafe_allow_html=True)
    if not st.session_state.experience:
        st.markdown("<div class='box-warn'>No experience added yet.</div>", unsafe_allow_html=True)
    for i,exp in enumerate(st.session_state.experience):
        st.markdown("<div class='entry-card'>", unsafe_allow_html=True)
        a,b,c = st.columns([2.5,2.5,.65])
        with a: st.session_state.experience[i]["company"]    = st.text_input("Company",            exp["company"],    key=f"xp_c_{i}")
        with b: st.session_state.experience[i]["role"]       = st.text_input("Role / Designation",  exp["role"],       key=f"xp_r_{i}")
        with c:
            st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="btn-r">', unsafe_allow_html=True)
            if st.button("🗑", key=f"del_exp_{i}", use_container_width=True):
                st.session_state.experience.pop(i); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        d,e = st.columns(2)
        with d: st.session_state.experience[i]["start_date"] = st.text_input("Start Date", exp["start_date"], key=f"xp_sd_{i}")
        with e: st.session_state.experience[i]["end_date"]   = st.text_input("End Date",   exp["end_date"],   key=f"xp_ed_{i}")
        st.session_state.experience[i]["description"] = st.text_area(
            "Key Responsibilities & Achievements", exp["description"], key=f"xp_de_{i}", height=80,
            placeholder="• Led development of...\n• Improved X by Y%...")
        st.markdown("</div>", unsafe_allow_html=True)
    add_exp_col, _ = st.columns([2,5])
    with add_exp_col:
        st.markdown('<div class="btn-g">', unsafe_allow_html=True)
        if st.button("➕ Add Experience", key="add_exp", use_container_width=True):
            st.session_state.experience.append({"company":"","role":"","start_date":"","end_date":"","description":""})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<hr class="div"/>', unsafe_allow_html=True)

    # ── Technical Skills ───────────────────────────────────────────────────────
    st.markdown("<div class='sec-title'>⚙️ Technical Skills</div>", unsafe_allow_html=True)
    if not st.session_state.skills:
        st.markdown("<div class='box-warn'>No skills added yet.</div>", unsafe_allow_html=True)
    for i,sk in enumerate(st.session_state.skills):
        st.markdown("<div class='skill-row'>", unsafe_allow_html=True)
        a,b,c,d = st.columns([3.5,1.3,1.3,.65])
        with a: st.session_state.skills[i]["name"]   = st.text_input("Skill Name", sk["name"],          key=f"sk_n_{i}", placeholder="e.g. Python, React, AWS…")
        with b: st.session_state.skills[i]["years"]  = st.number_input("Years",  value=int(sk["years"]),  min_value=0, max_value=30, key=f"sk_y_{i}")
        with c: st.session_state.skills[i]["months"] = st.number_input("Months", value=int(sk["months"]), min_value=0, max_value=11, key=f"sk_m_{i}")
        with d:
            st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="btn-r">', unsafe_allow_html=True)
            if st.button("🗑", key=f"del_sk_{i}", use_container_width=True):
                st.session_state.skills.pop(i); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    add_sk_col, _ = st.columns([2,5])
    with add_sk_col:
        st.markdown('<div class="btn-g">', unsafe_allow_html=True)
        if st.button("➕ Add Skill", key="add_sk", use_container_width=True):
            st.session_state.skills.append({"name":"","years":0,"months":0})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<hr class="div"/>', unsafe_allow_html=True)

    # ── Projects ───────────────────────────────────────────────────────────────
    st.markdown("<div class='sec-title'>🔨 Projects</div>", unsafe_allow_html=True)
    if not st.session_state.projects:
        st.markdown("<div class='box-warn'>No projects added yet.</div>", unsafe_allow_html=True)
    for i,pr in enumerate(st.session_state.projects):
        st.markdown("<div class='entry-card'>", unsafe_allow_html=True)
        a,b,c = st.columns([2.5,2.5,.65])
        with a: st.session_state.projects[i]["name"]        = st.text_input("Project Name",  pr["name"],        key=f"pr_n_{i}")
        with b: st.session_state.projects[i]["skills_used"] = st.text_input("Skills Used",   pr["skills_used"], key=f"pr_sk_{i}")
        with c:
            st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="btn-r">', unsafe_allow_html=True)
            if st.button("🗑", key=f"del_pr_{i}", use_container_width=True):
                st.session_state.projects.pop(i); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        d,e,f = st.columns(3)
        with d: st.session_state.projects[i]["start_date"] = st.text_input("Start Date",   pr["start_date"], key=f"pr_sd_{i}")
        with e: st.session_state.projects[i]["end_date"]   = st.text_input("End Date",     pr["end_date"],   key=f"pr_ed_{i}")
        with f: st.session_state.projects[i]["link"]       = st.text_input("Project Link", pr["link"],       key=f"pr_lk_{i}")
        st.session_state.projects[i]["summary"] = st.text_area(
            "Summary", pr["summary"], key=f"pr_su_{i}", height=70,
            placeholder="Describe the project, your role, and impact…")
        st.markdown("</div>", unsafe_allow_html=True)
    add_pr_col, _ = st.columns([2,5])
    with add_pr_col:
        st.markdown('<div class="btn-g">', unsafe_allow_html=True)
        if st.button("➕ Add Project", key="add_pr", use_container_width=True):
            st.session_state.projects.append({"name":"","skills_used":"","summary":"","start_date":"","end_date":"","link":""})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<hr class="div"/>', unsafe_allow_html=True)

    # ── Certifications ─────────────────────────────────────────────────────────
    st.markdown("<div class='sec-title'>🏆 Certifications</div>", unsafe_allow_html=True)
    if not st.session_state.certifications:
        st.markdown("<div class='box-warn'>No certifications added yet.</div>", unsafe_allow_html=True)
    for i,cert in enumerate(st.session_state.certifications):
        st.markdown("<div class='entry-card'>", unsafe_allow_html=True)
        a,b,c,d = st.columns([2.5,1.5,2,.65])
        with a: st.session_state.certifications[i]["name"] = st.text_input("Certification Name", cert["name"], key=f"ct_n_{i}")
        with b: st.session_state.certifications[i]["date"] = st.text_input("Date Received",       cert["date"], key=f"ct_d_{i}")
        with c: st.session_state.certifications[i]["link"] = st.text_input("Link / URL",          cert["link"], key=f"ct_l_{i}")
        with d:
            st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="btn-r">', unsafe_allow_html=True)
            if st.button("🗑", key=f"del_ct_{i}", use_container_width=True):
                st.session_state.certifications.pop(i); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    add_ct_col, _ = st.columns([2,5])
    with add_ct_col:
        st.markdown('<div class="btn-g">', unsafe_allow_html=True)
        if st.button("➕ Add Certification", key="add_cert", use_container_width=True):
            st.session_state.certifications.append({"name":"","date":"","link":""})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<hr class="div"/>', unsafe_allow_html=True)

    # ── Job Description ────────────────────────────────────────────────────────
    st.markdown("<div class='sec-title'>🎯 Job Description <span style='font-size:.72rem;font-weight:400;color:#6B7280;'>(optional)</span></div>", unsafe_allow_html=True)
    st.session_state.job_description = st.text_area(
        "jd", st.session_state.job_description, height=100,
        label_visibility="collapsed",
        placeholder="Paste the job description for ATS optimization and tailored resume…")
    st.markdown('<hr class="div"/>', unsafe_allow_html=True)

    # ── GENERATE ───────────────────────────────────────────────────────────────
    has_key  = bool(get_next_key())
    has_name = bool(pi.get("first_name","").strip())
    can_run  = has_key and has_name

    if not has_key:
        st.markdown("<div class='box-err'>🔴 No active API keys. Click <b>🔑 API Keys</b> in sidebar.</div>", unsafe_allow_html=True)
    elif not has_name:
        st.markdown("<div class='box-info'>ℹ️ Enter your First Name above to enable generation.</div>", unsafe_allow_html=True)

    gen_col, _ = st.columns([2,5])
    with gen_col:
        st.markdown('<div class="btn-a">', unsafe_allow_html=True)
        run_btn = st.button(
            "🚀 Generate Resume" if not st.session_state.pipeline_ran else "🔄 Regenerate",
            key="run_pipeline", use_container_width=True, disabled=not can_run)
        st.markdown("</div>", unsafe_allow_html=True)

    # Workflow placeholder
    wf_ph   = st.empty()
    prog_ph = st.empty()
    err_ph  = st.empty()

    if st.session_state.pipeline_ran or any(v!="wait" for v in st.session_state.wf_statuses.values()):
        wf_ph.markdown(render_wf(), unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # PIPELINE — LangGraph streaming
    # ─────────────────────────────────────────────────────────────────────────
    trigger_pipeline = run_btn or st.session_state.get("auto_regenerate", False)
    if trigger_pipeline and can_run:
        st.session_state.auto_regenerate = False
        st.session_state.wf_statuses     = {f"a{i}":"wait" for i in range(1,7)}
        st.session_state.show_hitl       = False
        st.session_state.human_approved  = False
        st.session_state.pipeline_ran    = False
        st.session_state.resume_pdf_bytes= None
        st.session_state.agent_results   = {}
        st.session_state.show_preview    = False
        st.session_state.insights        = {}

        profile = {
            "personal_info":   dict(pi),
            "education":       list(st.session_state.education),
            "experience":      list(st.session_state.experience),
            "skills":          list(st.session_state.skills),
            "projects":        list(st.session_state.projects),
            "certifications":  list(st.session_state.certifications),
            "job_description": st.session_state.job_description,
        }

        # Map LangGraph node names → workflow card IDs used by render_wf()
        NODE_TO_WF = {
            "agent1_skill_intake":      "a1",
            "agent2_skill_analysis":    "a2",
            "agent3_resume_generation": "a3",
            "agent4_resume_analyzer":   "a4",
            "agent5_readme_generator":  "a5",
            "agent6_skill_suggestions": "a6",
        }
        NODE_ORDER = list(NODE_TO_WF.keys())

        def mark(aid, s):
            st.session_state.wf_statuses[aid] = s
            wf_ph.markdown(render_wf(), unsafe_allow_html=True)

        prog = prog_ph.progress(0)

        try:
            from agents.llm import LLMClient
            from agents.graph import stream_pipeline

            # Build a fresh LLMClient from current session-state key pool
            all_keys = (st.session_state.get("ui_extra_keys", [])
                        + st.session_state.get("env_keys", []))
            llm_client = LLMClient(all_keys)
            llm_client.exhausted = set(st.session_state.get("exhausted_keys", set()))

            # Pre-mark the entry node as running so the UI shows immediate feedback
            mark("a1", "run"); prog.progress(0.05)

            final_state = {}
            running_idx = 0  # which node we expect to start next

            for node_name, accumulated in stream_pipeline(profile, llm_client):
                wf_id = NODE_TO_WF.get(node_name)
                if wf_id:
                    mark(wf_id, "done")
                final_state = accumulated

                # Advance the next node to "running"
                try:
                    finished_idx = NODE_ORDER.index(node_name)
                    next_idx = finished_idx + 1
                    if next_idx < len(NODE_ORDER):
                        mark(NODE_TO_WF[NODE_ORDER[next_idx]], "run")
                    prog.progress(min(1.0, (finished_idx + 1) / len(NODE_ORDER)))
                except ValueError:
                    pass

            # Sync exhausted key set back to session state
            st.session_state.exhausted_keys = set(llm_client.exhausted)

            # Map graph state → legacy agent_results keys (UI downstream depends on these)
            st.session_state.ats_score     = final_state.get("ats_score", 0)
            st.session_state.agent_results = {
                "categorized":    final_state.get("categorized_skills", ""),
                "skill_analysis": final_state.get("skill_analysis", ""),
                "jd_analysis":    final_state.get("jd_analysis", ""),
                "resume_draft":   final_state.get("resume_draft", ""),
                "ats_result":     final_state.get("ats_analysis", ""),
                "readme":         final_state.get("readme_content", ""),
                "roadmap_text":   final_state.get("roadmap_text", ""),
                "roadmap_parsed": final_state.get("roadmap_parsed", []),
                "level_map":      final_state.get("skill_level_map", {}),
                "retrieved_jds":  final_state.get("retrieved_jds", []),
                "llm_calls":      llm_client.call_count,
            }
            st.session_state.pipeline_ran = True
            st.session_state.show_hitl    = True

            prog_ph.empty()
            time.sleep(0.2)
            st.rerun()

        except RuntimeError as e:
            for k in st.session_state.wf_statuses:
                if st.session_state.wf_statuses[k] == "run":
                    st.session_state.wf_statuses[k] = "err"
            wf_ph.markdown(render_wf(), unsafe_allow_html=True)
            prog_ph.empty()
            msg = str(e)
            if "NO_KEYS" in msg:
                err_ph.error("❌ No active API keys. Add keys in the sidebar.")
            elif "ALL_EXHAUSTED" in msg:
                err_ph.error("🔴 All keys exhausted. Add new keys in the sidebar.")
            else:
                err_ph.error(f"❌ {msg}")
        except Exception as e:
            for k in st.session_state.wf_statuses:
                if st.session_state.wf_statuses[k] == "run":
                    st.session_state.wf_statuses[k] = "err"
            wf_ph.markdown(render_wf(), unsafe_allow_html=True)
            prog_ph.empty()
            if is_quota_error(e):
                mark_key_exhausted(get_next_key())
                err_ph.error("🔴 Key exhausted, rotating. Click Regenerate.")
            else:
                err_ph.error(f"❌ {e}")

    # ── INSIGHTS — shown before preview ───────────────────────────────────────
    if st.session_state.pipeline_ran and st.session_state.agent_results:
        st.markdown('<hr class="div"/>', unsafe_allow_html=True)
        st.markdown("<div class='sec-title'>💡 Insights &amp; Roadmap</div>", unsafe_allow_html=True)

        ar = st.session_state.agent_results
        roadmap_text = ar.get("roadmap_text","")

        # Parse key sections from roadmap_text for display
        def extract_section(text, header):
            pattern = rf"##\s*{re.escape(header)}(.*?)(?=\n##|\Z)"
            m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            return m.group(1).strip() if m else ""

        # Roles right now
        roles_now = extract_section(roadmap_text, "🎯 Roles You Can Apply For RIGHT NOW")
        if not roles_now:
            roles_now = extract_section(roadmap_text, "Roles You Can Apply For RIGHT NOW")

        # Domain
        domain_text = extract_section(roadmap_text, "🌐 Domain Identification")
        if not domain_text:
            domain_text = extract_section(roadmap_text, "Domain Identification")

        # Skills unlock
        skills_unlock = extract_section(roadmap_text, "📚 Skills That Unlock New Roles")
        if not skills_unlock:
            skills_unlock = extract_section(roadmap_text, "Skills That Unlock New Roles")

        # Cross domain
        cross_domain = extract_section(roadmap_text, "🔀 Cross-Domain Opportunities")

        # Roadmap phases
        m13 = extract_section(roadmap_text, "🗺️ Month 1-3")
        if not m13: m13 = extract_section(roadmap_text, "Month 1-3")
        m46 = extract_section(roadmap_text, "🗺️ Month 4-6")
        if not m46: m46 = extract_section(roadmap_text, "Month 4-6")
        m712= extract_section(roadmap_text, "🗺️ Month 7-12")
        if not m712: m712= extract_section(roadmap_text, "Month 7-12")

        # Display insights in cards
        if domain_text:
            st.markdown(
                f"<div class='insight-card'>"
                f"<div class='insight-title'>🌐 Your Technical Domain</div>"
                f"<div style='color:#374151;font-size:.88rem;line-height:1.7;'>{esc(domain_text).replace(chr(10),'<br/>')}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        if roles_now:
            st.markdown(
                f"<div class='insight-card'>"
                f"<div class='insight-title'>🎯 Roles You Can Apply For Right Now</div>"
                f"<div style='color:#374151;font-size:.87rem;line-height:1.75;'>{esc(roles_now).replace(chr(10),'<br/>')}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        if skills_unlock:
            st.markdown(
                f"<div class='insight-card'>"
                f"<div class='insight-title'>📚 Skills to Learn → Roles Unlocked</div>"
                f"<div style='color:#374151;font-size:.87rem;line-height:1.75;'>{esc(skills_unlock).replace(chr(10),'<br/>')}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        if cross_domain:
            st.markdown(
                f"<div class='insight-card'>"
                f"<div class='insight-title'>🔀 Cross-Domain Opportunities</div>"
                f"<div style='color:#374151;font-size:.87rem;line-height:1.75;'>{esc(cross_domain).replace(chr(10),'<br/>')}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        # Structured roadmap phases
        rp = ar.get("roadmap_parsed",[])
        if rp:
            st.markdown("<div class='insight-title' style='margin-top:.8rem;'>🗺️ Structured Learning Plan</div>", unsafe_allow_html=True)
            pc = st.columns(len(rp))
            clrs = ["#111827","#D97706","#059669","#1D4ED8"]
            for pidx, phase in enumerate(rp):
                with pc[pidx]:
                    clr   = clrs[pidx%len(clrs)]
                    items = "".join(f"<div style='padding:3px 0;font-size:.78rem;color:#374151;'>✦ {esc(it)}</div>" for it in phase.get("items",[]))
                    st.markdown(
                        f"<div style='background:#F9FAFB;border:1.5px solid {clr};border-radius:10px;padding:.85rem;'>"
                        f"<div style='color:{clr};font-weight:700;font-size:.8rem;margin-bottom:.5rem;'>📅 {esc(phase.get('phase',''))}</div>"
                        f"{items}</div>",
                        unsafe_allow_html=True,
                    )

        # Skill bars
        sk_all = st.session_state.skills
        if sk_all:
            st.markdown("<div class='insight-title' style='margin-top:1rem;'>⚙️ Your Skills Overview</div>", unsafe_allow_html=True)
            bc1, bc2 = st.columns(2)
            for idx,sk in enumerate(sk_all):
                y = int(sk.get("years",0)); mo = int(sk.get("months",0))
                tot = y*12+mo; pct = min(100,int((tot/60)*100))
                lbl = f"{y}y {mo}m" if y>0 else f"{mo}m"
                bc  = "#111827" if pct>=70 else "#D97706" if pct>=35 else "#6B7280"
                with (bc1 if idx%2==0 else bc2):
                    st.markdown(
                        f"<div class='sk-bar'>"
                        f"<div class='sk-bar-top'><span style='font-weight:500;'>{esc(sk.get('name',''))}</span><span style='color:#6B7280;'>{lbl}</span></div>"
                        f"<div class='sk-bar-bg'><div class='sk-bar-fill' style='width:{pct}%;background:{bc};'></div></div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

    # ── PREVIEW & HITL ────────────────────────────────────────────────────────
    if st.session_state.pipeline_ran and st.session_state.agent_results.get("resume_draft"):
        st.markdown('<hr class="div"/>', unsafe_allow_html=True)

        hdr1, hdr2, hdr3 = st.columns([4,1.5,1.5])
        with hdr1:
            st.markdown("<div class='sec-title'>📄 Resume Preview</div>", unsafe_allow_html=True)
        with hdr2:
            st.markdown('<div class="btn-b">', unsafe_allow_html=True)
            if st.button("👁️ Toggle Preview", key="toggle_prev", use_container_width=True):
                st.session_state.show_preview = not st.session_state.get("show_preview",False)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with hdr3:
            st.markdown('<div class="btn-a">', unsafe_allow_html=True)
            if st.button("🔄 Regenerate", key="regen_btn", use_container_width=True):
                st.session_state.pipeline_ran   = False
                st.session_state.show_hitl      = False
                st.session_state.human_approved = False
                st.session_state.show_preview   = False
                st.session_state.wf_statuses    = {f"a{i}":"wait" for i in range(1,7)}
                st.session_state.auto_regenerate = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.get("show_preview",False):
            st.markdown("<div class='preview-box'>", unsafe_allow_html=True)
            st.markdown(st.session_state.agent_results.get("resume_draft",""))
            st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.show_hitl and not st.session_state.human_approved:
        st.markdown(
            "<div style='background:#F5F3FF;border:1.5px solid #6C63FF;border-radius:10px;"
            "padding:1rem 1.3rem;margin:1rem 0 .8rem;'>"
            "<b style='color:#4C1D95;'>🔍 Review &amp; Edit before downloading</b><br/>"
            "<span style='color:#6B7280;font-size:.82rem;'>Edit the draft below. Your changes will be used for PDF generation.</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        draft  = st.session_state.agent_results.get("resume_draft","")
        edited = st.text_area("Resume Draft:", draft, height=380, key="hitl_edit")
        hc1, hc2, _ = st.columns([2,2,3])
        with hc1:
            st.markdown('<div class="btn-t">', unsafe_allow_html=True)
            if st.button("✅ Approve & Continue", key="approve_btn", use_container_width=True):
                st.session_state.agent_results["resume_draft"] = edited
                st.session_state.human_approved = True
                st.session_state.show_hitl      = False
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with hc2:
            st.markdown('<div class="btn-r">', unsafe_allow_html=True)
            if st.button("🔄 Reject & Redo", key="reject_btn", use_container_width=True):
                st.session_state.show_hitl      = False
                st.session_state.human_approved = False
                st.session_state.pipeline_ran   = False
                st.session_state.wf_statuses    = {f"a{i}":"wait" for i in range(1,7)}
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # ── TEMPLATES & DOWNLOAD ───────────────────────────────────────────────────
    if st.session_state.human_approved:
        st.markdown('<hr class="div"/>', unsafe_allow_html=True)
        st.markdown("<div class='sec-title'>📄 Templates &amp; Download</div>", unsafe_allow_html=True)

        if st.session_state.ats_score is not None:
            sc  = st.session_state.ats_score
            col = "#059669" if sc>=80 else "#D97706" if sc>=60 else "#DC2626"
            lbl = "Excellent ✨" if sc>=80 else "Good 👍" if sc>=60 else "Needs Work ⚠️"
            st.markdown(
                f"<div class='ats-box'>"
                f"<div style='font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:#6B7280;margin-bottom:.2rem;'>ATS Score (via Gemini Flash Lite)</div>"
                f"<div style='font-family:Syne,sans-serif;font-size:3.5rem;font-weight:800;color:{col};line-height:1.1;'>{sc}<span style='font-size:1.6rem;'>%</span></div>"
                f"<div style='color:{col};font-weight:700;font-size:.9rem;'>{lbl}</div>"
                f"<div style='background:#E5E7EB;border-radius:99px;height:6px;max-width:230px;margin:.5rem auto 0;'>"
                f"<div style='width:{sc}%;height:6px;border-radius:99px;background:{col};'></div></div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        TEMPLATES = [
            {"name":"Dark Header Classic", "desc":"Dark band · serif · red accents",   "c1":"#2D2D2D","c2":"#C0392B","icon":"🏛️"},
            {"name":"Two-Column Modern",   "desc":"Grey sidebar · two-column · clean", "c1":"#1A1A1A","c2":"#444444","icon":"📋"},
            {"name":"Academic Minimal",    "desc":"Centered · blue icons · clean",     "c1":"#1E3A5F","c2":"#2563EB","icon":"🎓"},
            {"name":"Institute Format",    "desc":"Left-right header · compact",       "c1":"#111827","c2":"#374151","icon":"🏫"},
            {"name":"Bold Professional",   "desc":"Large name · clean bullets",        "c1":"#111827","c2":"#6B7280","icon":"⚡"},
        ]

        tc = st.columns(5)
        for i,tmpl in enumerate(TEMPLATES):
            with tc[i]:
                sel  = st.session_state.selected_template==i
                bord = "#111827" if sel else "#D1D5DB"
                chk  = "✅" if sel else ""
                st.markdown(
                    f"<div class='tmpl-card {'sel' if sel else ''}' style='border-color:{bord};'>"
                    f"<div style='height:85px;background:linear-gradient(135deg,{tmpl['c1']},{tmpl['c2']});"
                    f"display:flex;align-items:center;justify-content:center;flex-direction:column;"
                    f"gap:3px;position:relative;'>"
                    f"<span style='font-size:1.8rem;'>{tmpl['icon']}</span>"
                    f"<span style='color:#fff;font-size:.58rem;font-weight:700;text-align:center;padding:0 4px;'>{tmpl['name']}</span>"
                    f"<span style='position:absolute;top:4px;right:5px;font-size:.8rem;'>{chk}</span>"
                    f"</div>"
                    f"<div style='padding:.4rem .5rem;background:#fff;'>"
                    f"<small style='color:#6B7280;font-size:.62rem;'>{tmpl['desc']}</small></div></div>",
                    unsafe_allow_html=True,
                )
                if st.button("✅ Selected" if sel else "Select", key=f"tmpl_{i}", use_container_width=True):
                    st.session_state.selected_template=i
                    st.session_state.resume_pdf_bytes=None
                    st.rerun()

        st.markdown(
            f"<p style='color:#6B7280;font-size:.8rem;margin:.4rem 0 .8rem;'>"
            f"Selected: <b style='color:#111;'>{TEMPLATES[st.session_state.selected_template]['name']}</b></p>",
            unsafe_allow_html=True,
        )

        dl1, dl2, _ = st.columns([2,2,3])
        with dl1:
            st.markdown('<div class="btn-a">', unsafe_allow_html=True)
            gen_pdf = st.button("🖨️ Generate PDF", key="gen_pdf", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with dl2:
            if st.session_state.resume_pdf_bytes:
                st.download_button("⬇️ Download PDF",
                    st.session_state.resume_pdf_bytes,
                    file_name=st.session_state.resume_filename,
                    mime="application/pdf",
                    use_container_width=True, key="dl_main")
            else:
                st.markdown(
                    "<div style='background:#F9FAFB;border:1.5px dashed #D1D5DB;border-radius:8px;"
                    "padding:.5rem .8rem;text-align:center;color:#9CA3AF;font-size:.8rem;'>⬇️ Generate first</div>",
                    unsafe_allow_html=True,
                )

        if gen_pdf:
            with st.spinner("Building PDF…"):
                try:
                    from utils.pdf_generator import generate_resume_pdf
                    pi_now = pi
                    role_0 = st.session_state.experience[0].get("role","") if st.session_state.experience else ""
                    fname  = f"{pi_now.get('first_name','')}{pi_now.get('last_name','')}{re.sub(r'[^A-Za-z0-9]','',role_0)}.pdf"
                    pdf_b  = generate_resume_pdf(
                        profile_data={
                            "personal_info":  dict(pi_now),
                            "education":      list(st.session_state.education),
                            "experience":     list(st.session_state.experience),
                            "skills":         list(st.session_state.skills),
                            "projects":       list(st.session_state.projects),
                            "certifications": list(st.session_state.certifications),
                        },
                        resume_draft=st.session_state.agent_results.get("resume_draft",""),
                        template_id=st.session_state.selected_template,
                    )
                    st.session_state.resume_pdf_bytes=pdf_b
                    st.session_state.resume_filename=fname
                    st.markdown(f"<div class='box-ok'>✅ <b>{fname}</b> ready!</div>", unsafe_allow_html=True)
                    st.rerun()
                except Exception as e:
                    st.error(f"PDF error: {e}")

        with st.expander("⚡ Generate all 5 templates"):
            qa = st.columns(5)
            for i,tmpl in enumerate(TEMPLATES):
                with qa[i]:
                    st.markdown(f"<div style='font-size:.7rem;font-weight:600;text-align:center;margin-bottom:.3rem;'>{tmpl['icon']} {tmpl['name']}</div>", unsafe_allow_html=True)
                    if st.button(f"Build #{i+1}", key=f"qg_{i}", use_container_width=True):
                        with st.spinner("Building…"):
                            try:
                                from utils.pdf_generator import generate_resume_pdf
                                piq = pi
                                rq  = st.session_state.experience[0].get("role","") if st.session_state.experience else ""
                                fnq = f"{piq.get('first_name','')}{piq.get('last_name','')}{re.sub(r'[^A-Za-z0-9]','',rq)}_T{i+1}.pdf"
                                pdq = generate_resume_pdf(
                                    profile_data={"personal_info":dict(piq),"education":list(st.session_state.education),
                                                  "experience":list(st.session_state.experience),"skills":list(st.session_state.skills),
                                                  "projects":list(st.session_state.projects),"certifications":list(st.session_state.certifications)},
                                    resume_draft=st.session_state.agent_results.get("resume_draft",""),
                                    template_id=i,
                                )
                                st.session_state[f"qpdf_{i}"]=pdq
                                st.session_state[f"qname_{i}"]=fnq
                            except Exception as ex:
                                st.error(str(ex))
                    if st.session_state.get(f"qpdf_{i}"):
                        st.download_button("⬇️ Download",st.session_state[f"qpdf_{i}"],
                            file_name=st.session_state[f"qname_{i}"],mime="application/pdf",
                            key=f"qdl_{i}",use_container_width=True)

        st.markdown('<hr class="div"/>', unsafe_allow_html=True)
        ot1,ot2,ot3,ot4 = st.tabs(["📊 Skill Analysis","📁 README","🎯 JD Match","✅ ATS Details"])
        with ot1: st.markdown(st.session_state.agent_results.get("skill_analysis",""))
        with ot2:
            rd = st.session_state.agent_results.get("readme","")
            st.code(rd, language="markdown")
            if rd: st.download_button("⬇️ README.md",rd,file_name="README.md",mime="text/markdown",key="dl_readme")
        with ot3:
            jda = st.session_state.agent_results.get("jd_analysis","")
            st.markdown(jda if jda else "_No job description provided._")
        with ot4:
            st.markdown(st.session_state.agent_results.get("ats_result",""))

        # Note: the RAG chatbot lives at the top of this tab (always visible).
        # It auto-picks up the resume draft + ATS analysis from session state.

        # ── INTERVIEW QUESTIONS ────────────────────────────────────────────────
        st.markdown('<hr class="div"/>', unsafe_allow_html=True)
        st.markdown("<div class='sec-title'>🎤 Interview Question Set</div>", unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#6B7280;font-size:.85rem;margin-bottom:.6rem;'>"
            "Generate a tailored interview Q&A based on your actual skills, experience, and projects. "
            "Download as a styled PDF for prep or sharing with interviewers.</p>",
            unsafe_allow_html=True,
        )

        iq_c1, iq_c2 = st.columns([2, 2])
        with iq_c1:
            st.markdown('<div class="btn-b">', unsafe_allow_html=True)
            gen_iq = st.button(
                "🎤 Generate Interview Questions PDF",
                key="gen_iq_build", use_container_width=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)
        with iq_c2:
            if st.session_state.get("iq_build_pdf"):
                st.download_button(
                    "⬇️ Download Interview PDF",
                    st.session_state["iq_build_pdf"],
                    file_name=st.session_state.get("iq_build_fname", "interview_questions.pdf"),
                    mime="application/pdf",
                    use_container_width=True, key="dl_iq_build",
                )
            else:
                st.markdown(
                    "<div style='background:#F9FAFB;border:1.5px dashed #D1D5DB;border-radius:8px;"
                    "padding:.5rem .8rem;text-align:center;color:#9CA3AF;font-size:.8rem;'>"
                    "⬇️ Generate first</div>", unsafe_allow_html=True,
                )

        if gen_iq:
            iq_status   = st.empty()
            iq_progress = st.progress(0)

            def _iq_cb(stage, done, total):
                iq_status.markdown(
                    f"<div class='box-info'>{esc(stage)} — step {done}/{total}</div>",
                    unsafe_allow_html=True,
                )
                iq_progress.progress(min(1.0, done / max(total, 1)))

            try:
                from agents.llm import LLMClient
                from agents.interview_agent import generate_interview_questions
                from utils.interview_pdf import generate_interview_pdf

                all_keys = (st.session_state.get("ui_extra_keys", [])
                            + st.session_state.get("env_keys", []))
                client = LLMClient(all_keys)
                client.exhausted = set(st.session_state.get("exhausted_keys", set()))

                profile_now = {
                    "personal_info":   dict(pi),
                    "education":       list(st.session_state.education),
                    "experience":      list(st.session_state.experience),
                    "skills":          list(st.session_state.skills),
                    "projects":        list(st.session_state.projects),
                    "certifications":  list(st.session_state.certifications),
                    "job_description": st.session_state.job_description,
                }
                qset = generate_interview_questions(
                    profile_now,
                    resume_draft=st.session_state.agent_results.get("resume_draft", ""),
                    llm_client=client,
                    progress_cb=_iq_cb,
                )
                cand_name = f"{pi.get('first_name','')} {pi.get('last_name','')}".strip()
                pdf_bytes = generate_interview_pdf(qset, candidate_name=cand_name)

                # namerole filename
                first_role = ""
                if st.session_state.experience:
                    first_role = (st.session_state.experience[0].get("role") or "")
                if not first_role:
                    first_role = qset.target_role or "Interview"
                fname = (
                    f"{pi.get('first_name','')}{pi.get('last_name','')}"
                    f"{re.sub(r'[^A-Za-z0-9]','', first_role)}_questions.pdf"
                )

                st.session_state["iq_build_set"]   = qset
                st.session_state["iq_build_pdf"]   = pdf_bytes
                st.session_state["iq_build_fname"] = fname
                st.session_state.exhausted_keys = set(client.exhausted)
                iq_progress.empty(); iq_status.empty()
                st.rerun()
            except Exception as e:
                iq_progress.empty(); iq_status.empty()
                if is_quota_error(e):
                    mark_key_exhausted(get_next_key())
                    st.error("🔴 Key exhausted. Try again.")
                else:
                    st.error(f"❌ {e}")

        # Inline preview (collapsible) — new per-skill tier layout
        if st.session_state.get("iq_build_set"):
            qset = st.session_state["iq_build_set"]
            total_q = qset.total_questions()
            with st.expander(
                f"👁️ Preview — {total_q} questions across {len(qset.skill_questions)} skills + 4 common categories"
            ):
                if qset.candidate_summary:
                    st.markdown(f"**Candidate brief:** {qset.candidate_summary}")
                for sq in qset.skill_questions:
                    st.markdown(f"#### 🧠 {sq.skill_name}  _({sq.total()} questions)_")
                    for tier_name, qs in [("Basic", sq.basic), ("Intermediate", sq.intermediate), ("Expert", sq.expert)]:
                        if not qs: continue
                        st.markdown(f"**{tier_name}**")
                        for i, q in enumerate(qs, 1):
                            st.markdown(f"- **Q{i}.** {q.question}")
                            if q.answer:
                                st.caption(f"Answer: {q.answer}")
                for title, qs in [
                    ("Behavioral / Situational", qset.behavioral),
                    ("Project Deep-Dive",         qset.project_deep_dive),
                    ("System Design",             qset.system_design),
                    ("Role-Specific",             qset.role_specific),
                ]:
                    if not qs: continue
                    st.markdown(f"#### {title}")
                    for i, q in enumerate(qs, 1):
                        st.markdown(f"- **Q{i}** _({q.difficulty})_ — {q.question}")
                        if q.answer:
                            st.caption(f"Answer: {q.answer}")

    # ── POST GENERATOR ─────────────────────────────────────────────────────────
    st.markdown('<hr class="div"/>', unsafe_allow_html=True)
    st.markdown("<div class='sec-title'>📢 Social Media Post Generator</div>", unsafe_allow_html=True)

    if not get_next_key() or not pi.get("first_name","").strip():
        st.markdown("<div class='box-info'>Add API key in sidebar and enter your name to generate posts.</div>", unsafe_allow_html=True)
    else:
        pg1,pg2 = st.columns(2)
        with pg1: platform  = st.selectbox("Platform",["LinkedIn","Naukri","Indeed","Unstop","Twitter/X"],key="post_plat")
        with pg2: post_type = st.selectbox("Post Type",["Open to Work","New Role Announcement","Skills Showcase","Project Highlight","Achievement","Career Change","Learning Journey"],key="post_type_sel")

        pcol,_ = st.columns([2,5])
        with pcol:
            st.markdown('<div class="btn-a">', unsafe_allow_html=True)
            gen_post = st.button("✨ Generate Post", key="gen_post_btn", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if gen_post:
            with st.spinner("Writing your post…"):
                try:
                    nm  = f"{pi.get('first_name','')} {pi.get('last_name','')}".strip()
                    sks = [s.get("name","") for s in st.session_state.skills[:8] if s.get("name")]
                    rls = [e.get("role","") for e in st.session_state.experience[:2] if e.get("role")]
                    cos = [e.get("company","") for e in st.session_state.experience[:2] if e.get("company")]
                    GUIDES = {
                        "LinkedIn":  {"tone":"professional yet personal","len":"150-300 words","tags":5,"style":"Hook first line. Story arc. Strong CTA. 1-2 emojis."},
                        "Naukri":    {"tone":"direct professional","len":"100-180 words","tags":3,"style":"Lead with experience years. Prominent skills. Location."},
                        "Indeed":    {"tone":"factual","len":"80-140 words","tags":2,"style":"Bullet qualifications. Target role clear."},
                        "Unstop":    {"tone":"energetic ambitious","len":"100-180 words","tags":6,"style":"Emojis freely 🚀🔥. Highlight energy and projects."},
                        "Twitter/X": {"tone":"punchy witty","len":"<270 chars or thread","tags":3,"style":"Hook in 5 words. Thread if needed."},
                    }
                    g = GUIDES.get(platform, GUIDES["LinkedIn"])
                    post_txt = call_llm(f"""Professional social media career content creator.
Create authentic {platform} post for:
Name: {nm}
Purpose: {post_type}
Skills: {', '.join(sks)}
Roles: {', '.join(rls)}
Companies: {', '.join(cos)}
Tone: {g['tone']}, Length: {g['len']}, Style: {g['style']}
Use exactly {g['tags']} relevant hashtags at end.
Sound like a real human. Output ONLY the post text.
""", temperature=0.8)
                    st.session_state.post_content = post_txt
                except Exception as e:
                    if is_quota_error(e):
                        mark_key_exhausted(get_next_key())
                        st.error("🔴 Key exhausted. Click Generate again.")
                    else:
                        st.error(f"Error: {e}")

        if st.session_state.post_content:
            st.markdown(f"<div class='post-box'>{esc(st.session_state.post_content)}</div>", unsafe_allow_html=True)
            pd1,pd2 = st.columns([2,2])
            with pd1:
                st.download_button("📥 Download Post",st.session_state.post_content,
                    file_name=f"post_{platform.lower().replace('/','_')}.txt",
                    mime="text/plain",use_container_width=True,key="dl_post")
            with pd2:
                st.markdown('<div class="btn-r">', unsafe_allow_html=True)
                if st.button("🔄 Regenerate Post", key="regen_post", use_container_width=True):
                    st.session_state.post_content=""
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — UPLOAD & ANALYZE
# ═════════════════════════════════════════════════════════════════════════════
with tab_upload:
    # ── TOP-OF-TAB RAG CHATBOT — visible immediately, uses uploaded resume context ──
    render_ats_chatbot(
        history_key="chat_upload",
        resume_text=st.session_state.get("upload_text", "") or "",
        ats_analysis=st.session_state.get("upload_analysis", "") or "",
        ats_score=st.session_state.get("upload_ats"),
        job_description=(st.session_state.get("upload_jd") or "").strip(),
        button_label="💬 RAG Coach — ask about your resume",
    )

    st.markdown("<div class='sec-title'>📤 Analyze Existing Resume</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B7280;font-size:.86rem;margin-bottom:1rem;'>Upload your PDF. AI extracts content, scores ATS, finds gaps, suggests roles and roadmap.</p>", unsafe_allow_html=True)

    if not get_next_key():
        st.markdown("<div class='box-warn'>⚠️ Add API key in sidebar first.</div>", unsafe_allow_html=True)
    else:
        uploaded = st.file_uploader("Upload Resume PDF", type=["pdf"],
                                     key="resume_upload", label_visibility="collapsed")

        if uploaded:
            file_bytes = uploaded.getvalue()
            st.markdown("<div class='box-ok'>✅ File received.</div>", unsafe_allow_html=True)

            up_c1,up_c2 = st.columns(2)
            with up_c1:
                upload_jd = st.text_area("Job Description / Role (optional)",
                    height=90, key="upload_jd",
                    placeholder="Paste JD or type a role e.g. 'Senior Python Developer'\nLeave blank for general ATS score.")
            with up_c2:
                st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
                st.markdown(
                    "<div class='box-info'><b>You'll get:</b><br/>"
                    "• ATS score (Gemini Flash Lite)<br/>"
                    "• Skills found &amp; gaps<br/>"
                    "• Roles you qualify for now<br/>"
                    "• Learn X → Unlock roles<br/>"
                    "• Optimized resume download</div>",
                    unsafe_allow_html=True,
                )

            acol,_ = st.columns([2,5])
            with acol:
                st.markdown('<div class="btn-a">', unsafe_allow_html=True)
                analyze_btn = st.button("🔍 Analyze Resume", key="analyze_upload", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

            if analyze_btn:
                with st.spinner("Extracting and analyzing…"):
                    try:
                        from utils.resume_parser import extract_text_from_pdf
                        raw_text = extract_text_from_pdf(file_bytes)
                        if not raw_text.strip():
                            st.error("❌ Cannot extract text. Use a text-based PDF.")
                        else:
                            st.session_state.upload_text = raw_text
                            ujd = upload_jd.strip() if upload_jd and upload_jd.strip() else ""

                            # ── Structured extraction → full profile (name, email, edu, exp, skills, projects, certs)
                            try:
                                from agents.llm import LLMClient
                                from agents.resume_extractor import extract_resume

                                ex_keys = (st.session_state.get("ui_extra_keys", [])
                                           + st.session_state.get("env_keys", []))
                                ex_client = LLMClient(ex_keys)
                                ex_client.exhausted = set(st.session_state.get("exhausted_keys", set()))
                                extraction = extract_resume(raw_text, ex_client)
                                st.session_state.upload_profile = extraction.to_profile()
                                st.session_state.upload_missing = extraction.missing_sections()
                                st.session_state.exhausted_keys = set(ex_client.exhausted)
                            except Exception as ex_e:
                                st.warning(f"⚠️ Could not auto-extract profile fields: {ex_e}")
                                st.session_state.upload_profile = None
                                st.session_state.upload_missing = []

                            result = call_llm(f"""Senior ATS expert and career coach.
Analyze this resume:

RESUME TEXT:
{raw_text[:4500]}

{"TARGET ROLE/JD:" + chr(10) + ujd if ujd else "No JD — give general assessment."}

Output ALL sections with clear headings:

## ATS_SCORE: [0-100]

## Candidate Profile Summary
2-3 sentences about this candidate.

## Skills Identified
Categorized list of all skills found.

{"## JD Match Analysis" + chr(10) + "Required: ✅ has / ❌ missing | Match%" if ujd else "## Profile Strength Assessment"}

## ATS Issues Found
Format and keyword problems.

## Roles You Can Apply For RIGHT NOW
Role | Match% | Qualifying skills (list 6-8)

## Learn X → Unlock These Roles
"Learn [Skill] (est time) → Eligible: Role1, Role2" (list 8-10)

## Learning Roadmap
Month 1-3: ...
Month 4-6: ...
Month 7-12: ...

## Top 5 Resume Improvements

## Overall Recommendation
""", use_flash_lite=True)
                            result = _extract_text(result)  # defensive: in case any cached path returned a list
                            st.session_state.upload_analysis = result
                            m3 = re.search(r"ATS_SCORE:\s*(\d+)", result)
                            if m3: st.session_state.upload_ats = min(100,max(0,int(m3.group(1))))
                            st.rerun()

                    except Exception as e:
                        if is_quota_error(e):
                            mark_key_exhausted(get_next_key())
                            st.error("🔴 Key exhausted. Try again.")
                        else:
                            st.error(f"Error: {e}")

        if st.session_state.upload_analysis:
            # Defensive: normalize any stale list-format value left in session state
            if not isinstance(st.session_state.upload_analysis, str):
                st.session_state.upload_analysis = _extract_text(st.session_state.upload_analysis)
            st.markdown('<hr class="div"/>', unsafe_allow_html=True)

            # ATS Score
            if st.session_state.upload_ats is not None:
                usc  = st.session_state.upload_ats
                ucol = "#059669" if usc>=80 else "#D97706" if usc>=60 else "#DC2626"
                ulbl = "Excellent ✨" if usc>=80 else "Good 👍" if usc>=60 else "Needs Work ⚠️"
                st.markdown(
                    f"<div class='ats-box'>"
                    f"<div style='font-size:.7rem;text-transform:uppercase;letter-spacing:.1em;color:#6B7280;margin-bottom:.2rem;'>Uploaded Resume ATS Score</div>"
                    f"<div style='font-family:Syne,sans-serif;font-size:3.5rem;font-weight:800;color:{ucol};line-height:1.1;'>{usc}<span style='font-size:1.7rem;'>%</span></div>"
                    f"<div style='color:{ucol};font-weight:700;font-size:.9rem;'>{ulbl}</div>"
                    f"<div style='background:#E5E7EB;border-radius:99px;height:6px;max-width:240px;margin:.5rem auto 0;'>"
                    f"<div style='width:{usc}%;height:6px;border-radius:99px;background:{ucol};'></div></div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            # Analysis — rendered with correct colors
            st.markdown("<div class='analysis-box'>", unsafe_allow_html=True)
            st.markdown(st.session_state.upload_analysis)
            st.markdown("</div>", unsafe_allow_html=True)

            # ── Extracted details from uploaded resume ─────────────────────────
            if st.session_state.upload_profile:
                up = st.session_state.upload_profile
                pi_up   = up.get("personal_info", {}) or {}
                missing = st.session_state.upload_missing or []

                st.markdown('<hr class="div"/>', unsafe_allow_html=True)
                st.markdown("<div class='sec-title'>📋 Extracted Details</div>", unsafe_allow_html=True)

                if missing:
                    st.markdown(
                        f"<div class='box-warn'>⚠️ The following sections are missing or incomplete in your "
                        f"uploaded resume: <b>{', '.join(missing)}</b>. The optimized PDF will still generate, "
                        f"but adding these will significantly improve your ATS score.</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        "<div class='box-ok'>✅ All key sections were detected in your resume.</div>",
                        unsafe_allow_html=True,
                    )

                with st.expander("👁️ Preview extracted profile", expanded=False):
                    cA, cB = st.columns(2)
                    with cA:
                        st.markdown(f"**Name:** {pi_up.get('first_name','')} {pi_up.get('last_name','')}")
                        st.markdown(f"**Email:** {pi_up.get('email','—')}")
                        st.markdown(f"**Mobile:** {pi_up.get('mobile','—')}")
                        st.markdown(f"**Location:** {pi_up.get('location','—')}")
                    with cB:
                        st.markdown(f"**LinkedIn:** {pi_up.get('linkedin','—')}")
                        st.markdown(f"**GitHub:** {pi_up.get('github','—')}")
                        st.markdown(f"**Education entries:** {len(up.get('education',[]))}")
                        st.markdown(f"**Experience entries:** {len(up.get('experience',[]))}")
                        st.markdown(f"**Skills:** {len(up.get('skills',[]))}  ·  **Projects:** {len(up.get('projects',[]))}  ·  **Certifications:** {len(up.get('certifications',[]))}")
                    if up.get("skills"):
                        st.caption("Skills detected: " + ", ".join(s.get("name","") for s in up["skills"] if s.get("name")))

            # Generate optimized
            st.markdown('<hr class="div"/>', unsafe_allow_html=True)
            st.markdown("<div class='sec-title'>🚀 Generate Optimized PDF</div>", unsafe_allow_html=True)

            opt_c1, opt_c2 = st.columns([2,2])
            with opt_c1:
                opt_sel = st.selectbox("Template",
                    ["Dark Header Classic","Two-Column Modern","Academic Minimal","Institute Format","Bold Professional"],
                    key="opt_tmpl")
                opt_tid = ["Dark Header Classic","Two-Column Modern","Academic Minimal","Institute Format","Bold Professional"].index(opt_sel)
            with opt_c2:
                st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
                ocol,_ = st.columns([1,1])
                with ocol:
                    st.markdown('<div class="btn-a">', unsafe_allow_html=True)
                    gen_opt = st.button("✨ Generate Optimized PDF", key="gen_opt", use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            if gen_opt:
                with st.spinner("Rewriting and generating…"):
                    try:
                        ujd2 = st.session_state.get("upload_jd","") or ""
                        opt_draft = call_llm(f"""Rewrite this resume as clean ATS-optimized Markdown.
Original:
{st.session_state.upload_text[:3500]}
Analysis:
{st.session_state.upload_analysis[:1200]}
{"Target: "+ujd2 if ujd2 else ""}
RULES: No skill levels. Keep real data. Action verbs. Quantify.
Sections: ## Summary → ## Experience → ## Education → ## Technical Skills → ## Projects → ## Certifications
Skip empty sections. LinkedIn → "LinkedIn". GitHub → "GitHub". Output Markdown only.
""", temperature=0.3)

                        from utils.pdf_generator import generate_resume_pdf

                        # Prefer the extracted profile from the uploaded PDF —
                        # this populates name, address, email, education, experience,
                        # skills, projects, and certifications for the template.
                        up_prof = st.session_state.get("upload_profile") or {}
                        if up_prof and up_prof.get("personal_info"):
                            opt_profile = {
                                "personal_info":  dict(up_prof.get("personal_info", {})),
                                "education":      list(up_prof.get("education", [])),
                                "experience":     list(up_prof.get("experience", [])),
                                "skills":         list(up_prof.get("skills", [])),
                                "projects":       list(up_prof.get("projects", [])),
                                "certifications": list(up_prof.get("certifications", [])),
                            }
                        else:
                            # Fallback to whatever's in the build-tab session state
                            opt_pi_fb = {k: pi.get(k, "") for k in
                                         ["first_name","last_name","email","mobile","location","linkedin","github"]}
                            opt_profile = {
                                "personal_info":  opt_pi_fb,
                                "education":      [], "experience": [], "skills": [],
                                "projects":       [], "certifications": [],
                            }

                        opt_pdf = generate_resume_pdf(
                            profile_data=opt_profile,
                            resume_draft=opt_draft,
                            template_id=opt_tid,
                        )

                        # namerole.pdf naming
                        opt_pi_now = opt_profile["personal_info"]
                        first = opt_pi_now.get("first_name", "") or ""
                        last  = opt_pi_now.get("last_name", "") or ""
                        role_for_fname = ""
                        if opt_profile.get("experience"):
                            role_for_fname = (opt_profile["experience"][0].get("role") or "")
                        if not role_for_fname:
                            role_for_fname = (ujd2.split("\n",1)[0][:30] if ujd2 else "Optimized")
                        fname = f"{first}{last}{re.sub(r'[^A-Za-z0-9]','', role_for_fname)}.pdf"
                        if fname in ("", ".pdf"):
                            fname = f"optimized_{opt_sel.replace(' ','')}.pdf"

                        st.session_state.opt_pdf   = opt_pdf
                        st.session_state.opt_draft = opt_draft
                        st.session_state.opt_fname = fname
                        st.rerun()
                    except Exception as e:
                        if is_quota_error(e):
                            mark_key_exhausted(get_next_key())
                            st.error("🔴 Key exhausted. Try again.")
                        else:
                            st.error(f"Error: {e}")

            if st.session_state.opt_pdf:
                st.markdown("<div class='box-ok'>✅ Optimized resume ready!</div>", unsafe_allow_html=True)
                dl_o1,dl_o2 = st.columns(2)
                with dl_o1:
                    st.download_button("⬇️ Download Optimized PDF",
                        st.session_state.opt_pdf, file_name=st.session_state.opt_fname,
                        mime="application/pdf", use_container_width=True, key="dl_opt")
                with dl_o2:
                    st.markdown('<div class="btn-b">', unsafe_allow_html=True)
                    if st.button("👁️ Toggle Preview", key="prev_opt", use_container_width=True):
                        st.session_state.show_opt_preview = not st.session_state.get("show_opt_preview", False)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                if st.session_state.get("show_opt_preview", False):
                    st.markdown("<div class='preview-box'>", unsafe_allow_html=True)
                    st.markdown(st.session_state.opt_draft)
                    st.markdown("</div>", unsafe_allow_html=True)

            # ── INTERVIEW QUESTIONS (from extracted resume) ────────────────────
            st.markdown('<hr class="div"/>', unsafe_allow_html=True)
            st.markdown("<div class='sec-title'>🎤 Interview Question Set</div>", unsafe_allow_html=True)
            st.markdown(
                "<p style='color:#6B7280;font-size:.85rem;margin-bottom:.6rem;'>"
                "Generate a tailored interview Q&A based on the skills + experience extracted from "
                "your uploaded resume. Download as a styled PDF for prep.</p>",
                unsafe_allow_html=True,
            )

            iqu_c1, iqu_c2 = st.columns([2, 2])
            with iqu_c1:
                st.markdown('<div class="btn-b">', unsafe_allow_html=True)
                gen_iqu = st.button(
                    "🎤 Generate Interview Questions PDF",
                    key="gen_iq_upload", use_container_width=True,
                )
                st.markdown("</div>", unsafe_allow_html=True)
            with iqu_c2:
                if st.session_state.get("iq_upload_pdf"):
                    st.download_button(
                        "⬇️ Download Interview PDF",
                        st.session_state["iq_upload_pdf"],
                        file_name=st.session_state.get("iq_upload_fname", "interview_questions.pdf"),
                        mime="application/pdf",
                        use_container_width=True, key="dl_iq_upload",
                    )
                else:
                    st.markdown(
                        "<div style='background:#F9FAFB;border:1.5px dashed #D1D5DB;border-radius:8px;"
                        "padding:.5rem .8rem;text-align:center;color:#9CA3AF;font-size:.8rem;'>"
                        "⬇️ Generate first</div>", unsafe_allow_html=True,
                    )

            if gen_iqu:
                # Use the extracted profile (so all skills + experience flow into the agent).
                ujd = (st.session_state.get("upload_jd") or "").strip()
                up_prof = st.session_state.get("upload_profile") or {}
                if up_prof and up_prof.get("personal_info"):
                    iq_profile = {
                        "personal_info":   dict(up_prof.get("personal_info", {})),
                        "education":       list(up_prof.get("education", [])),
                        "experience":      list(up_prof.get("experience", [])),
                        "skills":          list(up_prof.get("skills", [])),
                        "projects":        list(up_prof.get("projects", [])),
                        "certifications":  list(up_prof.get("certifications", [])),
                        "job_description": ujd,
                    }
                else:
                    iq_profile = {
                        "personal_info":   dict(pi),
                        "education":       [], "experience": [], "skills": [],
                        "projects":        [], "certifications": [],
                        "job_description": ujd,
                    }

                iqu_status   = st.empty()
                iqu_progress = st.progress(0)

                def _iqu_cb(stage, done, total):
                    iqu_status.markdown(
                        f"<div class='box-info'>{esc(stage)} — step {done}/{total}</div>",
                        unsafe_allow_html=True,
                    )
                    iqu_progress.progress(min(1.0, done / max(total, 1)))

                try:
                    from agents.llm import LLMClient
                    from agents.interview_agent import generate_interview_questions
                    from utils.interview_pdf import generate_interview_pdf

                    all_keys = (st.session_state.get("ui_extra_keys", [])
                                + st.session_state.get("env_keys", []))
                    client = LLMClient(all_keys)
                    client.exhausted = set(st.session_state.get("exhausted_keys", set()))

                    qset = generate_interview_questions(
                        iq_profile,
                        resume_draft=st.session_state.upload_text,
                        llm_client=client,
                        progress_cb=_iqu_cb,
                    )

                    # Candidate name + target role for filename
                    cand_pi    = iq_profile.get("personal_info", {})
                    first      = (cand_pi.get("first_name") or "").strip()
                    last       = (cand_pi.get("last_name") or "").strip()
                    cand_name  = f"{first} {last}".strip()
                    if not cand_name:
                        first_line = (st.session_state.upload_text or "").strip().split("\n",1)[0][:60]
                        cand_name  = first_line or "Candidate"

                    role_part = qset.target_role or (
                        iq_profile["experience"][0].get("role") if iq_profile.get("experience") else "Interview"
                    )
                    fname = f"{first}{last}{re.sub(r'[^A-Za-z0-9]','', role_part or 'Interview')}_questions.pdf"

                    pdf_bytes = generate_interview_pdf(qset, candidate_name=cand_name)

                    st.session_state["iq_upload_set"]   = qset
                    st.session_state["iq_upload_pdf"]   = pdf_bytes
                    st.session_state["iq_upload_fname"] = fname
                    st.session_state.exhausted_keys = set(client.exhausted)
                    iqu_progress.empty(); iqu_status.empty()
                    st.rerun()
                except Exception as e:
                    iqu_progress.empty(); iqu_status.empty()
                    if is_quota_error(e):
                        mark_key_exhausted(get_next_key())
                        st.error("🔴 Key exhausted. Try again.")
                    else:
                        st.error(f"❌ {e}")

            if st.session_state.get("iq_upload_set"):
                qset = st.session_state["iq_upload_set"]
                total_q = qset.total_questions()
                with st.expander(
                    f"👁️ Preview — {total_q} questions across {len(qset.skill_questions)} skills + 4 common categories"
                ):
                    if qset.candidate_summary:
                        st.markdown(f"**Candidate brief:** {qset.candidate_summary}")
                    for sq in qset.skill_questions:
                        st.markdown(f"#### 🧠 {sq.skill_name}  _({sq.total()} questions)_")
                        for tier_name, qs in [("Basic", sq.basic), ("Intermediate", sq.intermediate), ("Expert", sq.expert)]:
                            if not qs: continue
                            st.markdown(f"**{tier_name}**")
                            for i, q in enumerate(qs, 1):
                                st.markdown(f"- **Q{i}.** {q.question}")
                                if q.answer:
                                    st.caption(f"Answer: {q.answer}")
                    for title, qs in [
                        ("Behavioral / Situational", qset.behavioral),
                        ("Project Deep-Dive",         qset.project_deep_dive),
                        ("System Design",             qset.system_design),
                        ("Role-Specific",             qset.role_specific),
                    ]:
                        if not qs: continue
                        st.markdown(f"#### {title}")
                        for i, q in enumerate(qs, 1):
                            st.markdown(f"- **Q{i}** _({q.difficulty})_ — {q.question}")
                            if q.answer:
                                st.caption(f"Answer: {q.answer}")

            # Note: the RAG chatbot lives at the top of this tab (always visible).
            # After analysis runs, it now has full resume + ATS context to draw on.


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<hr class="div"/>', unsafe_allow_html=True)
st.markdown(
    "<div style='background:#F9FAFB;border:1px solid #E5E7EB;border-radius:10px;"
    "padding:1rem 1.4rem;margin-bottom:1.5rem;'>"
    "<div style='font-family:Syne,sans-serif;font-size:.88rem;font-weight:700;color:#111827;margin-bottom:.5rem;'>"
    "🤖 AI Guidance — Note</div>"
    "<div style='font-size:.8rem;color:#374151;line-height:1.75;'>"
    "All analysis, resume writing, ATS scoring (via <b>Gemini Flash Lite</b>), roadmaps and posts "
    "are generated by <b>Google Gemini via a 6-agent LangGraph pipeline</b> — nothing hardcoded.<br/>"
    "✅ Review every section before sending to employers.<br/>"
    "⚠️ AI guides — human recruiters make final decisions.<br/>"
    "💡 Paste a job description for maximum ATS optimization.<br/>"
    "🔑 Add 2–4 API keys in the sidebar — keys rotate automatically on exhaustion."
    "</div></div>"
    "<div style='text-align:center;color:#9CA3AF;font-size:.74rem;padding-bottom:1rem;'>"
    "AI Resume Builder · LangGraph · Streamlit · Gemini · "
    "<a href='https://aistudio.google.com/app/apikey' target='_blank' style='color:#6B7280;'>Get Free API Keys</a>"
    "</div>",
    unsafe_allow_html=True,
)
