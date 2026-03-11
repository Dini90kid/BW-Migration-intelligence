"""
BW Migration Intelligence Platform — Streamlit Host
Handles login, shared server-side storage, and role enforcement.
"""
import streamlit as st
import json, hashlib, os
from pathlib import Path
from datetime import datetime

# ── PATHS ────────────────────────────────────────────────────────────────────
DATA_DIR   = Path("data")
STATE_FILE = DATA_DIR / "bw_state.json"
USERS_FILE = DATA_DIR / "users.json"
HTML_FILE  = Path("bw_platform.html")
DATA_DIR.mkdir(exist_ok=True)

def _hash(pw): return hashlib.sha256(pw.encode()).hexdigest()

DEFAULT_USERS = {
    "admin":   {"password_hash": _hash("admin123"), "role":"Admin",   "access":"admin"},
    "analyst": {"password_hash": _hash("bw2024"),   "role":"Analyst", "access":"analyst"},
    "guest":   {"password_hash": _hash("guest123"), "role":"Guest",   "access":"guest"},
}

def load_users():
    if USERS_FILE.exists():
        try: return json.loads(USERS_FILE.read_text())
        except: pass
    return json.loads(json.dumps(DEFAULT_USERS))

def save_users(u): USERS_FILE.write_text(json.dumps(u, indent=2))

def load_bw_state():
    if STATE_FILE.exists():
        try: return json.loads(STATE_FILE.read_text())
        except: pass
    return None

def save_bw_state(s): STATE_FILE.write_text(json.dumps(s))

def load_html():
    if HTML_FILE.exists(): return HTML_FILE.read_text(encoding="utf-8")
    return "<h2 style='color:red;font-family:monospace'>bw_platform.html not found.</h2>"

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="BW Migration Intelligence", page_icon="⬡", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>
  #MainMenu,header,footer,[data-testid="stToolbar"],[data-testid="stDecoration"],
  [data-testid="stStatusWidget"]{visibility:hidden;height:0;display:none!important}
  .block-container{padding:0!important;max-width:100%!important;margin:0!important}
  [data-testid="stAppViewContainer"]{background:#080c12!important;padding:0!important}
  [data-testid="stVerticalBlock"]{gap:0!important;padding:0!important}
  iframe{display:block;border:none;}
</style>""", unsafe_allow_html=True)

# ── SESSION ───────────────────────────────────────────────────────────────────
for k,v in [("logged_in",False),("username",""),("role",""),("access",""),("show_user_mgr",False)]:
    if k not in st.session_state: st.session_state[k] = v

# ════════════════════════════════════════════════════════════════════════════
# LOGIN SCREEN
# ════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    users = load_users()
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    body,[data-testid="stAppViewContainer"]{background:#080c12!important}
    .stForm{background:#0d1420;border:1px solid #253650;border-radius:8px;padding:32px 28px 24px;
            box-shadow:0 8px 40px rgba(0,0,0,.6);max-width:420px;margin:0 auto;}
    .stTextInput input{background:#121b2e!important;border:1px solid #253650!important;
                       color:#e8f0fe!important;font-family:'JetBrains Mono',monospace!important;border-radius:4px!important;}
    .stTextInput input:focus{border-color:#00d4ff!important;box-shadow:0 0 0 3px rgba(0,212,255,.08)!important;}
    .stFormSubmitButton button{width:100%!important;background:rgba(0,212,255,.12)!important;
                               border:1px solid #00d4ff!important;color:#00d4ff!important;
                               font-family:'JetBrains Mono',monospace!important;font-weight:600!important;
                               letter-spacing:.1em!important;text-transform:uppercase!important;border-radius:4px!important;}
    .stFormSubmitButton button:hover{background:#00d4ff!important;color:#080c12!important;}
    label{color:#4a5a7a!important;font-family:'JetBrains Mono',monospace!important;font-size:10px!important;
          text-transform:uppercase!important;letter-spacing:.1em!important;}
    </style>""", unsafe_allow_html=True)

    # Centre the login card
    _, mid, _ = st.columns([1,2,1])
    with mid:
        st.markdown("""
        <div style='text-align:center;padding:40px 0 8px;'>
          <div style='font-family:Syne,sans-serif;font-weight:800;font-size:28px;color:#00d4ff;
                      letter-spacing:.1em;text-shadow:0 0 30px rgba(0,212,255,.4);'>
            BW<span style='color:#8899bb;font-weight:400'> Migration</span> Intelligence</div>
          <div style='width:60px;height:2px;background:linear-gradient(90deg,transparent,#00d4ff,transparent);margin:12px auto;'></div>
          <div style='font-size:10px;color:#4a5a7a;letter-spacing:.12em;text-transform:uppercase;margin-bottom:28px;'>
            Enterprise Analytics Platform · Secure Access</div>
        </div>""", unsafe_allow_html=True)

        with st.form("login"):
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="••••••••••")
            submitted = st.form_submit_button("→  Sign In", use_container_width=True)
            if submitted:
                u = username.strip().lower()
                if u in users and users[u]["password_hash"] == _hash(password):
                    st.session_state.logged_in = True
                    st.session_state.username  = u
                    st.session_state.role      = users[u]["role"]
                    st.session_state.access    = users[u]["access"]
                    st.rerun()
                else:
                    st.error("⚠ Invalid credentials.")

        # Role hints
        roles = {}
        for u,d in users.items(): roles.setdefault(d["access"],[]).append(u)
        icons = {"admin":"🔑","analyst":"📊","guest":"👁"}
        hints = [f"{icons.get(a,'·')} **{a.title()}**: {', '.join(names)}" for a,names in roles.items()]
        st.markdown(
            "<div style='margin-top:16px;padding:10px 14px;background:rgba(255,255,255,.03);"
            "border-radius:4px;font-family:monospace;font-size:10px;color:#4a5a7a;line-height:2.2;'>"
            + "<br>".join(hints)+"</div>", unsafe_allow_html=True)
    st.stop()

