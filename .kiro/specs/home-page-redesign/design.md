# Design Document

## Overview

מסמך זה מתאר את העיצוב המפורט של דף הבית (Home) החדש באפליקציית Audio Chat QT ואת השינויים בצבעי התפריט. דף הבית יכלול אזור צ'אט ואזור להעלאת קבצים בפריסה דו-פאנלית, וצבעי התפריט ישונו מכחול ללבן לשיפור הנראות והקריאות.

## Architecture

### Component Structure

```
src/ui/pages/
├── home_page.py (דף הבית החדש)
│   ├── HomePage (QWidget)
│   │   ├── ChatPanel (אזור צ'אט)
│   │   └── FileUploadPanel (אזור העלאת קבצים)
└── components/
    ├── chat/
    │   ├── chat_message.py
    │   ├── chat_input.py
    │   └── chat_history.py
    └── file_upload/
        ├── file_uploader.py
        ├── recent_files_list.py
        └── upload_progress.py
```

### Integration Points

1. **Sidebar Navigation**: עדכון צבעי התפריט בקובץ `sidebar.py`
2. **Main Window**: שילוב דף הבית החדש ב-`main_window.py`
3. **Theme Integration**: התאמת צבעים לערכת הנושא הכללית

## Components and Interfaces

### HomePage Class

```python
class HomePage(QWidget):
    """דף הבית המשלב צ'אט והעלאת קבצים"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("homePage")
        
        # יצירת הלייאאוט הראשי
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # יצירת הפאנלים
        self.chat_panel = self._create_chat_panel()
        self.file_panel = self._create_file_panel()
        
        # הוספת הפאנלים ללייאאוט
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.chat_panel)
        self.splitter.addWidget(self.file_panel)
        self.splitter.setSizes([int(self.width() * 0.6), int(self.width() * 0.4)])
        
        self.main_layout.addWidget(self.splitter)
        
        # חיבור אותות
        self.connect_signals()
        
        # טעינת היסטוריית צ'אט
        self.load_chat_history()
    
    def _create_chat_panel(self):
        """יצירת פאנל צ'אט"""
        panel = QWidget()
        panel.setObjectName("chatPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # כותרת
        title = QLabel("צ'אט")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # היסטוריית צ'אט
        self.chat_history = ChatHistory()
        layout.addWidget(self.chat_history)
        
        # קלט צ'אט
        self.chat_input = ChatInput()
        layout.addWidget(self.chat_input)
        
        return panel
    
    def _create_file_panel(self):
        """יצירת פאנל העלאת קבצים"""
        panel = QWidget()
        panel.setObjectName("filePanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # כותרת
        title = QLabel("העלאת קבצים")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # אזור העלאה
        self.file_uploader = FileUploader()
        layout.addWidget(self.file_uploader)
        
        # רשימת קבצים אחרונים
        self.recent_files = RecentFilesList()
        layout.addWidget(self.recent_files)
        
        return panel
    
    def connect_signals(self):
        """חיבור אותות בין רכיבים"""
        # שליחת הודעה בצ'אט
        self.chat_input.message_sent.connect(self.on_message_sent)
        
        # העלאת קובץ
        self.file_uploader.file_uploaded.connect(self.on_file_uploaded)
        
        # בחירת קובץ מהרשימה
        self.recent_files.file_selected.connect(self.on_file_selected)
    
    def on_message_sent(self, message):
        """טיפול בשליחת הודעה"""
        # הוספת הודעת משתמש להיסטוריה
        self.chat_history.add_user_message(message)
        
        # כאן יש להוסיף קוד לשליחת ההודעה ל-AI וקבלת תשובה
        # לדוגמה:
        self.process_message(message)
    
    def process_message(self, message):
        """עיבוד הודעה ושליחה ל-AI"""
        # כאן יש להוסיף קוד לעיבוד ההודעה
        # לדוגמה:
        response = "זוהי תשובת דוגמה מה-AI. בהמשך יש להחליף בתשובה אמיתית."
        
        # הוספת תשובת AI להיסטוריה
        self.chat_history.add_ai_message(response)
    
    def on_file_uploaded(self, file_info):
        """טיפול בהעלאת קובץ"""
        # עדכון רשימת הקבצים האחרונים
        self.recent_files.add_file(file_info)
        
        # הודעה בצ'אט על העלאת הקובץ
        self.chat_history.add_system_message(f"הקובץ {file_info.name} הועלה בהצלחה.")
    
    def on_file_selected(self, file_info):
        """טיפול בבחירת קובץ מהרשימה"""
        # הודעה בצ'אט על בחירת הקובץ
        self.chat_history.add_system_message(f"הקובץ {file_info.name} נבחר.")
    
    def load_chat_history(self):
        """טעינת היסטוריית צ'אט"""
        # כאן יש להוסיף קוד לטעינת היסטוריית צ'אט מהמסד נתונים
        # לדוגמה:
        if self.is_first_time_user():
            self.chat_history.add_ai_message("ברוכים הבאים ל-Audio Chat Studio! במה אוכל לעזור לך היום?")
        else:
            # טעינת היסטוריה קודמת
            pass
    
    def is_first_time_user(self):
        """בדיקה האם זהו משתמש חדש"""
        # כאן יש להוסיף קוד לבדיקה האם זהו משתמש חדש
        # לדוגמה:
        return True  # לצורך הדוגמה
```

