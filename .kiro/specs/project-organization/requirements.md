# Requirements Document

## Introduction

הפרויקט הוא אפליקציית Audio Chat Studio המורכבת מבקאנד FastAPI ופרונטאנד Electron. הצורך הוא לארגן את הפרויקט בצורה נכונה עם קבצי הפעלה מסודרים, כך שהמערכת תעבוד בצורה חלקה ויהיה קל להפעיל אותה.

## Requirements

### Requirement 1

**User Story:** כמפתח, אני רוצה שהבקאנד FastAPI יהיה מאורגן נכון עם נקודת כניסה ברורה, כך שאוכל להפעיל את השרת בקלות.

#### Acceptance Criteria

1. WHEN המפתח מפעיל את הבקאנד THEN המערכת SHALL יצור נקודת כניסה ראשית ב-backend/main.py
2. WHEN השרת מופעל THEN המערכת SHALL טען את כל השירותים הנדרשים מ-backend/api/main.py
3. WHEN השרת רץ THEN המערכת SHALL יהיה זמין על פורט 5000 עם כל ה-endpoints

### Requirement 2

**User Story:** כמפתח, אני רוצה שהפרונטאנד Electron יהיה מסודר עם קבצי הפעלה נכונים, כך שאוכל להפעיל את האפליקציה בקלות.

#### Acceptance Criteria

1. WHEN המפתח מפעיל את הפרונטאנד THEN המערכת SHALL הפעיל את שרת הפיתוח של Vite
2. WHEN שרת הפיתוח רץ THEN המערכת SHALL הפעיל את Electron עם האפליקציה
3. WHEN האפליקציה רצה THEN המערכת SHALL התחבר לבקאנד על פורט 5000

### Requirement 3

**User Story:** כמשתמש, אני רוצה קבצי הפעלה פשוטים ומסודרים, כך שאוכל להפעיל את המערכת בקלות.

#### Acceptance Criteria

1. WHEN המשתמש מפעיל קובץ start.bat THEN המערכת SHALL הפעיל את הבקאנד והפרונטאנד יחד
2. WHEN המערכת מופעלת THEN המערכת SHALL הציג הודעות ברורות על מצב ההפעלה
3. WHEN יש שגיאה THEN המערכת SHALL הציג הודעת שגיאה ברורה בעברית

### Requirement 4

**User Story:** כמפתח, אני רוצה שהמערכת תתמוך בסביבת פיתוח ובסביבת ייצור, כך שאוכל לעבוד בשני המצבים.

#### Acceptance Criteria

1. WHEN המפתח עובד בסביבת פיתוח THEN המערכת SHALL הפעיל hot reload לפרונטאנד
2. WHEN המפתח בונה לייצור THEN המערכת SHALL יצור build מוכן להפצה
3. WHEN המערכת רצה בייצור THEN המערכת SHALL השתמש בקבצים הסטטיים הבנויים

### Requirement 5

**User Story:** כמשתמש, אני רוצה שהמערכת תנהל dependencies נכון, כך שלא יהיו בעיות עם חבילות חסרות.

#### Acceptance Criteria

1. WHEN המשתמש מתקין את המערכת THEN המערכת SHALL בדוק ותתקין את כל ה-dependencies הנדרשים
2. WHEN יש dependency חסר THEN המערכת SHALL הציג הודעה ברורה ותנסה להתקין אותו
3. WHEN המערכת מופעלת THEN המערכת SHALL וודא שכל השירותים זמינים לפני ההפעלה