# ════════════════════════════════════════════════════════════════════════════
# LOGGED IN
# ════════════════════════════════════════════════════════════════════════════
access   = st.session_state.access
username = st.session_state.username
role     = st.session_state.role
role_colors = {"admin":"#00d4ff","analyst":"#00ff88","guest":"#ffaa00"}
role_color  = role_colors.get(access,"#8899bb")

# ── NO STREAMLIT TOP BAR — all controls are inside the HTML platform header ──

# Handle logout triggered from HTML (via query param)
if st.query_params.get("action") == "logout":
    for k in ["logged_in","username","role","access","show_user_mgr","trigger_save"]:
        st.session_state.pop(k, None)
    st.query_params.clear()
    st.rerun()

# ── BUILD HTML WITH INJECTED AUTH + PRELOAD ───────────────────────────────────
stored_state = load_bw_state() if access in ("admin","analyst") else None
preload_json = json.dumps(stored_state) if stored_state else "null"

inject = f"""
<script>
window.__BW_SERVER_AUTH__ = {{
  username: "{username}",
  role:     "{role}",
  access:   "{access}",
  color:    "{role_color}"
}};
window.__BW_PRELOAD__ = {preload_json};
window.__BW_TRIGGER_SAVE__ = {'true' if st.session_state.get('trigger_save') else 'false'};
</script>
"""
if st.session_state.get("trigger_save"):
    st.session_state.pop("trigger_save", None)

