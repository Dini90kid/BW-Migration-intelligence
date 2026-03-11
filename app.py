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
st.markdown("<style>#MainMenu,header,footer{visibility:hidden}.block-container{padding:0!important;max-width:100%!important}</style>", unsafe_allow_html=True)

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

# ── TOP BAR ───────────────────────────────────────────────────────────────────
bar = st.container()
with bar:
    c1,c2,c3,c4,c5 = st.columns([4,2,1,1,1])
    with c1:
        st.markdown(f"<div style='font-family:Syne,sans-serif;font-weight:800;font-size:17px;color:#00d4ff;"
                    f"letter-spacing:.08em;padding:8px 0 0 4px;'>BW <span style='color:#8899bb;font-weight:400'>"
                    f"Migration Intelligence</span></div>", unsafe_allow_html=True)
    with c2:
        stored = load_bw_state()
        meta_txt = f" · {stored['meta']}" if stored and 'meta' in stored else ""
        st.markdown(f"<div style='padding:10px 0 0;font-family:monospace;font-size:11px;color:#8899bb;'>"
                    f"<span style='color:{role_color};font-weight:600;'>{role}</span> · {username}{meta_txt}</div>",
                    unsafe_allow_html=True)
    with c3:
        if access in ("admin","analyst") and st.button("💾 Save", help="Save to server", use_container_width=True):
            st.session_state["trigger_save"] = True
    with c4:
        if access == "admin" and st.button("⚙ Users", use_container_width=True):
            st.session_state.show_user_mgr = not st.session_state.show_user_mgr
    with c5:
        if st.button("⏻ Out", help="Logout", use_container_width=True):
            for k in ["logged_in","username","role","access","show_user_mgr","trigger_save"]:
                st.session_state.pop(k,None)
            st.rerun()

