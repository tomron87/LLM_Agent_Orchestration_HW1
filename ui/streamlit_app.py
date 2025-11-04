import os
import time
import html
import requests
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
from streamlit.components.v1 import html as st_html
from math import ceil

# ====== ENV ======
load_dotenv(find_dotenv())
API_URL = os.getenv("API_URL")
APP_API_KEY = os.getenv("APP_API_KEY")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "")
DEBUG = False  # שנה ל-True אם תרצה לראות raw מה-API

# ====== PAGE ======
st.set_page_config(page_title="Local Ollama Chat", page_icon="💬", layout="wide")

# ====== GLOBAL CSS (Dark + Modern + RTL) ======
st.markdown("""
<style>
:root {
  color-scheme: dark;
  --bubble-w: 86%;                 /* שליטה נוחה ברוחב הבועות */
}

/* רקע ומצב RTL */
html, body, .stApp {
  background: radial-gradient(1200px 600px at 50% -10%, #222b3a 0%, #0e1117 40%, #0b0d12 100%) !important;
}
html, body, [class*="css"] { direction: rtl; }
h1, h2, h3, h4, label, .stAlert, .stCaption { text-align: center; }

/* מעטפת חלון ההודעות (נקודת ייחוס למרכז/רוחב) */
.chat-shell { max-width: 980px; margin: 1.2rem auto; }

/* === API float (שמאל למעלה, בלי לזעזע פריסה) === */
.api-floating {
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 9999;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.18);
  backdrop-filter: blur(6px);
  border-radius: 12px;
  padding: 10px 12px;
  max-width: min(38vw, 420px);
  color: #e6e8f0;
  box-shadow: 0 6px 24px rgba(0,0,0,0.25);
}
.api-floating .api-url {
  font-size: .9rem;
  opacity: .95;
  word-break: break-all;
  text-align: left;
  direction: ltr;
}
.api-floating .stButton > button {
  margin-top: 8px;
  width: 100%;
  height: 40px;
  border-radius: 10px;
  font-weight: 600;
}

/* === בחירת מודל ממורכזת === */
.center-select {
  width: 100%;
  display: flex;
  justify-content: center;
  margin: 0.15rem 0 0.6rem;
}
.center-select .stSelectbox { min-width: 280px; max-width: 420px; }
.center-select .stSelectbox > div { margin: 0 auto; }

/* === כפתור נקה מימין (מתחת לבוחר מודל) === */
.controls-row {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin: .2rem 0 .6rem;
}
.clear-btn .stButton > button {
  height: 44px;
  border-radius: 12px;
  font-weight: 600;
  white-space: nowrap;
  padding: 8px 14px;
}

/* === בועות: רוחב זהה ומרכוז === */
.bubble-wrap {
  width: var(--bubble-w);
  margin: 0 auto;
  position: relative;              /* מאפשר להציב את כפתור ההעתק בצורה absolute */
}
.msg-user, .msg-bot {
  width: 100%;
  color: #e6e8f0;
  padding: 12px 14px;
  border-radius: 14px;
  margin: 8px 0;
  border: 1px solid transparent;
}
.msg-user {
  background: rgba(255,255,255,0.08);
  border-color: rgba(255,255,255,0.08);
}
.msg-bot  {
  background: rgba(100,140,255,0.12);
  border-color: rgba(120,160,255,0.18);
  direction: rtl;                  /* תוכן הבועה נשאר RTL */
}

/* === כפתור "העתק" משמאל לבועת הבוט, ממורכז אנכית, ללא צריכת רוחב === */
.copy-btn {
  position: absolute;
  top: 50%;
  left: -8px;                      /* צמוד לצד שמאל של הבועה */
  transform: translate(-100%, -50%); /* מחוץ לבועה ובדיוק באמצע הגובה */
  z-index: 1;
}
.copy-btn button {
  font-size: .95rem;
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,0.25);
  background: rgba(255,255,255,0.08);
  color: #fff;
  cursor: pointer;
  min-width: 72px;
}
.copy-btn button:hover { background: rgba(255,255,255,0.16); }
.copy-btn button.copied {
  opacity: 0.85;
  border-color: rgba(120,200,120,.8);
  box-shadow: 0 0 0 2px rgba(120,200,120,.15) inset;
}

/* מקור טקסט חבוי לגמרי (ל-fallback של העתקה) */
.visually-hidden {
  position: absolute;
  left: -9999px;
  height: 0;
  overflow: hidden;
}

/* חותמות זמן – ממורכז */
.ts {
  width: 100%;
  text-align: center;
  font-size: 0.85rem;
  opacity: 0.85;
  margin: 6px 0 10px;
}

/* שדה הודעה */
textarea { min-height: 140px !important; resize: vertical !important; font-size: 1rem; }

/* כפתור שליחה */
.stButton > button[kind="primary"] {
  width: 100%;
  border-radius: 12px;
  padding: 10px 14px;
  font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# === כותרת ===
st.title("Local Ollama Chat")

# === פאנל API צף משמאל למעלה ===
with st.container():
    st.markdown('<div class="api-floating">', unsafe_allow_html=True)
    st.markdown(f'<div class="api-url"><b>API_URL</b>: {html.escape(API_URL or "(missing)")}</div>', unsafe_allow_html=True)
    # כפתור בדיקה – התוצאה ב-toast כדי לא להזיז פריסה
    if st.button("בדיקת חיבור ל־API 🔧", key="api_check_btn"):
        try:
            health = requests.get(API_URL.replace("/chat", "/health"), timeout=5).json()
            st.toast(f"API OK: {health}", icon="✅")
        except Exception as e:
            st.toast(f"API health failed: {e}", icon="❌")
    st.markdown('</div>', unsafe_allow_html=True)

# ====== GUARD RAILS ======
if not API_URL or not APP_API_KEY:
    st.error("חסר API_URL או APP_API_KEY. ודא/י קובץ .env (ראה/י .env.example).")
    st.stop()

# ====== SESSION ======
if "history" not in st.session_state:
    # נשמור רק זמנים (ללא מדידת זמן תגובה)
    st.session_state.history = []  # {"role": "user"/"bot", "text": "...", "ts": "HH:MM:SS"}

if "model_choice" not in st.session_state:
    base_opts = [m for m in ["phi", "mistral", "qwen2.5:3b"] if m]
    opts = []
    if DEFAULT_MODEL and DEFAULT_MODEL not in base_opts:
        opts = [DEFAULT_MODEL] + base_opts
    else:
        opts = [DEFAULT_MODEL] + base_opts if DEFAULT_MODEL else base_opts
    st.session_state.model_choice = opts[0] if opts else ""

# ====== בוחר מודל ממורכז + נקה מימין (יחסית לחלון ההודעות) ======
st.markdown('<div class="chat-shell">', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="center-select">', unsafe_allow_html=True)
    opts = sorted({m for m in [DEFAULT_MODEL, "phi", "mistral", "qwen2.5:3b"] if m})
    st.session_state.model_choice = st.selectbox(
        "בחר/י מודל",
        options=opts,
        index=opts.index(st.session_state.model_choice) if st.session_state.model_choice in opts else 0,
        label_visibility="visible",
        key="model_select_centered"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="controls-row">', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        if st.button("נקה שיחה", key="clear_history_btn"):
            st.session_state.history = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.caption("טיפ: אפשר לגרור את שדה ההודעה כדי להגדיל; הכל תומך ב־RTL (עברית).")
st.markdown('</div>', unsafe_allow_html=True)  # chat-shell

# ====== CHAT INPUT ======
with st.form("chat_form", clear_on_submit=True):
    user_msg = st.text_area("הודעת משתמש", placeholder="כתוב/י הודעה למודל…")
    submit = st.form_submit_button("שלח", type="primary", use_container_width=True)

# ====== SEND ======
if submit and user_msg.strip():
    headers = {"Authorization": f"Bearer {APP_API_KEY}", "Content-Type": "application/json"}
    messages = [{"role": "user", "content": user_msg}]
    payload = {"model": st.session_state.model_choice, "messages": messages, "stream": False}

    st.session_state.history.append({"role": "user", "text": user_msg, "ts": datetime.now().strftime("%H:%M:%S")})

    with st.spinner("המודל חושב…"):
        t0 = time.perf_counter()
        try:
            # --- בדיקת מקור: קודם API, ואז מצב Ollama ---
            try:
                h = requests.get(API_URL.replace("/chat", "/health"), timeout=3)
                h.raise_for_status()
                hdata = h.json()
            except Exception as he:
                # API לא זמין = בעיית מקור; מציגים רק את זו ועוצרים
                st.warning(f"⚠️ API לא זמין: {he}")
                raise SystemExit

            # אם ה-API חי אבל Ollama לא זמין – בעיית מקור
            if not hdata.get("ollama", False):
                st.warning("⚠️ שרת Ollama לא זמין/כבוי. הפעל את Ollama ונסה שוב.")
                raise SystemExit

            # --- במצב תקין ממשיכים לשלוח את בקשת /chat ---
            r = requests.post(API_URL, json=payload, headers=headers, timeout=120)
            if DEBUG:
                st.caption(f"HTTP {r.status_code} | raw: {r.text[:300] if r.text else '(no body)'}")

            # שגיאת HTTP מהשרת (למשל 401, 404, 502) – זו בעיית המקור עכשיו
            if r.status_code >= 400:
                try:
                    err_detail = r.json().get("detail") or r.text or f"HTTP {r.status_code}"
                except Exception:
                    err_detail = r.text or f"HTTP {r.status_code}"
                st.warning(f"⚠️ {err_detail}")
                raise SystemExit

            # תשובת 200 תקינה – מפענחים notice/answer
            data = r.json()
            notice = (data.get("notice") or "").strip()
            ans = (data.get("answer") or "").strip()

            if notice:
                # אם יש notice (למשל מודל לא מותקן) – זו ההתראה היחידה
                st.warning(f"⚠️ {notice}")
                raise SystemExit  # לא מציגים "לא החזיר תשובה" בנוסף

            if not ans:
                # אין notice, אבל גם אין תשובה – בעיית מקור: "לא החזיר תשובה"
                st.warning("⚠️ המודל לא החזיר תשובה. נסו/י לשנות ניסוח או מודל.")
                raise SystemExit

            # הצלחה: מוסיפים לבוט להיסטוריה
            st.session_state.history.append({
                "role": "bot",
                "text": ans,
                "ts": datetime.now().strftime("%H:%M:%S")
            })

        except requests.exceptions.ReadTimeout:
            st.error("⏳ בקשת הצ'אט חצתה את מגבלת הזמן (timeout). שקלו להגדיל timeout או לבדוק את זמני התגובה.")
        except SystemExit:
            # כבר הצגנו את התראה/שגיאה המתאימה לפי בעיית המקור
            pass
        except Exception as e:
            st.error(f"שגיאה: {e}")

# ====== HELPERS ======
def render_user(text: str, ts: str):
    safe = html.escape(text)
    st.markdown(f"""
<div class='chat-shell'>
  <div class='bubble-wrap'>
    <!-- זמן מעל הבועה -->
    <div class='ts' style="width:100%;text-align:center;font-size:.85rem;opacity:.85;margin:6px 0 10px;">
      {html.escape(ts)}
    </div>
    <div class='msg-user'>🧑‍💻 {safe}</div>
  </div>
</div>
""", unsafe_allow_html=True)


def render_bot(text: str, ts: str, idx: int):
    safe_text = (text.replace("&", "&amp;")
                      .replace("<", "&lt;")
                      .replace(">", "&gt;"))

    from math import ceil
    rows = max(3, min(40, ceil(len(text) / 48) + text.count("\n") + 1))
    height = 98 + rows * 26  # מרווח קטן לטיימסטמפ שמעל

    html_block = f"""
<div style="max-width:980px;margin:1.2rem auto;position:relative;">
  <div style="width:86%;margin:0 auto;position:relative;">
    <!-- זמן מעל הבועה (בתוך iframe חייבים להגדיר צבע) -->
    <div style="width:100%;text-align:center;font-size:.85rem;opacity:.85;margin:6px 0 10px; color:#e6e8f0;">
      {ts}
    </div>

    <!-- כפתור העתק משמאל, ממורכז אנכית -->
    <div style="position:absolute;top:50%;left:-8px;transform:translate(-100%,-50%);z-index:1;">
      <button
        style="font-size:.95rem;padding:8px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.25);
               background:rgba(255,255,255,.08);color:#fff;cursor:pointer;min-width:72px;"
        onclick="(async () => {{
          try {{
            const area = document.getElementById('copy_src_{idx}');
            const txt = area.value;
            if (navigator.clipboard && window.isSecureContext) {{
              await navigator.clipboard.writeText(txt);
            }} else {{
              area.focus(); area.select(); document.execCommand('copy'); area.blur();
            }}
            this.textContent = 'הועתק ✔';
            setTimeout(() => {{ this.textContent = 'העתק'; }}, 1200);
          }} catch (e) {{
            this.textContent = 'נכשל ✖';
            setTimeout(() => {{ this.textContent = 'העתק'; }}, 1200);
          }}
        }})()"
      >העתק</button>
    </div>

    <!-- בועת הבוט -->
    <div style="background:rgba(100,140,255,.12);border:1px solid rgba(120,160,255,.18);
                padding:12px 14px;border-radius:14px;margin:8px 0;color:#e6e8f0;direction:rtl;">
      🤖 {safe_text}
    </div>

    <!-- מקור טקסט להעתקה (חבוי לגמרי) -->
    <textarea id="copy_src_{idx}" style="position:absolute;left:-9999px;height:0;overflow:hidden;">{safe_text}</textarea>
  </div>
</div>
"""
    st_html(html_block, height=height)

# ====== HISTORY ======
for i, item in enumerate(st.session_state.history):
    if item["role"] == "user":
        render_user(item["text"], item["ts"])
    else:
        render_bot(item["text"], item["ts"], i)