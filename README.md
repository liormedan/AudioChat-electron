# 🎧 Audio Chat QT — AI-Powered Audio Toolkit

מערכת מודרנית לעריכת שמע, העלאת קבצים, הפעלת מודלים של בינה מלאכותית, וניהול פרויקטים — הכל עם ממשק גרפי מבוסס PyQt6 ו־Material Design.

---

## 🚀 תכונות עיקריות

### 🟦 Core Workflow
- 🏠 **Home** — צ'אט מבוסס AI עם אפשרות להעלות קבצי שמע.
- ⚡ **AI Audio Actions** — הפעלת פעולות חכמות על השמע באמצעות מודלים של למידת מכונה.
- 📤 **Audio Exports** — ייצוא שמע לאחר עריכה בפורמטים שונים.
- 📊 **File Stats** — דף סטטיסטיקות עבור הקבצים שהועלו (כמות, סוג, משך, תאריכים).

### 🛠️ Advanced
- 🧠 **AI Terminal** — מסוף להפעלת פקודות AI מותאמות אישית.
- 🧬 **LLM Management** — ניהול מודלים שפתיים (Large Language Models).

### ⚙️ System
- 🔐 **Auth Settings** — הגדרות התחברות והרשאות.
- 👤 **Profile** — ניהול פרופיל משתמש.
- 🗃️ **Database Management** — גישה לבסיס הנתונים וניהול תכני שמע.

---

## 🧩 מבנה התיקיות

```
Audio-Chat-qt/
├── my_audio_app/
│   ├── main.py
│   └── src/
│       ├── ui/
│       │   ├── main_window.py
│       │   ├── widgets/
│       │   │   └── sidebar.py
│       │   └── pages/
│       │       ├── home_page.py
│       │       ├── audio_actions_page.py
│       │       ├── file_stats_page.py
│       │       └── ...
│       ├── data/
│       │   └── models/
│       └── services/
├── .kiro/
│   └── specs/
│       └── file-statistics-dashboard/
└── requirements.txt
```

---

## 🛠️ התקנה והרצה

1. **שיבוט הפרויקט:**
```bash
git clone https://github.com/liormedan/AudioChatQt.git
cd AudioChatQt
```

2. **יצירת סביבה וירטואלית:**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. **התקנת תלויות:**
```bash
pip install -r requirements.txt
```

4. **הרצה:**
```bash
python my_audio_app/main.py
```

---

## 🎨 עיצוב

- מבוסס על **qt-material**
- נושא עיצוב: **dark_blue.xml**
- תמיכה בנושאות נוספים: dark_amber, dark_teal

---

## 📦 תלויות עיקריות

- **PyQt6** — ממשק גרפי מודרני
- **qt-material** — עיצוב Material Design
- **numpy, scipy, matplotlib** — עיבוד נתונים וגרפים
- **librosa** — ניתוח קבצי אודיו
- **openai / transformers** — מודלי AI (בהמשך)

---

## 💡 רעיונות להמשך

- שילוב מודלים קוליים כמו **Whisper**
- הפעלת מודלים גנרטיביים על אודיו (**AudioLM** / **Bark**)
- ייצוא **JSON** של תמלול, רגשות, ומטא-דאטה
- אינטגרציה עם **cloud services** לעיבוד מתקדם

---

## 🔧 פיתוח

### מבנה Specs
הפרויקט משתמש במתודולוגיית **Spec-Driven Development**:
- **Requirements** — דרישות מפורטות עם user stories
- **Design** — ארכיטקטורה ועיצוב מערכת
- **Tasks** — תוכנית יישום מסודרת

### התחלת פיתוח
1. עיין בקבצי הspec ב-`.kiro/specs/`
2. בחר משימה מ-`tasks.md`
3. הפעל את הכלי "Start task" ב-Kiro IDE

---

## 👤 יוצרים

- **פיתוח:** [@liormedan](https://github.com/liormedan)
- **מנטורינג בינה מלאכותית:** ChatGPT & Kiro AI

---

## ⚖️ רישיון

MIT License

---

**רוצה לתרום לפרויקט?** פתח issue או שלח pull request!
