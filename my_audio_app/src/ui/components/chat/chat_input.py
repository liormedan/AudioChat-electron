from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QSize
from PyQt6.QtGui import QIcon, QKeyEvent, QTextCursor


class ChatInput(QWidget):
    """רכיב קלט להזנת הודעות צ'אט"""
    
    # אותות
    message_sent = pyqtSignal(str)  # אות שנשלח כאשר שולחים הודעה
    typing_started = pyqtSignal()   # אות שנשלח כאשר המשתמש מתחיל להקליד
    typing_stopped = pyqtSignal()   # אות שנשלח כאשר המשתמש מפסיק להקליד
    
    def __init__(self, parent=None, placeholder="הקלד הודעה..."):
        """
        יוצר רכיב קלט צ'אט חדש
        
        Args:
            parent (QWidget, optional): הווידג'ט ההורה
            placeholder (str, optional): טקסט פלייסהולדר לתיבת הקלט
        """
        super().__init__(parent)
        self.setObjectName("chatInput")
        self.placeholder = placeholder
        self.is_typing = False
        
        # עיצוב
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton {
                background-color: #333;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444;
            }
            QPushButton:pressed {
                background-color: #555;
            }
            QPushButton:disabled {
                background-color: #222;
                color: #666;
                border: 1px solid #333;
            }
            QLabel {
                color: #888;
                font-size: 11px;
                margin-top: 2px;
            }
        """)
        
        # לייאאוט ראשי
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        
        # לייאאוט לתיבת הקלט וכפתור השליחה
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(10)
        
        # תיבת קלט
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(self.placeholder)
        self.text_edit.setMaximumHeight(80)
        self.text_edit.textChanged.connect(self._on_text_changed)
        self.text_edit.installEventFilter(self)  # התקנת מסנן אירועים לתפיסת מקש Enter
        input_layout.addWidget(self.text_edit)
        
        # כפתור שליחה
        self.send_button = QPushButton("שלח")
        self.send_button.setMinimumWidth(80)
        self.send_button.setEnabled(False)  # מבוטל בהתחלה כי אין טקסט
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        self.layout.addLayout(input_layout)
        
        # תווית עזרה
        self.help_label = QLabel("לחץ Enter לשליחה, Shift+Enter לשורה חדשה")
        self.help_label.setAlignment(self._get_alignment_flag("AlignRight"))
        self.layout.addWidget(self.help_label)
    
    def _get_alignment_flag(self, flag_name):
        """מחזיר דגל יישור לפי שם, עם תמיכה בגרסאות שונות של PyQt6"""
        if flag_name == "AlignRight":
            try:
                return Qt.AlignRight
            except AttributeError:
                try:
                    return Qt.AlignmentFlag.AlignRight
                except AttributeError:
                    return 0x0002  # AlignRight = 0x0002
        elif flag_name == "AlignCenter":
            try:
                return Qt.AlignCenter
            except AttributeError:
                try:
                    return Qt.AlignmentFlag.AlignCenter
                except AttributeError:
                    return 0x0004 | 0x0080  # AlignCenter = AlignHCenter | AlignVCenter
        return 0
    
    def _get_key_event_type(self):
        """מחזיר סוג אירוע מקש, עם תמיכה בגרסאות שונות של PyQt6"""
        try:
            return QEvent.KeyPress
        except AttributeError:
            try:
                return QEvent.Type.KeyPress
            except AttributeError:
                return 6  # KeyPress = 6
    
    def _get_key_return(self):
        """מחזיר קוד מקש Enter, עם תמיכה בגרסאות שונות של PyQt6"""
        try:
            return Qt.Key_Return
        except AttributeError:
            try:
                return Qt.Key.Key_Return
            except AttributeError:
                return 0x01000004  # Key_Return = 0x01000004
    
    def _get_shift_modifier(self):
        """מחזיר מודיפייר Shift, עם תמיכה בגרסאות שונות של PyQt6"""
        try:
            return Qt.ShiftModifier
        except AttributeError:
            try:
                return Qt.KeyboardModifier.ShiftModifier
            except AttributeError:
                return 0x02000000  # ShiftModifier = 0x02000000
    
    def eventFilter(self, obj, event):
        """סינון אירועים לתפיסת מקש Enter"""
        if obj is self.text_edit and event.type() == self._get_key_event_type():
            key_return = self._get_key_return()
            shift_modifier = self._get_shift_modifier()
            
            if event.key() == key_return and not event.modifiers() & shift_modifier:
                self.send_message()
                return True
        return super().eventFilter(obj, event)
    
    def _on_text_changed(self):
        """מופעל כאשר הטקסט בתיבת הקלט משתנה"""
        has_text = len(self.text_edit.toPlainText().strip()) > 0
        self.send_button.setEnabled(has_text)
        
        # שליחת אותות הקלדה
        if has_text and not self.is_typing:
            self.is_typing = True
            self.typing_started.emit()
        elif not has_text and self.is_typing:
            self.is_typing = False
            self.typing_stopped.emit()
    
    def send_message(self):
        """שליחת הודעה"""
        text = self.text_edit.toPlainText().strip()
        if text:
            self.message_sent.emit(text)
            self.text_edit.clear()
            self.is_typing = False
            self.typing_stopped.emit()
    
    def set_focus(self):
        """מיקוד בתיבת הקלט"""
        self.text_edit.setFocus()
    
    def set_placeholder(self, text):
        """הגדרת טקסט פלייסהולדר"""
        self.placeholder = text
        self.text_edit.setPlaceholderText(text)
    
    def set_text(self, text):
        """הגדרת טקסט בתיבת הקלט"""
        self.text_edit.setText(text)
        self.text_edit.moveCursor(QTextCursor.End)  # העברת הסמן לסוף הטקסט
    
    def clear(self):
        """ניקוי תיבת הקלט"""
        self.text_edit.clear()
        self.is_typing = False
        self.typing_stopped.emit()
    
    def is_empty(self):
        """בדיקה האם תיבת הקלט ריקה"""
        return len(self.text_edit.toPlainText().strip()) == 0