auto_script = """
<script>
(function(){
  function init(){
    var auth = window.__BW_SERVER_AUTH__;
    if (!auth) return;

    // Bypass HTML login system — set SESSION_USER
    window.SESSION_USER = {
      username: auth.username, role: auth.role,
      color: auth.color,       access: auth.access
    };

    // Hide login screen immediately
    var ls = document.getElementById('login-screen');
    if (ls) { ls.style.opacity='0'; ls.style.pointerEvents='none'; setTimeout(function(){ ls.style.display='none'; },100); }

    // Show inline header session badge + controls
    if (typeof showSessionBadge==='function') {
      try { showSessionBadge(); } catch(e){}
    }

    // Show ⚙ Users button for admin (opens in-HTML modal)
    var gear = document.getElementById('admin-settings-btn');
    if (gear && auth.access==='admin') gear.style.display='inline-block';

    // Wire ⏻ logout button → Streamlit session kill via query param
    var lo = document.getElementById('header-logout-btn');
    if (lo) {
      lo.onclick = function(){
        window.parent.location.href = window.parent.location.pathname + '?action=logout';
      };
    }
    // Also hide old floating logout if it exists
    var oldLo = document.querySelector('.logout-btn');
    if (oldLo) oldLo.style.display='none';

    // ── STEP 1: Load server preloaded data FIRST (before applyAccessLevel) ──
    if (window.__BW_PRELOAD__ && typeof STATE!=='undefined' && typeof renderAll==='function'){
      try {
        STATE.useCases  = window.__BW_PRELOAD__.useCases  || [];
        STATE.fmLibrary = window.__BW_PRELOAD__.fmLibrary || {};
        // Also mirror into localStorage so applyAccessLevel's loadStoredState() finds it
        try { localStorage.setItem('bw_platform_saved_state', JSON.stringify(window.__BW_PRELOAD__)); } catch(e){}
        renderAll();
        var ind = document.getElementById('saved-indicator');
        var lbl = document.getElementById('saved-label');
        if (ind) ind.style.display = 'flex';
        if (lbl) lbl.textContent = (window.__BW_PRELOAD__.meta || 'data loaded') +
          (window.__BW_PRELOAD__.savedAt ? ' · ' + window.__BW_PRELOAD__.savedAt : '');
      } catch(e){ console.warn('Preload error:', e); }
    }

    // ── STEP 2: Apply access restrictions (auto-loads localStorage which now has server data) ──
    if (typeof applyAccessLevel==='function') {
      try { applyAccessLevel(auth.access); } catch(e){}
    }

    // ── STEP 3: Wire 💾 Save → POST back to Streamlit server ──
    var saveBtn = document.getElementById('save-data-btn');
    if (saveBtn && auth.access !== 'guest') {
      saveBtn.onclick = function() {
        if (!STATE || !STATE.useCases || !STATE.useCases.length) {
          if (typeof showToast==='function') showToast('No data to save.', 'amber'); return;
        }
        var provCount = STATE.useCases.reduce(function(s,uc){ return s+(uc.providers||[]).length; }, 0);
        var payload = {
          meta:      STATE.useCases.length + ' UCs · ' + provCount + ' Providers',
          savedAt:   new Date().toLocaleString(),
          savedBy:   auth.username,
          useCases:  STATE.useCases,
          fmLibrary: STATE.fmLibrary || {}
        };
        try {
          var url = new URL(window.parent.location.href);
          url.searchParams.set('save_data', JSON.stringify(payload));
          window.parent.location.href = url.toString();
        } catch(e) {
          if (typeof showToast==='function') showToast('Save error: ' + e.message, 'red');
        }
      };
      // Show save button immediately if data already loaded
      if (STATE && STATE.useCases && STATE.useCases.length) {
        saveBtn.style.display = 'inline-block';
      }
    }

    // ── STEP 4: If Load Data button used — auto-save to server after upload ──
    // Hook into the existing upload completion so new data replaces server state automatically
    var origRenderAll = typeof renderAll === 'function' ? renderAll : null;
    if (origRenderAll && auth.access !== 'guest') {
      var _hooked = false;
      var hookSave = function() {
        if (!_hooked) {
          _hooked = true;
          var _orig = renderAll;
          renderAll = function() {
            _orig();
            // Show save button after any renderAll
            var sb = document.getElementById('save-data-btn');
            if (sb && STATE && STATE.useCases && STATE.useCases.length) sb.style.display='inline-block';
          };
        }
      };
      setTimeout(hookSave, 200);
    }
  }

  if(document.readyState==='loading'){ document.addEventListener('DOMContentLoaded',init); }
  else { setTimeout(init,50); }
})();
</script>
"""

html_content = load_html()
html_content = html_content.replace("</head>", inject + "</head>", 1)
html_content = html_content.replace("</body>", auto_script + "</body>", 1)

# Handle save via query param
if "save_data" in st.query_params:
    try:
        payload = json.loads(st.query_params["save_data"])
        save_bw_state(payload)
        st.success(f"✓ Data saved by **{payload.get('savedBy','?')}** — {payload.get('meta','')} at {payload.get('savedAt','')}")
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Save failed: {e}")

# ── RENDER ────────────────────────────────────────────────────────────────────
from streamlit.components.v1 import html as st_html
st_html(html_content, height=920, scrolling=True)
