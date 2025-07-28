# Git Setup Instructions

## הגדרת הרפוזיטורי לראשונה

אם זה פרויקט חדש שטרם הועלה לגיטהאב:

```bash
# אתחול גיט בתיקיית הפרויקט
git init

# הוספת כל הקבצים
git add .

# קומיט ראשון
git commit -m "Initial commit: Audio Chat QT project setup"

# הוספת הרפוזיטורי המרוחק
git remote add origin https://github.com/liormedan/AudioChatQt.git

# העלאה לגיטהאב
git branch -M main
git push -u origin main
```

## אם הרפוזיטורי כבר קיים

```bash
# שיבוט הרפוזיטורי
git clone https://github.com/liormedan/AudioChatQt.git
cd AudioChatQt

# או אם אתה כבר בתיקיית הפרויקט:
git remote add origin https://github.com/liormedan/AudioChatQt.git
git pull origin main
```

## פקודות גיט שימושיות לפיתוח

```bash
# בדיקת סטטוס
git status

# הוספת שינויים
git add .

# קומיט עם הודעה
git commit -m "Add file statistics dashboard feature"

# העלאה לגיטהאב
git push origin main

# יצירת ברנץ' חדש לפיצ'ר
git checkout -b feature/file-stats-dashboard

# מעבר בין ברנצ'ים
git checkout main
git checkout feature/file-stats-dashboard

# מיזוג ברנץ'
git checkout main
git merge feature/file-stats-dashboard
```

## .gitignore מומלץ

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/

# PyQt
*.ui~

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Database
*.db
*.sqlite
*.sqlite3

# Audio files (if large)
*.wav
*.mp3
*.flac
*.m4a
```