### ChatHistory Component

```python
class ChatHistory(QScrollArea):
    """רכיב להצגת היסטוריית צ'אט"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # יצירת ווידג'ט פנימי
        self.container = QWidget()
        self.setWidget(self.container)
        
        # לייאאוט להודעות
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        
        # הוספת מרווח בסוף
        self.layout.addStretch()
    
    def add_user_message(self, text):
        """הוספת הודעת משתמש"""
        message = ChatMessage(text, "user")
        self._add_message(message)
    
    def add_ai_message(self, text):
        """הוספת הודעת AI"""
        message = ChatMessage(text, "ai")
        self._add_message(message)
    
    def add_system_message(self, text):
        """הוספת הודעת מערכת"""
        message = ChatMessage(text, "system")
        self._add_message(message)
    
    def _add_message(self, message):
        """הוספת הודעה ללייאאוט"""
        # הסרת המרווח
        self.layout.removeItem(self.layout.itemAt(self.layout.count() - 1))
        
        # הוספת ההודעה
        self.layout.addWidget(message)
        
        # הוספת מרווח מחדש
        self.layout.addStretch()
        
        # גלילה לתחתית
        QTimer.singleShot(50, self.scroll_to_bottom)
    
    def scroll_to_bottom(self):
        """גלילה לתחתית הצ'אט"""
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
    
    def clear_history(self):
        """ניקוי היסטוריית הצ'אט"""
        # הסרת כל ההודעות
        while self.layout.count() > 1:  # שמירה על המרווח בסוף
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
```

### ChatMessage Component

```python
class ChatMessage(QFrame):
    """רכיב להצגת הודעת צ'אט בודדת"""
    
    def __init__(self, text, message_type="user", parent=None):
        super().__init__(parent)
        self.message_type = message_type
        self.text = text
        
        # עיצוב הודעה
        self.setObjectName(f"{message_type}Message")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        
        # לייאאוט
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # תוכן ההודעה
        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(text_label)
        
        # זמן שליחה
        time_label = QLabel(QDateTime.currentDateTime().toString("HH:mm"))
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        time_label.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(time_label)
        
        # עיצוב לפי סוג הודעה
        self._apply_style()
    
    def _apply_style(self):
        """החלת עיצוב לפי סוג הודעה"""
        base_style = """
            border-radius: 8px;
            padding: 5px;
            margin: 2px 0;
        """
        
        if self.message_type == "user":
            self.setStyleSheet(base_style + """
                background-color: #E3F2FD;
                border: 1px solid #BBDEFB;
                margin-left: 50px;
            """)
        elif self.message_type == "ai":
            self.setStyleSheet(base_style + """
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                margin-right: 50px;
            """)
        else:  # system
            self.setStyleSheet(base_style + """
                background-color: #FFF8E1;
                border: 1px solid #FFECB3;
                font-style: italic;
            """)
```

### ChatInput Component

```python
class ChatInput(QWidget):
    """רכיב קלט להזנת הודעות צ'אט"""
    
    # אות לשליחת הודעה
    message_sent = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # לייאאוט
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 0)
        
        # שדה טקסט
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("הקלד הודעה...")
        self.text_edit.setMaximumHeight(80)
        layout.addWidget(self.text_edit)
        
        # כפתור שליחה
        self.send_button = QPushButton("שלח")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)
        
        # חיבור מקש Enter לשליחה
        self.text_edit.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """סינון אירועים לתפיסת מקש Enter"""
        if obj is self.text_edit and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)
    
    def send_message(self):
        """שליחת הודעה"""
        text = self.text_edit.toPlainText().strip()
        if text:
            self.message_sent.emit(text)
            self.text_edit.clear()
```

