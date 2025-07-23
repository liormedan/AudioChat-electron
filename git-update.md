# עדכון הגיט עם השינויים האחרונים

בצע את הפקודות הבאות כדי לעדכן את הגיט עם השינויים שביצענו:

```bash
# הוספת כל השינויים
git add .

# יצירת קומיט עם הודעה מתארת
git commit -m "עיצוב מחדש של הממשק: רקע שחור וטקסט לבן, הוספת דף בית חדש"

# דחיפה לרפוזיטורי המרוחק
git push origin main
```

אם אתה רוצה לראות את השינויים הספציפיים לפני הקומיט:

```bash
# הצגת השינויים בקבצים
git diff

# הצגת סטטוס מפורט
git status -v
```

אם אתה רוצה להוסיף רק קבצים ספציפיים:

```bash
# הוספת קבצים ספציפיים
git add my_audio_app/src/ui/pages/home_page.py
git add my_audio_app/src/ui/main_window.py
git add my_audio_app/src/ui/pages/file_stats_page.py
git add my_audio_app/src/ui/widgets/sidebar.py
git add .kiro/specs/home-page-redesign/
```