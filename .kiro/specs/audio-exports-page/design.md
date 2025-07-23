# Design Document

## Overview

מסמך זה מתאר את העיצוב המפורט של דף "ייצוא אודיו" (Audio Exports) באפליקציית Audio Chat QT. הדף יאפשר למשתמשים לנהל את כל היבטי ייצוא קבצי האודיו, כולל צפייה בקבצים שיוצאו, יצירת ייצואים חדשים, וניהול ייצואים קיימים. העיצוב מתמקד בממשק משתמש נוח, יעילות תפעולית, ואינטגרציה חלקה עם שאר חלקי האפליקציה.

## Architecture

### Component Structure

```
src/ui/pages/
├── exports_page.py (דף ייצוא אודיו)
│   ├── ExportsPage (QWidget)
│   │   ├── ExportsList (רשימת ייצואים)
│   │   ├── ExportDetails (פרטי ייצוא)
│   │   └── ExportsToolbar (סרגל כלים)
└── components/exports/
    ├── exports_list.py (רכיב רשימת ייצואים)
    ├── export_details.py (רכיב פרטי ייצוא)
    ├── export_dialog.py (דיאלוג יצירת ייצוא)
    └── export_item.py (פריט ייצוא בודד)

src/services/
└── export_service.py (שירות לניהול ייצואי אודיו)

src/models/
└── audio_export.py (מודל נתונים לייצוא אודיו)
```

### Integration Points

1. **File Service**: שימוש בשירות הקבצים לגישה לקבצי המקור ולשמירת הקבצים המיוצאים
2. **Chat Service**: אינטגרציה עם שירות הצ'אט לאפשר התייחסות לקבצים מיוצאים בצ'אט
3. **Main Window**: שילוב בחלון הראשי של האפליקציה וניווט
4. **User Preferences**: שימוש בהעדפות המשתמש להגדרות ברירת מחדל לייצוא

## Components and Interfaces

### ExportsPage Class

```python
class ExportsPage(QWidget):
    """דף ייצוא אודיו"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("exportsPage")
        
        # שירותים
        self.export_service = ExportService()
        self.file_service = FileService()
        
        # לייאאוט ראשי
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # סרגל כלים
        self.toolbar = ExportsToolbar()
        self.toolbar.create_export.connect(self.show_export_dialog)
        self.toolbar.search_changed.connect(self.filter_exports)
        self.main_layout.addWidget(self.toolbar)
        
        # אזור תוכן
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # רשימת ייצואים
        self.exports_list = ExportsList()
        self.exports_list.export_selected.connect(self.show_export_details)
        self.exports_list.export_deleted.connect(self.refresh_exports)
        self.content_splitter.addWidget(self.exports_list)
        
        # פרטי ייצוא
        self.export_details = ExportDetails()
        self.export_details.export_updated.connect(self.refresh_exports)
        self.export_details.export_deleted.connect(self.refresh_exports)
        self.content_splitter.addWidget(self.export_details)
        
        # הגדרת יחס גודל התחלתי (60% לרשימה, 40% לפרטים)
        self.content_splitter.setSizes([600, 400])
        
        self.main_layout.addWidget(self.content_splitter)
        
        # טעינת ייצואים
        self.refresh_exports()
```

### AudioExport Model

```python
@dataclass
class AudioExport:
    """מודל לייצוא אודיו"""
    id: str
    source_file_id: str
    name: str
    path: str
    format: str
    size: int
    duration: int
    created_at: datetime
    status: str
    settings: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### ExportService Service

```python
class ExportService:
    """שירות לניהול ייצואי אודיו"""
    
    def __init__(self, db_path: str = None):
        """
        אתחול שירות ייצואים
        
        Args:
            db_path (str, optional): נתיב למסד הנתונים. אם לא מסופק, ישתמש בנתיב ברירת מחדל
        """
        if db_path is None:
            # יצירת תיקיית נתונים אם לא קיימת
            data_dir = os.path.join(os.path.expanduser("~"), ".audio_app", "data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.join(data_dir, "audio_exports.db")
        
        self.db_path = db_path
        self._init_db()
```

## Error Handling

### Error Scenarios

1. **שגיאת ייצוא**
   - הצגת הודעת שגיאה ברורה
   - אפשרות לנסות שוב
   - לוג שגיאה מפורט

2. **קובץ מקור לא קיים**
   - בדיקת קיום קובץ המקור לפני ייצוא
   - הצגת הודעת שגיאה מתאימה
   - הסרת ייצואים שקובץ המקור שלהם נמחק

### Error Display Strategy

- הצגת שגיאות בצורה ברורה וידידותית
- שימוש בדיאלוגים ייעודיים
- הצעת פתרונות אפשריים

## Testing Strategy

### Unit Tests

1. **בדיקות מודל AudioExport**
   - יצירת אובייקט
   - המרת פורמטים
   - תכונות מחושבות

2. **בדיקות ExportService**
   - יצירת ייצוא
   - עדכון ייצוא
   - מחיקת ייצוא
   - חיפוש ייצואים

### Integration Tests

1. **שילוב עם FileService**
   - ייצוא מקבצים קיימים
   - טיפול בקבצים שנמחקו

2. **שילוב עם UI**
   - הצגת רשימת ייצואים
   - יצירת ייצוא חדש
   - עדכון ממשק בזמן אמת