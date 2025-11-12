import html
from datetime import datetime
from math import ceil

import requests
import streamlit as st
from streamlit.components.v1 import html as st_html


def check_api_health(api_url: str, timeout: int = 5, require_ollama: bool = False) -> dict:
    """Ping the FastAPI /health endpoint and optionally enforce Ollama availability."""
    if not api_url:
        raise RuntimeError("API_URL חסר בקובץ הסביבה או משתנה הסביבה.")

    health_url = api_url.replace("/chat", "/health")
    try:
        response = requests.get(health_url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:  # broad by design: we want one UX path for any failure
        raise RuntimeError(f"API לא זמין: {exc}") from exc

    if require_ollama and not data.get("ollama", False):
        raise RuntimeError("⚠️ שרת Ollama לא זמין/כבוי. הפעל/י את Ollama ונסה/י שוב.")

    return data


def build_payload(model: str, prompt: str, temperature: float, stream: bool = False) -> dict:
    """Create the chat payload so request-shaping stays consistent with the API."""
    messages = [{"role": "user", "content": prompt}]
    return {
        "model": model,
        "messages": messages,
        "stream": stream,
        "temperature": float(temperature),
    }


def add_history_entry(role: str, text: str) -> None:
    """Append a timestamped chat item to Streamlit session state."""
    st.session_state.history.append(
        {"role": role, "text": text, "ts": datetime.now().strftime("%H:%M:%S")}
    )


def render_history(history: list[dict]) -> None:
    """Render all chat bubbles using the existing RTL look & feel."""
    for idx, item in enumerate(history):
        if item["role"] == "user":
            _render_user(item["text"], item["ts"])
        else:
            _render_bot(item["text"], item["ts"], idx)


def _render_user(text: str, ts: str) -> None:
    safe = html.escape(text)
    st.markdown(
        f"""
<div class='chat-shell'>
  <div class='bubble-wrap'>
    <div class='ts' style="width:100%;text-align:center;font-size:.85rem;opacity:.85;margin:6px 0 10px;">
      {html.escape(ts)}
    </div>
    <div class='msg-user'>🧑‍💻 {safe}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def _render_bot(text: str, ts: str, idx: int) -> None:
    safe_text = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    rows = max(3, min(40, ceil(len(text) / 48) + text.count("\n") + 1))
    height = 98 + rows * 26

    html_block = f"""
<div style="max-width:980px;margin:1.2rem auto;position:relative;">
  <div style="width:86%;margin:0 auto;position:relative;">
    <div style="width:100%;text-align:center;font-size:.85rem;opacity:.85;margin:6px 0 10px; color:#e6e8f0;">
      {ts}
    </div>
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
    <div style="background:rgba(100,140,255,.12);border:1px solid rgba(120,160,255,.18);
                padding:12px 14px;border-radius:14px;margin:8px 0;color:#e6e8f0;direction:rtl;">
      🤖 {safe_text}
    </div>
    <textarea id="copy_src_{idx}" style="position:absolute;left:-9999px;height:0;overflow:hidden;">{safe_text}</textarea>
  </div>
</div>
"""
    st_html(html_block, height=height)