### FileUploader Component

```python
class FileUploader(QWidget):
    """רכיב להעלאת קבצי אודיו"""
    
    # אות להעלאת קובץ
    file_uploaded = pyqtSignal(object)  # FileInfo object
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # לייאאוט
        layout = QVBoxLayout(self)
        
        # אזור גרירה והשלכה
        self.drop_area = QLabel("גרור קבצי אודיו לכאן או לחץ לבחירה")
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setStyleSheet("""
            border: 2px dashed #BBDEFB;
            border-radius: 8px;
            padding: 30px;
            background-color: #E3F2FD;
            color: #1976D2;
        """)
        self.drop_area.setAcceptDrops(True)
        self.drop_area.mousePressEvent = self.on_drop_area_click
        layout.addWidget(self.drop_area)
        
        # פרוגרס בר
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # התקנת מסנן אירועים לגרירה והשלכה
        self.drop_area.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """סינון אירועים לתפיסת גרירה והשלכה"""
        if obj is self.drop_area:
            if event.type() == QEvent.Type.DragEnter:
                self.on_drag_enter(event)
                return True
            elif event.type() == QEvent.Type.Drop:
                self.on_drop(event)
                return True
        return super().eventFilter(obj, event)
    
    def on_drag_enter(self, event):
        """טיפול באירוע גרירה מעל האזור"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_area.setStyleSheet("""
                border: 2px dashed #1976D2;
                border-radius: 8px;
                padding: 30px;
                background-color: #BBDEFB;
                color: #0D47A1;
            """)
    
    def on_drop(self, event):
        """טיפול באירוע השלכה"""
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if self.is_audio_file(file_path):
                self.upload_file(file_path)
        
        # החזרת העיצוב המקורי
        self.drop_area.setStyleSheet("""
            border: 2px dashed #BBDEFB;
            border-radius: 8px;
            padding: 30px;
            background-color: #E3F2FD;
            color: #1976D2;
        """)
    
    def on_drop_area_click(self, event):
        """טיפול בלחיצה על אזור ההשלכה"""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Audio Files (*.mp3 *.wav *.flac *.ogg *.m4a)")
        
        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            for file_path in files:
                self.upload_file(file_path)
    
    def is_audio_file(self, file_path):
        """בדיקה האם הקובץ הוא קובץ אודיו"""
        audio_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a']
        return any(file_path.lower().endswith(ext) for ext in audio_extensions)
    
    def upload_file(self, file_path):
        """העלאת קובץ"""
        # הצגת פרוגרס בר
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        # סימולציה של העלאה
        for i in range(101):
            self.progress.setValue(i)
            QApplication.processEvents()
            time.sleep(0.01)  # סימולציה של זמן העלאה
        
        # הסתרת פרוגרס בר
        self.progress.setVisible(False)
        
        # יצירת אובייקט FileInfo
        file_info = self.create_file_info(file_path)
        
        # שידור אות העלאה
        self.file_uploaded.emit(file_info)
    
    def create_file_info(self, file_path):
        """יצירת אובייקט FileInfo מקובץ"""
        # כאן יש להוסיף קוד לחילוץ מידע מקובץ האודיו
        # לדוגמה:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_type = os.path.splitext(file_path)[1][1:].upper()
        
        # יצירת אובייקט FileInfo
        file_info = SimpleNamespace()
        file_info.name = file_name
        file_info.path = file_path
        file_info.size = file_size
        file_info.type = file_type
        file_info.upload_date = QDateTime.currentDateTime()
        
        return file_info
```

### RecentFilesList Component

