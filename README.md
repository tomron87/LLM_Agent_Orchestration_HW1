<div dir="rtl">

# 🤖 Local AI Chat Agent

> **Interactive chat interface with local LLM using Ollama + FastAPI + Streamlit**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green.svg)](https://ollama.ai/)

---

## 🏫 פרטי הקורס והמטלה
- **שם המטלה:** Assignment 1 – AI Chat Bot  
- **שם הקורס:** LLMs and MultiAgent Orchestration  
- **מרצה:** ד״ר יורם גל  
- **סטודנטים:** איגור נזרנקו ו[שותף נוסף במידת הצורך]  
- **מועד הגשה:** נובמבר 2025  
- **מקום אחסון:** [GitHub Repository](../)

---

## 🎯 מטרות ויעדים
הפרויקט נועד להציג **מערכת צ’אט חכמה הפועלת מול מודל בינה מלאכותית מקומי (LLM)**,  
באמצעות חיבור ישיר למנוע **Ollama** – המאפשר הרצת מודלים לוקאליים כגון `Phi`, `Llama`, או `Mistral`.  

המערכת ממחישה כיצד ניתן:
- להפעיל מודל שפה גדול באופן מקומי, ללא תלות בענן.  
- לחבר בין ממשק משתמש גרפי (Streamlit) לבין שרת API (FastAPI).  
- לנהל תקשורת מלאה עם שרת **Ollama** וליצור חוויית צ’אט אינטראקטיבית.  
- ליישם תהליך פיתוח מקצועי הכולל בדיקות, תיעוד, ופרומפטינג מבוקר.  

---

## 🤖 תיאור כללי של הפרויקט
המערכת כוללת שלושה רכיבים עיקריים:

| רכיב | תיאור |
|------|--------|
| **FastAPI Backend** | מנהל את תקשורת ה־API מול המשתמש, כולל אימות, ניהול בקשות והעברתן ל־Ollama. |
| **Ollama Client Service** | מבצע תקשורת ישירה עם שרת Ollama המקומי באמצעות HTTP ומחזיר את תגובת המודל. |
| **Streamlit UI** | ממשק משתמש גרפי להצגת השיחה בזמן אמת בצורה נוחה ואינטואיטיבית. |

**תרשים זרימת מידע כללי:**
```
User → Streamlit UI → FastAPI → Ollama Client → Ollama Server (Local Model)
```

---

## 🧠 טכנולוגיות עיקריות
- **Python 3.10+**
- **FastAPI** – ממשק API קליל ומהיר  
- **Streamlit** – בניית ממשק גרפי אינטראקטיבי  
- **Ollama** – ניהול מודלי שפה לוקאליים  
- **dotenv / Pydantic** – ניהול משתני סביבה וקונפיגורציה  
- **Pytest** – בדיקות יחידה ואינטגרציה  

---

## 📁 מבנה הפרויקט
מבנה הפרויקט מתואר בפירוט במסמך - [Architecture](documentation/Architecture.md)
```bash
HW1_ai_chat_bot/
├── app/
│   ├── api/routers/chat.py
│   ├── core/config.py
│   ├── services/ollama_client.py
│   ├── services/chat_service.py
│   └── main.py
├── ui/
│   └── streamlit_app.py
├── tests/
│   ├── test_auth_api.py
│   ├── test_chat_happy_errors_api.py
│   ├── test_chat_validation_api.py
│   ├── test_config_settings.py
│   ├── test_health_api.py
│   ├── test_ollama_client_unit.py
│   ├── test_ollama_models_integration.py
│   ├── conftest.py
│   └── pytest.ini
├── scripts/
│   ├── preflight.py
│   └── check_langchain.py
├── documentation/
│   ├── PRD.md
│   ├── Architecture.md
│   ├── Installation_and_Testing.md
│   ├── Prompting_and_Developing.md
│   └── Screenshots_and_Demonstrations.md
├── README.md
├── Makefile
├── .env.example
├── .env
├── requirements.txt
└──  .gitignore
```

---

## 📚 מסמכי תיעוד וניווט
כל מסמכי ההסבר מרוכזים תחת התיקייה [`documentation/`]

| מסמך                                                                                     | תיאור |
|------------------------------------------------------------------------------------------|--------|
| 📘 [PRD.md](documentation/PRD.md)                                                        | מסמך דרישות המוצר – מטרות, תכולה ודרישות המערכת. |
| 🧱 [Architecture.md](documentation/Architecture.md)                                      | מבנה ותרשימי ארכיטקטורה של המערכת. |
| 🧪 [Installation_and_Testing.md](documentation/Installation_and_Testing.md)              | הוראות התקנה, הגדרת סביבה, והרצת בדיקות. |
| 🤖 [Prompting_and_Developing.md](documentation/Prompting_and_Developing.md)              | תיעוד תהליך הפיתוח בעזרת הנחיות AI ו־LLMs. |
| 🖼️ [Screenshots_and_Demonstrations.md](documentation/Screenshots_and_Demonstrations.md) | הדגמות וצילומי מסך של הממשק בפעולה. |

---

## 🚀 שימוש התקנה והפעלה
להוראות ההתקנה וההרצה המלאות יש לעיין במסמך:  
[Installation_and_Testing.md](documentation/Installation_and_Testing.md) 👉

לאחר ההתקנה:
1. הפעל את ה־API (FastAPI)
2. הפעל את ממשק המשתמש (Streamlit)
3. התחל שיחה עם המודל המקומי דרך הממשק הגרפי  

---

## ⚡ הרצה מהירה (Makefile)
למידע המלא על תהליך הבדיקות ופירוט יש לעיין במסמך:  
[Installation_and_Testing.md](documentation/Installation_and_Testing.md) 👉

הפקודות הבאות זמינות להרצה מהירה (דורש GNU Make):
<div dir="ltr">

```
bash
make help               # הצגת פקודות זמינות
make preflight          # בדיקת סביבה
make install            # התקנת תלויות (requirements.txt)
make ollama             # הבטחת שרת Ollama רץ (יפעיל אם צריך)
make api                # שרת FastAPI
make ui                 # ממשק Streamlit
make test               # כל הבדיקות (pytest)
make test-unit          # בדיקות“בדיקות יחידה (not integration)”
make test-integration   # בדיקות אינטגרציה בלבד
make all                # preflight -> install -> ollama -> api(bg) -> ui(fg)
make clean              # ניקוי קבצי cache של Python
```

---
<div dir="rtl">

## 🙌 מה למדנו מהפרויקט
במהלך פיתוח הפרויקט רכשנו ניסיון מעשי בעבודה עם מודלים לוקאליים ובניית תשתית AI מלאה:  
- הבנה מעמיקה של תקשורת בין רכיבי מערכת (Frontend–Backend–Model)  
- יישום תהליך פיתוח מונחה־AI ותיעוד בעזרת prompting מתוכנן  
- בניית סביבת עבודה ניידת ויציבה עם בדיקות תקינות אוטומטיות  
- הקפדה על עקרונות של נגישות, ניידות ותחזוקתיות בקוד ובתיעוד  

---

## 🔗 קישורים מהירים
- 📦 [Repository ראשי (GitHub)](../)
- 🧭 [תיקיית Documentation](documentation/)
  1. 📘 [מסמך PRD – דרישות מוצר](documentation/PRD.md)
  2. 🧱 [Architecture – מבנה מערכת](documentation/Architecture.md)  
  3. 🧪 [Installation & Testing – התקנה ובדיקות](documentation/Installation_and_Testing.md)
  4. 🤖 [Prompting & Developing – פרומפטינג ותהליך פיתוח](documentation/Prompting_and_Developing.md)
  5. 🖼️ [Screenshots – צילומי מסך והדגמות](documentation/Screenshots_and_Demonstrations.md)  

</div>
</div>
</div>

