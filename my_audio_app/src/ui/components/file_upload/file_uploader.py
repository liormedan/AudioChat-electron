from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QProgressBar, 
                           QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QUrl, QTimer
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDragLeaveEvent

import os
import time
from .file_info import FileInfo


class FileUploader(QWidget):
    """רכיב להעלאת קבצי אודיו"""
    
    # אותות
    file_upload_started = pyqtSignal(str)  # אות שנשלח כאשר מתחילה העלאת קובץ
    file_upload_progress = pyqtSignal(str, int)  # אות שנשלח במהלך העלאת קובץ (נתיב, אחוז)
    file_upload_completed = pyqtSignal(FileInfo)  # אות שנשלח כאשר הסתיימה העלאת קובץ
    file_upload_failed = pyqtSignal(str, str)  # אות שנשלח כאשר נכשלה העלאת קובץ (נתיב, הודעת שגיאה)
    
    def __init__(self, parent=None):
        """
        יוצר רכיב העלאת קבצים חדש
        
        Args:
            parent (QWidget, optional): הווידג'ט ההורה
        """
        super().__init__(parent)
        self.setObjectName("fileUploader")
        self.setAcceptDrops(True)
        
        # הגדרת סוגי קבצים מותרים
        self.allowed_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']
        
        # עיצוב
        self.setStyleSheet("""
            QLabel#dropArea {
                border: 2px dashed #555;
                border-radius: 8px;
                padding: 30px;
                background-color: #1e1e1e;
                color: white;
            }
            QLabel#dropAreaActive {
                border: 2px dashed #2196F3;
                border-radius: 8px;
                padding: 30px;
                background-color: #263238;
                color: white;
            }
            QProgressBar {
                border: 1px solid #333;
                border-radius: 4px;
                background-color: #1e1e1e;
                color: white;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """)
        
        # לייאאוט ראשי
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)
        
        # אזור גרירה והשלכה
        self.drop_area = QLabel("גרור קבצי אודיו לכאן או לחץ לבחירה")
        self.drop_area.setObjectName("dropArea")
        self.drop_area.setAlignment(self._get_alignment_flag("AlignCenter"))
        self.drop_area.setMinimumHeight(120)
        self.drop_area.mousePressEvent = self._on_drop_area_clicked
        self.layout.addWidget(self.drop_area)
        
        # פרוגרס בר
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)
        
        # מצב נוכחי
        self.current_file = None
        self.is_uploading = False
    
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
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """טיפול באירוע גרירת קובץ מעל הרכיב"""
        if event.mimeData().hasUrls():
            # בדיקה אם יש לפחות קובץ אודיו אחד
            has_audio_file = False
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if self._is_audio_file(file_path):
                    has_audio_file = True
                    break
            
            if has_audio_file:
                event.acceptProposedAction()
                self.drop_area.setObjectName("dropAreaActive")
                self.drop_area.setStyleSheet(self.styleSheet())
                self.drop_area.setText("שחרר כדי להעלות")
    
    def dragLeaveEvent(self, event: QDragLeaveEvent):
        """טיפול באירוע יציאת גרירה מהרכיב"""
        self.drop_area.setObjectName("dropArea")
        self.drop_area.setStyleSheet(self.styleSheet())
        self.drop_area.setText("גרור קבצי אודיו לכאן או לחץ לבחירה")
    
    def dropEvent(self, event: QDropEvent):
        """טיפול באירוע השלכת קובץ על הרכיב"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
            # החזרת העיצוב הרגיל
            self.drop_area.setObjectName("dropArea")
            self.drop_area.setStyleSheet(self.styleSheet())
            self.drop_area.setText("גרור קבצי אודיו לכאן או לחץ לבחירה")
            
            # טיפול בקבצים
            urls = event.mimeData().urls()
            audio_files = []
            
            for url in urls:
                file_path = url.toLocalFile()
                if self._is_audio_file(file_path):
                    audio_files.append(file_path)
            
            if audio_files:
                self._upload_files(audio_files)
            else:
                QMessageBox.warning(self, "סוג קובץ לא נתמך", 
                                   "יש להעלות רק קבצי אודיו בפורמטים הבאים: " + 
                                   ", ".join(self.allowed_extensions))
    
    def _on_drop_area_clicked(self, event):
        """טיפול בלחיצה על אזור ההשלכה"""
        if self.is_uploading:
            return
        
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Audio Files (*" + " *".join(self.allowed_extensions) + ")")
        
        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            audio_files = []
            
            for file_path in files:
                if self._is_audio_file(file_path):
                    audio_files.append(file_path)
            
            if audio_files:
                self._upload_files(audio_files)
    
    def _is_audio_file(self, file_path):
        """בדיקה האם הקובץ הוא קובץ אודיו מותר"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.allowed_extensions
    
    def _upload_files(self, file_paths):
        """העלאת קבצים"""
        if self.is_uploading:
            return
        
        # התחלת העלאה
        self.is_uploading = True
        self.files_queue = file_paths.copy()
        self._upload_next_file()
    
    def _upload_next_file(self):
        """העלאת הקובץ הבא בתור"""
        if not self.files_queue:
            self.is_uploading = False
            self.progress_bar.setVisible(False)
            return
        
        # קבלת הקובץ הבא
        file_path = self.files_queue.pop(0)
        self.current_file = file_path
        
        # הצגת פרוגרס בר
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # שליחת אות התחלת העלאה
        self.file_upload_started.emit(file_path)
        
        # סימולציה של העלאה
        self._simulate_upload(file_path)
    
    def _simulate_upload(self, file_path):
        """סימולציה של העלאת קובץ"""
        # בפרויקט אמיתי, כאן היינו מעלים את הקובץ לשרת או מעבדים אותו
        # לצורך הדוגמה, נסמלץ העלאה עם טיימר
        
        self.upload_progress = 0
        
        def update_progress():
            self.upload_progress += 5
            self.progress_bar.setValue(self.upload_progress)
            self.file_upload_progress.emit(file_path, self.upload_progress)
            
            if self.upload_progress >= 100:
                # סיום העלאה
                try:
                    # יצירת אובייקט FileInfo
                    file_info = FileInfo.from_file_path(file_path)
                    
                    # שליחת אות סיום העלאה
                    self.file_upload_completed.emit(file_info)
                    
                    # המשך לקובץ הבא
                    QTimer.singleShot(500, self._upload_next_file)
                except Exception as e:
                    self.file_upload_failed.emit(file_path, str(e))
                    QTimer.singleShot(500, self._upload_next_file)
            else:
                # המשך העלאה
                QTimer.singleShot(100, update_progress)
        
        # התחלת העלאה
        QTimer.singleShot(100, update_progress)
    
    def cancel_upload(self):
        """ביטול העלאה נוכחית"""
        if self.is_uploading:
            self.is_uploading = False
            self.files_queue = []
            self.progress_bar.setVisible(False)
            self.file_upload_failed.emit(self.current_file, "העלאה בוטלה")
            self.current_file = None
