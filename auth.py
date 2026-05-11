"""Custom login / signup gate.

Why custom (not streamlit-authenticator)?
- We need a "🎯 Use demo credentials" button that auto-fills the form
- We need full control over the signup flow + validation messages
- We avoid the streamlit-authenticator version-API churn

Storage:
- Users live in `auth_users.json` (local file, gitignored)
- Passwords are bcrypt-hashed
- Demo credentials come from `.env` (DEMO_USERNAME / DEMO_PASSWORD) — never hardcoded
- Streamlit Cloud: paste a `auth_users_json` blob into secrets to seed users

Session:
- Logged-in state lives in `st.session_state["auth_session"]` with an expiry
- Logout button rendered in the sidebar
- Browser refresh logs the user out (no cookie persistence — keep it simple)
"""
from __future__ import annotations
import json, os, time, secrets as _secrets
from pathlib import Path
from typing import Optional
import streamlit as st


USERS_PATH = Path(__file__).resolve().parent / "auth_users.json"
SESSION_KEY = "auth_session"
SESSION_TTL_SECONDS = 7 * 24 * 3600   # 7 days


# ─────────────────────────────────────────────────────────────────────────────
# Password hashing (bcrypt with passlib-style fallback)
# ─────────────────────────────────────────────────────────────────────────────
def _hash_pw(pw: str) -> str:
    import bcrypt
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _check_pw(pw: str, hashed: str) -> bool:
    import bcrypt
    try:
        return bcrypt.checkpw(pw.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Config — demo credentials read from .env or st.secrets (no hardcoding)
# ─────────────────────────────────────────────────────────────────────────────
def _demo_creds() -> Optional[tuple[str, str]]:
    """Return (username, password) if demo creds are configured, else None."""
    def _get(name: str) -> str:
        v = os.getenv(name, "").strip()
        if v:
            return v
        try:
            return (st.secrets.get(name, "") or "").strip()
        except Exception:
            return ""

    u = _get("DEMO_USERNAME")
    p = _get("DEMO_PASSWORD")
    return (u, p) if (u and p) else None


# ─────────────────────────────────────────────────────────────────────────────
# User database
# ─────────────────────────────────────────────────────────────────────────────
def _load_users() -> dict:
    """Load users from disk OR Streamlit secrets, seeding demo user on first run."""
    # 1. Streamlit secrets blob (deploy scenario — persistent)
    try:
        blob = st.secrets.get("auth_users_json", None)
        if blob:
            return json.loads(blob)
    except Exception:
        pass

    # 2. Local JSON file
    if USERS_PATH.exists():
        try:
            return json.loads(USERS_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass

    # 3. First run — seed with demo user if demo creds are set
    users: dict = {}
    demo = _demo_creds()
    if demo:
        u, p = demo
        users[u] = {
            "name":     "Demo User",
            "email":    "demo@example.com",
            "password": _hash_pw(p),
        }
        _save_users(users)
    return users


def _save_users(users: dict) -> None:
    try:
        USERS_PATH.write_text(json.dumps(users, indent=2), encoding="utf-8")
    except Exception as e:
        st.warning(f"⚠️ Could not persist user database: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Session helpers
# ─────────────────────────────────────────────────────────────────────────────
def _is_logged_in() -> bool:
    sess = st.session_state.get(SESSION_KEY)
    if not sess:
        return False
    if time.time() > sess.get("expires_at", 0):
        del st.session_state[SESSION_KEY]
        return False
    return True


def _establish_session(username: str, name: str) -> None:
    st.session_state[SESSION_KEY] = {
        "username":   username,
        "name":       name,
        "expires_at": time.time() + SESSION_TTL_SECONDS,
    }


def logout() -> None:
    """Clear the session — exposed for the sidebar logout button."""
    if SESSION_KEY in st.session_state:
        del st.session_state[SESSION_KEY]


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────
def require_login() -> tuple[str, str]:
    """Block the app until logged in. Returns (display_name, username)."""
    if _is_logged_in():
        sess = st.session_state[SESSION_KEY]
        return sess["name"], sess["username"]

    users = _load_users()
    demo  = _demo_creds()

    # ── Pre-render hook: copy any pending demo-fill values into the actual
    # widget session-state keys BEFORE the widgets are instantiated. Streamlit
    # ignores `value=` after a widget's first render, so we must seed via
    # session_state under the widget's `key`.
    if "_pending_login_user" in st.session_state:
        st.session_state["login_uname_input"] = st.session_state.pop("_pending_login_user")
    if "_pending_login_pw" in st.session_state:
        st.session_state["login_pw_input"] = st.session_state.pop("_pending_login_pw")
    if st.session_state.pop("_clear_login_form", False):
        st.session_state["login_uname_input"] = ""
        st.session_state["login_pw_input"]    = ""

    # ── Centered card layout ──────────────────────────────────────────────────
    pad_l, main, pad_r = st.columns([1, 2, 1])
    with main:
        st.markdown(
            "<div style='padding:1.4rem 1.6rem 1rem;background:#fff;"
            "border:1px solid #E5E7EB;border-radius:14px;"
            "box-shadow:0 8px 24px rgba(0,0,0,.06);margin-top:2rem;'>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<h2 style='margin:0 0 .3rem;font-family:Syne,sans-serif;'>🚀 AI Resume Builder</h2>"
            "<p style='color:#6B7280;margin:0 0 1rem;font-size:.92rem;'>"
            "Sign in to generate ATS-optimized resumes, interview questions, and chat with the RAG coach.</p>",
            unsafe_allow_html=True,
        )

        tab_login, tab_signup = st.tabs(["🔑 Log in", "📝 Create account"])

        # ── Login tab ─────────────────────────────────────────────────────────
        with tab_login:
            if demo:
                d_user, d_pass = demo
                st.markdown(
                    f"<div style='background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;"
                    f"padding:.55rem .9rem;font-size:.82rem;margin-bottom:.6rem;color:#1E40AF;'>"
                    f"💡 <b>Demo account ready:</b> <code>{d_user}</code> / <code>{d_pass}</code><br/>"
                    f"<span style='color:#1E3A8A;font-size:.76rem;'>Click below to auto-fill the form.</span></div>",
                    unsafe_allow_html=True,
                )
                # NOTE: this button must live OUTSIDE the form (forms can only
                # contain one submit button) and set a pending key that the
                # pre-render hook above copies into the widget state on rerun.
                if st.button("🎯 Use demo credentials", key="demo_fill_btn", use_container_width=True):
                    st.session_state["_pending_login_user"] = d_user
                    st.session_state["_pending_login_pw"]   = d_pass
                    st.rerun()
            else:
                st.markdown(
                    "<div style='background:#FFFBEB;border:1px solid #FCD34D;border-radius:8px;"
                    "padding:.55rem .9rem;font-size:.78rem;color:#92400E;margin-bottom:.6rem;'>"
                    "ℹ️ No demo account configured. Set <code>DEMO_USERNAME</code> and "
                    "<code>DEMO_PASSWORD</code> in <code>.env</code> to enable the demo button, "
                    "or create an account below.</div>",
                    unsafe_allow_html=True,
                )

            # Clear button also lives OUTSIDE the form so it can mutate widget
            # state cleanly via the pre-render hook on the next run.
            if st.button("↻ Clear form", key="clear_login_form_btn", use_container_width=True):
                st.session_state["_clear_login_form"] = True
                st.rerun()

            with st.form("login_form", clear_on_submit=False):
                uname = st.text_input(
                    "Username",
                    key="login_uname_input",
                    placeholder="your_username",
                )
                pw = st.text_input(
                    "Password",
                    key="login_pw_input",
                    type="password",
                    placeholder="••••••••",
                )
                submitted = st.form_submit_button("🔓 Log in", use_container_width=True)

                if submitted:
                    u = (uname or "").strip()
                    if not u or not pw:
                        st.error("Please enter both username and password.")
                    elif u not in users:
                        st.error("❌ User not found. Sign up first.")
                    elif not _check_pw(pw, users[u]["password"]):
                        st.error("❌ Incorrect password.")
                    else:
                        _establish_session(u, users[u].get("name", u))
                        st.success(f"✅ Welcome back, {users[u].get('name', u)}!")
                        st.rerun()

        # ── Signup tab ────────────────────────────────────────────────────────
        with tab_signup:
            st.markdown(
                "<p style='color:#6B7280;font-size:.85rem;margin-bottom:.4rem;'>"
                "Create a free account. Username and password are required; "
                "name + email are optional.</p>",
                unsafe_allow_html=True,
            )
            with st.form("signup_form", clear_on_submit=False):
                s_user    = st.text_input("Username *",        placeholder="3+ chars, letters/numbers/underscore")
                s_name    = st.text_input("Display name",      placeholder="(optional)")
                s_email   = st.text_input("Email",             placeholder="(optional)")
                s_pw      = st.text_input("Password *",        type="password", placeholder="≥ 6 characters")
                s_confirm = st.text_input("Confirm password *", type="password")
                s_submit  = st.form_submit_button("🆕 Create account", use_container_width=True)

                if s_submit:
                    user = (s_user or "").strip()
                    errors: list[str] = []
                    if len(user) < 3:
                        errors.append("Username must be at least 3 characters.")
                    if not user.replace("_", "").isalnum():
                        errors.append("Username can only contain letters, numbers, and underscore.")
                    if len(s_pw) < 6:
                        errors.append("Password must be at least 6 characters.")
                    if s_pw != s_confirm:
                        errors.append("Passwords do not match.")
                    if user in users:
                        errors.append(f"Username '{user}' is already taken.")

                    if errors:
                        for e in errors:
                            st.error("❌ " + e)
                    else:
                        users[user] = {
                            "name":     (s_name or user).strip(),
                            "email":    (s_email or "").strip(),
                            "password": _hash_pw(s_pw),
                        }
                        _save_users(users)
                        st.success(
                            f"✅ Account `{user}` created! "
                            f"Switch to the **Log in** tab to sign in."
                        )

        # ── Footer ────────────────────────────────────────────────────────────
        st.markdown(
            "<p style='text-align:center;color:#9CA3AF;font-size:.72rem;margin:.8rem 0 0;'>"
            "Local accounts only · bcrypt-hashed · no third-party SSO</p>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


def render_logout_chip() -> None:
    """Sidebar chip + logout button. Call once from the main app after require_login()."""
    if not _is_logged_in():
        return
    sess = st.session_state[SESSION_KEY]
    with st.sidebar:
        st.markdown(
            f"<div style='background:#052E16;border:1px solid #166534;color:#86EFAC;"
            f"border-radius:8px;padding:.45rem .8rem;font-size:.78rem;margin-bottom:.4rem;'>"
            f"👤 <b>{sess.get('name','User')}</b><br/>"
            f"<span style='color:#6EE7B7;font-size:.7rem;'>@{sess.get('username','')}</span></div>",
            unsafe_allow_html=True,
        )
        if st.button("🚪 Log out", key="_logout_btn", use_container_width=True):
            logout()
            st.rerun()
