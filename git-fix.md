# פתרון בעיות Git

בצע את הפקודות הבאות בסדר הזה:

```bash
# 1. וודא שאתה בתיקיית הפרויקט הראשית
cd C:\Audio-Chat-main\Audio-Chat-qt

# 2. אתחל את הרפוזיטורי (אם עוד לא עשית זאת)
git init

# 3. הוסף את הרפוזיטורי המרוחק
git remote add origin https://github.com/liormedan/AudioChatQt.git

# 4. הוסף את כל הקבצים לקומיט
git add .

# 5. בצע קומיט ראשוני
git commit -m "Initial commit: Audio Chat QT project setup"

# 6. משוך את התוכן מהרפוזיטורי המרוחק (אם יש)
git pull origin main --allow-unrelated-histories

# 7. פתור התנגשויות אם יש (ערוך את הקבצים הבעייתיים)

# 8. הוסף את הקבצים המתוקנים
git add .

# 9. בצע קומיט למיזוג
git commit -m "Merge remote repository with local changes"

# 10. צור ברנץ' מקומי בשם main
git branch -M main

# 11. דחוף לרפוזיטורי המרוחק
git push -u origin main
```

אם אתה עדיין נתקל בבעיות, נסה:

```bash
# בדוק אילו ברנצ'ים יש לך מקומית
git branch -a

# אם אין לך ברנץ' main, צור אותו
git checkout -b main

# בדוק את הסטטוס
git status

# בצע קומיט אם יש שינויים
git add .
git commit -m "Setup project structure"

# דחוף לרפוזיטורי המרוחק
git push -u origin main
```

אם אתה רוצה לדרוס את מה שיש ברפוזיטורי המרוחק:

```bash
git push -f origin main
```