from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, 
                           QListWidgetItem, QHBoxLayout, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction, QCursor

from .file_info import FileInfo


class RecentFilesList(QWidget):
    """רכיב להצגת רשימת קבצים אחרונים"""
    
    # אותות
    file_selected = pyqtSignal(FileInfo)  # אות שנשלח כאשר נבחר קובץ
    file_play_requested = pyqtSignal(FileInfo)  # אות שנשלח כאשר מבקשים לנגן קובץ
    file_delete_requested = pyqtSignal(FileInfo)  # אות שנשלח כאשר מבקשים למחוק קובץ
    
    def __init__(self, parent=None, max_files=10):
        """
        יוצר רכיב רשימת קבצים אחרונים
        
        Args:
            parent (QWidget, optional): הווידג'ט ההורה
            max_files (int, optional): מספר מקסימלי של קבצים להצגה
        """
        super().__init__(parent)
        self.setObjectName("recentFilesList")
        self.max_files = max_files
        
        # עיצוב
        self.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                border-bottom: 1px solid #333;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #2c3e50;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #263238;
            }
            QLabel#emptyLabel {
                color: #888;
                font-style: italic;
            }
        """)
        
        # לייאאוט ראשי
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        
        # כותרת
        title_layout = QHBoxLayout()
        title = QLabel("קבצים אחרונים")
        title.setStyleSheet("font-weight: bold; color: white;")
        title_layout.addWidget(title)
        title_layout.addStretch()
        self.layout.addLayout(title_layout)
        
        # רשימת קבצים
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.layout.addWidget(self.list_widget)
        
        # תווית ריקה
        self.empty_label = QLabel("אין קבצים אחרונים להצגה")
        self.empty_label.setObjectName("emptyLabel")
        self.empty_label.setAlignment(self._get_alignment_flag("AlignCenter"))
        self.empty_label.setVisible(False)
        self.layout.addWidget(self.empty_label)
        
        # רשימת קבצים
        self.files = []
        
        # בדיקה אם הרשימה ריקה
        self._update_empty_state()
    
    def _get_alignment_flag(self, flag_name):
        """מחזיר דגל יישור לפי שם, עם תמיכה בגרסאות שונות של PyQt6"""
        if flag_name == "AlignCenter":
            try:
                return Qt.AlignCenter
            except AttributeError:
                try:
                    return Qt.AlignmentFlag.AlignCenter
                except AttributeError:
                    return 0x0004 | 0x0080  # AlignCenter = AlignHCenter | AlignVCenter
        return 0
    
    def _on_item_clicked(self, item):
        """טיפול בלחיצה על פריט ברשימה"""
        file_info = item.data(Qt.ItemDataRole.UserRole)
        self.file_selected.emit(file_info)
    
    def _show_context_menu(self, position):
        """הצגת תפריט הקשר"""
        item = self.list_widget.itemAt(position)
        if not item:
            return
        
        file_info = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
        play_action = QAction("נגן", self)
        play_action.triggered.connect(lambda: self.file_play_requested.emit(file_info))
        menu.addAction(play_action)
        
        delete_action = QAction("מחק", self)
        delete_action.triggered.connect(lambda: self._delete_file(file_info))
        menu.addAction(delete_action)
        
        menu.exec(QCursor.pos())
    
    def _delete_file(self, file_info):
        """מחיקת קובץ מהרשימה"""
        # שליחת אות מחיקה
        self.file_delete_requested.emit(file_info)
        
        # מחיקה מהרשימה
        self.remove_file(file_info)
    
    def add_file(self, file_info):
        """הוספת קובץ לרשימה"""
        # בדיקה אם הקובץ כבר קיים
        for i, existing_file in enumerate(self.files):
            if existing_file.path == file_info.path:
                # עדכון קובץ קיים
                self.files[i] = file_info
                self._update_list()
                return
        
        # הוספת קובץ חדש
        self.files.insert(0, file_info)
        
        # שמירה על מספר מקסימלי של קבצים
        if len(self.files) > self.max_files:
            self.files.pop()
        
        # עדכון הרשימה
        self._update_list()
    
    def remove_file(self, file_info):
        """הסרת קובץ מהרשימה"""
        for i, existing_file in enumerate(self.files):
            if existing_file.path == file_info.path:
                self.files.pop(i)
                self._update_list()
                break
    
    def clear(self):
        """ניקוי הרשימה"""
        self.files = []
        self._update_list()
    
    def _update_list(self):
        """עדכון רשימת הקבצים בתצוגה"""
        self.list_widget.clear()
        
        for file_info in self.files:
            item = QListWidgetItem()
            item.setText(f"{file_info.name} ({file_info.size_formatted})")
            item.setToolTip(f"שם: {file_info.name}\n"
                           f"גודל: {file_info.size_formatted}\n"
                           f"פורמט: {file_info.format}\n"
                           f"תאריך העלאה: {file_info.upload_date_formatted}")
            item.setData(Qt.ItemDataRole.UserRole, file_info)
            
            # הוספת אייקון לפי סוג קובץ
            # בפרויקט אמיתי, כאן היינו מוסיפים אייקונים שונים לפי סוג הקובץ
            # item.setIcon(QIcon("path/to/icon.png"))
            
            self.list_widget.addItem(item)
        
        # עדכון מצב ריק
        self._update_empty_state()
    
    def _update_empty_state(self):
        """עדכון מצב ריק"""
        is_empty = len(self.files) == 0
        self.empty_label.setVisible(is_empty)
        self.list_widget.setVisible(not is_empty)
    
    def get_files(self):
        """החזרת רשימת הקבצים"""
        return self.files.copy()
        
    def load_recent_files(self, files=None):
        """
        טעינת קבצים אחרונים
        
        Args:
            files (List[FileInfo], optional): רשימת קבצים לטעינה. אם לא מסופק, הרשימה תישאר ריקה.
        """
        if files:
            self.files = files.copy()
            self._update_list()
