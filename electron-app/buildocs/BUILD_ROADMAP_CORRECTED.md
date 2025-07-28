# תוכנית בנייה מתוקנת - Audio Chat Studio Electron

## 🎯 מטרת האפליקציה

**Audio Chat Studio** - אפליקציית עריכת אודיו מבוססת צ'אט AI. המשתמשים מעלים קבצי אודיו ונותנים הוראות בשפה טבעית (כמו "הסר רעש רקע", "חתוך את הדקה הראשונה", "הגבר את הקול") והאפליקציה מבצעת את העריכה ומאפשרת ייצוא הקבצים המעובדים.

---

## 📅 לוח זמנים מתוקן

**משך כולל: 10 שבועות (2.5 חודשים)**

| שלב | משך | מטרה |
|-----|-----|------|
| **Phase 1** | 2 שבועות | תשתית צ'אט-אודיו בסיסית |
| **Phase 2** | 3 שבועות | מנוע עריכת אודיו מבוסס AI |
| **Phase 3** | 3 שבועות | תכונות מתקדמות וייצוא |
| **Phase 4** | 2 שבועות | פוליש ובדיקות |

---

## 🚀 Phase 1: תשתית צ'אט-אודיו בסיסית (שבועיים)

### שבוע 1: AudioPage ואינטגרציה עם צ'אט

#### יום 1-2: AudioPage מתקדם
```typescript
// יעדים:
- העלאת קבצים עם drag & drop
- נגן אודיו מתקדם עם waveform
- רשימת קבצים עם metadata
- אינטגרציה עם ChatPage
```

**משימות ספציפיות:**
- [x] שיפור AudioPage עם רכיב FileUploader מתקדם
- [x] אינטגרציה עם wavesurfer.js לwaveform
- [x] רכיב AudioFileManager לניהול קבצים
- [x] חיבור AudioPage ל-ChatPage
- [x] Zustand store לניהול קבצי אודיו

#### יום 3-4: Backend עיבוד אודיו בסיסי
```python
# יעדים:
- שירותי העלאה ואחסון קבצים
- metadata extraction
- פעולות עריכה בסיסיות
- אינטגרציה עם LLM לפרשנות פקודות
```

**משימות ספציפיות:**
- [x] endpoint `/api/audio/upload` עם validation
- [x] endpoint `/api/audio/metadata` עם librosa
- [x] שירות `AudioCommandParser` לפרשנות פקודות
- [x] פעולות עריכה בסיסיות: trim, volume, normalize
- [x] endpoint `/api/audio/execute-command`

#### יום 5: אינטגרציה צ'אט-אודיו
- [x] חיבור ChatPage לפונקציות אודיו
- [x] הצגת קבצי אודיו בצ'אט
- [x] פקודות אודיו בסיסיות בצ'אט
- [ ] feedback למשתמש על סטטוס עיבוד

### שבוע 2: שיפור ממשק הצ'אט לעריכת אודיו

#### יום 1-2: ChatPage מותאם לאודיו
```typescript
// יעדים:
- ממשק צ'אט מותאם לעריכת אודיו
- הצגת קבצי אודיו בשיחה
- פקודות מהירות לעריכה
- preview תוצאות בצ'אט
```

**משימות ספציפיות:**
- [ ] רכיב `AudioChatMessage` להצגת אודיו בצ'אט
- [ ] רכיב `AudioCommandSuggestions` לפקודות מהירות
- [ ] רכיב `AudioPreview` לתוצאות עיבוד
- [ ] אינטגרציה עם audio player בצ'אט

#### יום 3-4: LLMPage מותאם לעריכת אודיו
```typescript
// יעדים:
- הגדרות LLM מותאמות לעריכת אודיו
- system prompts לעריכת אודיו
- בדיקת יכולות עריכה של מודלים
- הגדרות מתקדמות לעיבוד אודיו
```