```python
class RecentFilesList(QWidget):
    """רכיב להצגת רשימת קבצים אחרונים"""
    
    # אות לבחירת קובץ
    file_selected = pyqtSignal(object)  # FileInfo object
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # לייאאוט
        layout = QVBoxLayout(self)
        
        # כותרת
        title = QLabel("קבצים אחרונים")
        title.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(title)
        
        # רשימת קבצים
        self.file_list = QListWidget()
        self.file_list.setAlternatingRowColors(True)
        self.file_list.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.file_list)
        
        # טעינת קבצים אחרונים
        self.load_recent_files()
    
    def load_recent_files(self):
        """טעינת קבצים אחרונים"""
        # כאן יש להוסיף קוד לטעינת קבצים אחרונים ממסד הנתונים
        # לדוגמה:
        pass
    
    def add_file(self, file_info):
        """הוספת קובץ לרשימה"""
        # יצירת פריט רשימה
        item = QListWidgetItem()
        item.setText(file_info.name)
        item.setData(Qt.ItemDataRole.UserRole, file_info)
        
        # הוספת אייקון לפי סוג קובץ
        icon = self.get_file_icon(file_info.type)
        item.setIcon(icon)
        
        # הוספה לרשימה בראש
        self.file_list.insertItem(0, item)
    
    def get_file_icon(self, file_type):
        """קבלת אייקון לפי סוג קובץ"""
        # כאן יש להוסיף קוד להחזרת אייקון מתאים
        # לדוגמה:
        return QIcon.fromTheme("audio-x-generic")
    
    def on_item_clicked(self, item):
        """טיפול בלחיצה על פריט ברשימה"""
        file_info = item.data(Qt.ItemDataRole.UserRole)
        self.file_selected.emit(file_info)
```

## Sidebar Color Changes

```python
# עדכון סגנון התפריט בקובץ sidebar.py

class Sidebar(QWidget):
    # ...
    
    def _add_section(self, title, items):
        section_label = QLabel(title)
        section_label.setStyleSheet("font-weight: bold; margin-top: 10px; color: white; opacity: 0.8;")
        self.layout.addWidget(section_label)

        for text, page in items:
            self._add_button(text, page)
    
    def _add_button(self, text, page_name):
        button = QPushButton(text)
        button.setObjectName("sidebarButton")
        button.setCheckable(True)
        button.setAutoExclusive(True)
        button.clicked.connect(lambda: self.page_changed.emit(page_name))
        
        # עיצוב כפתור עם טקסט לבן
        button.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 12px;
                border: none;
                border-radius: 4px;
                color: white;
                font-weight: normal;
            }
            QPushButton:checked {
                background-color: rgba(255, 255, 255, 0.2);
                font-weight: bold;
            }
            QPushButton:hover:!checked {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        
        self.layout.addWidget(button)
        self.buttons[page_name] = button
```

## Data Models

### FileInfo Model

```python
@dataclass
class FileInfo:
    """מידע על קובץ אודיו"""
    name: str
    path: str
    size: int
    type: str
    duration: int = 0
    upload_date: datetime = None
    
    @property
    def size_formatted(self) -> str:
        """החזרת גודל קובץ בפורמט קריא"""
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        else:
            return f"{self.size / (1024 * 1024):.1f} MB"
    
    @property
    def duration_formatted(self) -> str:
        """החזרת משך בפורמט קריא"""
        minutes, seconds = divmod(self.duration, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
```

### ChatMessage Model

```python
@dataclass
class ChatMessageData:
    """מידע על הודעת צ'אט"""
    text: str
    sender: str  # "user", "ai", "system"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
```

## Error Handling

### Error Scenarios

1. **שגיאת העלאת קובץ**
   - הצגת הודעת שגיאה ברורה
   - אפשרות לנסות שוב
   - לוג שגיאה מפורט

2. **שגיאת תקשורת עם AI**
   - הצגת הודעת שגיאה בצ'אט
   - אפשרות לנסות שוב
   - שמירת ההודעה שלא נשלחה

### Error Display Strategy

- הצגת שגיאות בצורה ברורה וידידותית
- שימוש באייקונים ברורים
- הצעת פתרונות אפשריים

## Testing Strategy

### Unit Tests

1. **בדיקות רכיבי צ'אט**
   - שליחת הודעות
   - קבלת תשובות
   - הצגת היסטוריה

2. **בדיקות רכיבי העלאת קבצים**
   - העלאת קבצים תקינים
   - טיפול בקבצים לא תקינים
   - הצגת רשימת קבצים

### Integration Tests

1. **שילוב צ'אט והעלאת קבצים**
   - העלאת קובץ והתייחסות אליו בצ'אט
   - שליחת הודעות על קבצים

2. **שילוב עם מערכת הנתונים**
   - שמירת היסטוריית צ'אט
   - שמירת מידע על קבצים