# ── USER MANAGER (Admin only) ─────────────────────────────────────────────────
if st.session_state.show_user_mgr and access == "admin":
    users = load_users()
    with st.expander("⚙ Manage Users", expanded=True):
        st.markdown("**Admin** — username `admin` is permanent")
        new_admin_pass = st.text_input("New Admin Password (blank = keep)", type="password", key="adm_pw")
        st.divider()

        # Existing non-admin users
        non_admin = {u:d for u,d in users.items() if d["access"]!="admin"}
        updated = {}
        if non_admin:
            st.markdown("**Existing users** — tick 🗑 to delete")
            for uname, udata in non_admin.items():
                c1,c2,c3,c4 = st.columns([2,2,2,1])
                with c1: st.text_input("User", value=uname, key=f"u_{uname}", disabled=True)
                with c2: sel = st.selectbox("Role",["Analyst","Guest"],index=0 if udata["access"]=="analyst" else 1, key=f"r_{uname}")
                with c3: npw = st.text_input("New Password",type="password",placeholder="(unchanged)",key=f"p_{uname}")
                with c4:
                    st.write("")
                    st.write("")
                    delete = st.checkbox("🗑", key=f"d_{uname}")
                if not delete:
                    updated[uname] = {
                        "password_hash": _hash(npw) if npw else udata["password_hash"],
                        "role": sel, "access": sel.lower()
                    }
        st.divider()
        st.markdown("**Add new user**")
        c1,c2,c3 = st.columns(3)
        with c1: new_u = st.text_input("Username", placeholder="e.g. john", key="nu")
        with c2: new_r = st.selectbox("Role", ["Analyst","Guest"], key="nr")
        with c3: new_p = st.text_input("Password", type="password", placeholder="Set password", key="np")

        if st.button("✓ Save All Users", type="primary"):
            admin_data = users.get("admin", {"password_hash":_hash("admin123"),"role":"Admin","access":"admin"})
            final = {"admin": {"password_hash": _hash(new_admin_pass) if new_admin_pass else admin_data["password_hash"],
                               "role":"Admin","access":"admin"}}
            final.update(updated)
            if new_u.strip():
                if not new_p.strip(): st.error("New user needs a password.")
                elif new_u.strip().lower() in final: st.error(f"'{new_u}' already exists.")
                else:
                    final[new_u.strip().lower()] = {"password_hash":_hash(new_p),"role":new_r,"access":new_r.lower()}
            if "error" not in str(final):
                save_users(final)
                a = sum(1 for d in final.values() if d["access"]=="analyst")
                g = sum(1 for d in final.values() if d["access"]=="guest")
                st.success(f"✓ Saved — 1 Admin · {a} Analyst{'s' if a!=1 else ''} · {g} Guest{'s' if g!=1 else ''}")
                st.session_state.show_user_mgr = False
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

    // Bypass HTML login system
    window.SESSION_USER = {
      username: auth.username, role: auth.role,
      color: auth.color,       access: auth.access
    };
    // Also set it for the login system if it uses LOGIN_USERS scope
    if (typeof SESSION_USER === 'undefined') window.SESSION_USER = window.SESSION_USER;

    // Hide login screen immediately
    var ls = document.getElementById('login-screen');
    if (ls) { ls.style.opacity='0'; ls.style.pointerEvents='none'; setTimeout(function(){ ls.style.display='none'; },100); }

    // Show session badge
    if (typeof showSessionBadge==='function') {
      try { showSessionBadge(); } catch(e){}
    } else {
      var badge = document.getElementById('session-badge');
      var dot   = document.getElementById('badge-dot');
      var lbl   = document.getElementById('badge-label');
      if (badge){ badge.classList.add('show'); }
      if (dot)  { dot.style.background=auth.color; dot.style.boxShadow='0 0 6px '+auth.color; }
      if (lbl)  { lbl.innerHTML='<span style="color:'+auth.color+';font-weight:600">'+auth.role+'</span>&nbsp;·&nbsp;'+auth.username; }
    }

    // Hide gear button (Streamlit top bar handles user mgmt)
    var gear = document.getElementById('admin-settings-btn');
    if (gear) gear.style.display='none';

    // Hide logout button (Streamlit handles it)
    var lo = document.querySelector('.logout-btn');
    if (lo) lo.style.display='none';

    // Apply access restrictions
    if (typeof applyAccessLevel==='function') {
      try { applyAccessLevel(auth.access); } catch(e){}
    } else {
      // Manual fallback
      var uploadBtn = document.getElementById('upload-trigger');
      var saveBtn   = document.getElementById('save-data-btn');
      var aiSend    = document.getElementById('ai-send');
      if (auth.access==='analyst'){
        if (uploadBtn){ uploadBtn.style.opacity='0.35'; uploadBtn.style.pointerEvents='none'; }
      }
      if (auth.access==='guest'){
        if (saveBtn)  saveBtn.style.display='none';
        if (aiSend)   { aiSend.style.opacity='0.35'; aiSend.style.pointerEvents='none'; }
      }
    }

    // Load preloaded server state
    if (window.__BW_PRELOAD__ && typeof STATE!=='undefined' && typeof renderAll==='function'){
      try{
        STATE.useCases  = window.__BW_PRELOAD__.useCases  || [];
        STATE.fmLibrary = window.__BW_PRELOAD__.fmLibrary || {};
        renderAll();
        var ind = document.getElementById('saved-indicator');
        var lbl = document.getElementById('saved-label');
        if(ind) ind.style.display='flex';
        if(lbl) lbl.textContent='Server: '+(window.__BW_PRELOAD__.meta||'data loaded');
      } catch(e){ console.warn('Preload error:',e); }
    }

    // Wire save button → POST to Streamlit via query param
    var saveBtn = document.getElementById('save-data-btn');
    if (saveBtn && auth.access!=='guest'){
      saveBtn.onclick = function(){
        if(!STATE||!STATE.useCases||!STATE.useCases.length){
          if(typeof showToast==='function') showToast('No data to save.','amber'); return;
        }
        var provCount = STATE.useCases.reduce(function(s,uc){return s+(uc.providers||[]).length;},0);
        var payload = {
          meta: STATE.useCases.length+' UCs · '+provCount+' Providers',
          savedAt: new Date().toLocaleString(),
          savedBy: auth.username,
          useCases: STATE.useCases,
          fmLibrary: STATE.fmLibrary||{}
        };
        // Send to parent Streamlit window
        try{
          var url = new URL(window.location.href);
          url.searchParams.set('save_data', JSON.stringify(payload));
          window.location.href = url.toString();
        } catch(e){
          if(typeof showToast==='function') showToast('Save error: '+e.message,'red');
        }
      };
    }

    // Trigger save from Streamlit top bar
    if (window.__BW_TRIGGER_SAVE__ && saveBtn){ setTimeout(function(){ saveBtn.click(); },1000); }
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