**משימות ספציפיות:**
- [ ] system prompts מותאמים לעריכת אודיו
- [ ] בדיקת חיבור עם פקודות אודיו לדוגמה
- [ ] הגדרות מודל מותאמות (creativity vs precision)
- [ ] רשימת פקודות נתמכות

#### יום 5: בדיקות ושיפורים
- [ ] בדיקות flow מלא: העלאה → צ'אט → עריכה
- [ ] טיפול בשגיאות ופקודות לא ברורות
- [ ] שיפורי UX
- [ ] תיעוד פקודות

---

## 🔧 Phase 2: מנוע עריכת אודיו מבוסס AI (3 שבועות)

### שבוע 3: פקודות עריכה בסיסיות

#### יום 1-2: מנוע פרשנות פקודות
```python
# יעדים:
- פרשנות פקודות בשפה טבעית
- מיפוי פקודות לפונקציות עריכה
- validation ו-error handling
- feedback למשתמש
```

**משימות ספציפיות:**
- [ ] שירות `AudioCommandInterpreter` עם LLM
- [ ] מיפוי פקודות לפונקציות: trim, volume, fade, normalize
- [ ] validation פרמטרים (זמנים, רמות קול, וכו')
- [ ] מערכת הצעות לפקודות לא ברורות

#### יום 3-4: פעולות עריכה מתקדמות
```python
# יעדים:
- חיתוך וחיבור קטעים
- שינוי עוצמת קול
- fade in/out
- נורמליזציה
```

**משימות ספציפיות:**
- [ ] פונקציות עריכה עם pydub ו-librosa
- [ ] trim_audio(start, end), adjust_volume(factor)
- [ ] fade_in(duration), fade_out(duration)
- [ ] normalize_audio(), remove_silence()
- [ ] combine_audio_files(files, method)

#### יום 5: ממשק עריכה אינטראקטיבי
```typescript
// יעדים:
- הצגת תוצאות עריכה בזמן אמת
- preview לפני שמירה
- undo/redo לפעולות
- היסטוריית עריכה
```

**משימות ספציפיות:**
- [ ] רכיב `AudioEditPreview` עם before/after
- [ ] מערכת undo/redo לפעולות עריכה
- [ ] היסטוריית פקודות עם אפשרות חזרה
- [ ] save/discard changes

### שבוע 4: עיבוד אודיו מתקדם

#### יום 1-2: הסרת רעש ושיפור איכות
```python
# יעדים:
- הסרת רעש רקע
- שיפור איכות קול
- EQ בסיסי
- דחיסה
```

**משימות ספציפיות:**
- [ ] noise reduction עם spectral subtraction
- [ ] EQ פונקציות (bass, treble, mid)
- [ ] dynamic range compression
- [ ] audio enhancement algorithms

#### יום 3-4: פקודות מתקדמות
```python
# יעדים:
- פקודות מורכבות עם מספר שלבים
- batch processing
- conditional operations
- loops ו-automation
```

**משימות ספציפיות:**
- [ ] פרשנות פקודות מורכבות ("הסר רעש ואז הגבר ב-20%")
- [ ] batch operations על מספר קבצים
- [ ] conditional logic ("אם הקול חלש, הגבר")
- [ ] automation scripts

#### יום 5: אופטימיזציה וביצועים
- [ ] אופטימיזציה של אלגוריתמי עיבוד
- [ ] parallel processing לקבצים גדולים
- [ ] caching תוצאות עיבוד
- [ ] progress tracking מתקדם

### שבוע 5: AI Audio Intelligence

#### יום 1-2: ניתוח אודיו חכם
```python
# יעדים:
- זיהוי אוטומטי של בעיות באודיו
- המלצות עריכה
- ניתוח איכות
- אופטימיזציה אוטומטית
```

**משימות ספציפיות:**
- [ ] זיהוי רעש, clipping, silence
- [ ] המלצות עריכה אוטומטיות
- [ ] ניתוח ספקטרלי ו-dynamic range
- [ ] auto-optimization suggestions

#### יום 3-4: ממשק AI מתקדם
```typescript
// יעדים:
- הצגת תובנות AI על האודיו
- המלצות עריכה אינטראקטיביות
- auto-fix options
- learning מהעדפות משתמש
```

**משימות ספציפיות:**
- [ ] רכיב `AudioInsights` עם ניתוח AI
- [ ] רכיב `SmartSuggestions` להמלצות
- [ ] one-click fixes לבעיות נפוצות
- [ ] learning algorithm להעדפות

#### יום 5: בדיקות AI ואינטגרציה
- [ ] בדיקות דיוק המלצות AI
- [ ] בדיקות ביצועים עם AI
- [ ] fine-tuning אלגוריתמים
- [ ] user feedback integration

---

## 📊 Phase 3: תכונות מתקדמות וייצוא (3 שבועות)

### שבוע 6: מערכת ייצוא מתקדמת

#### יום 1-2: ExportPage מלא
```typescript
// יעדים:
- ייצוא בפורמטים שונים
- הגדרות איכות מתקדמות
- batch export
- metadata preservation
```

**משימות ספציפיות:**
- [ ] תמיכה בפורמטים: MP3, WAV, FLAC, OGG, M4A
- [ ] הגדרות bitrate, sample rate, channels
- [ ] batch export עם queue management
- [ ] שמירת metadata ותגים

#### יום 3-4: היסטוריה ופרויקטים
```typescript
// יעדים:
- ניהול פרויקטי עריכה
- שמירת היסטוריית עבודה
- templates לעריכה
- sharing ו-collaboration
```

**משימות ספציפיות:**
- [ ] מערכת פרויקטים לניהול עבודות
- [ ] שמירת היסטוריית עריכה
- [ ] templates לפקודות נפוצות
- [ ] export project settings

#### יום 5: בדיקות ייצוא
- [ ] בדיקות איכות ייצוא
- [ ] בדיקות פורמטים שונים
- [ ] בדיקות metadata
- [ ] performance testing

### שבוע 7: StatsPage ו-Analytics

#### יום 1-2: דף סטטיסטיקות מתקדם
```typescript
// יעדים:
- סטטיסטיקות שימוש
- ניתוח פעילות עריכה
- גרפים ודוחות
- insights על דפוסי עבודה
```

**משימות ספציפיות:**
- [ ] גרפים של פעילות עריכה
- [ ] סטטיסטיקות פקודות פופולריות
- [ ] ניתוח זמני עיבוד
- [ ] דוחות איכות אודיו

#### יום 3-4: ProfilePage ו-SettingsPage מתקדמים
```typescript
// יעדים:
- הגדרות משתמש מתקדמות
- העדפות עריכה
- shortcuts ו-macros
- גיבוי והחזרה
```

**משימות ספציפיות:**
- [ ] העדפות עריכה אישיות
- [ ] keyboard shortcuts מותאמים
- [ ] macros לפקודות מורכבות
- [ ] גיבוי הגדרות וקבצים

#### יום 5: אינטגרציה מלאה
- [ ] חיבור כל הדפים
- [ ] בדיקות flow מלא
- [ ] תיקון bugs
- [ ] UX improvements

### שבוע 8: Cloud ו-Collaboration

#### יום 1-2: Cloud Storage
```python
# יעדים:
- שמירת קבצים בענן
- סנכרון בין מכשירים
- גיבוי אוטומטי
- sharing קבצים
```

**משימות ספציפיות:**
- [ ] אינטגרציה עם AWS S3/Google Drive
- [ ] סנכרון פרויקטים
- [ ] גיבוי אוטומטי של עבודות
- [ ] sharing links לקבצים

#### יום 3-4: Collaboration Features
```typescript
// יעדים:
- שיתוף פרויקטים
- comments ו-feedback
- version control בסיסי
- team workflows
```

**משימות ספציפיות:**
- [ ] שיתוף פרויקטים עם אחרים
- [ ] מערכת comments על עריכות
- [ ] version history לפרויקטים
- [ ] team management בסיסי

#### יום 5: בדיקות Cloud
- [ ] בדיקות סנכרון
- [ ] בדיקות sharing
- [ ] בדיקות ביצועים
- [ ] security testing

---

## 🎨 Phase 4: פוליש ובדיקות (שבועיים)

### שבוע 9: UI/UX Polish

#### יום 1-2: עיצוב מתקדם
```typescript
// יעדים:
- אנימציות חלקות
- מיקרו-אינטראקציות
- responsive design
- accessibility
```

**משימות ספציפיות:**
- [ ] אנימציות לעיבוד אודיו
- [ ] loading states מתקדמים
- [ ] drag & drop משופר
- [ ] keyboard navigation מלא

#### יום 3-4: ביצועים
```typescript
// יעדים:
- אופטימיזציית ביצועים
- memory management
- caching strategy
- bundle optimization
```

**משימות ספציפיות:**
- [ ] lazy loading לרכיבים כבדים
- [ ] audio caching ו-streaming
- [ ] memory cleanup לקבצים גדולים
- [ ] bundle splitting

#### יום 5: UX Testing
- [ ] user testing עם משתמשים אמיתיים
- [ ] feedback collection
- [ ] UX improvements
- [ ] accessibility testing

### שבוע 10: Testing ו-QA

#### יום 1-2: Testing מקיף
```typescript
// יעדים:
- unit tests לכל רכיב
- integration tests
- E2E testing
- audio processing tests
```

**משימות ספציפיות:**
- [ ] tests לפונקציות עריכת אודיו
- [ ] tests לפרשנות פקודות
- [ ] E2E tests לflow מלא
- [ ] performance benchmarks

#### יום 3-4: Bug Fixes ו-Optimization
- [ ] bug triage ו-fixes
- [ ] performance optimization
- [ ] memory leak fixes
- [ ] error handling improvements

#### יום 5: Final QA
- [ ] regression testing
- [ ] final bug fixes
- [ ] documentation update
- [ ] release preparation

---

## 🛠️ טכנולוgiות נדרשות

### Frontend
```json
{
  "dependencies": {
    "wavesurfer.js": "^7.7.3",
    "react-dropzone": "^14.2.3",
    "framer-motion": "^11.0.6",
    "chart.js": "^4.4.1",
    "react-chartjs-2": "^5.2.0"
  }
}
```

### Backend Python
```txt
librosa==0.10.1
pydub==0.25.1
numpy==1.24.3
scipy==1.11.4
soundfile==0.12.1
noisereduce==3.0.0
```

---

## 🎯 מדדי הצלחה מתוקנים

### פונקציונליות
- [ ] העלאת קבצי אודיו עובדת חלק
- [ ] פרשנות פקודות בשפה טבעית מדויקת (90%+)
- [ ] עריכת אודיו איכותית ומהירה
- [ ] ייצוא בפורמטים מרובים
- [ ] ממשק צ'אט אינטואיטיבי

### ביצועים
- [ ] עיבוד קבצי אודיו עד 100MB תוך < 30 שניות
- [ ] זמן תגובה לפקודות < 2 שניות
- [ ] זיכרון < 1GB לקבצים רגילים
- [ ] יציבות 99%+ ללא crashes

### חוויית משתמש
- [ ] learning curve < 10 דקות למשתמש חדש
- [ ] פקודות טבעיות וברורות
- [ ] feedback מיידי על פעולות
- [ ] ממשק נקי ומקצועי

---

**סיכום**: תוכנית זו מתמקדת במטרה האמיתית - יצירת אפליקציית עריכת אודיו מבוססת צ'אט AI שמאפשרת למשתמשים לערוך אודיו באמצעות הוראות בשפה טבעית.