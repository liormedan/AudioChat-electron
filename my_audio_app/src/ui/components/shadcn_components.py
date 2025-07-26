"""
shadcn/ui inspired components for modern UI
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QFrame, QGraphicsDropShadowEffect, QLineEdit, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QBrush, QPen
from typing import Optional


class ShadcnCard(QFrame):
    """shadcn/ui Card component"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self._setup_styling()
    
    def _setup_styling(self):
        """Apply shadcn card styling"""
        self.setStyleSheet("""
            ShadcnCard {
                background-color: #27272a;
                border: 1px solid #27272a;
                border-radius: 8px;
                padding: 24px;
            }
            ShadcnCard:hover {
                border-color: #3f3f46;
            }
        """)
        
        # Add subtle shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 1)
        self.setGraphicsEffect(shadow)


class ShadcnButton(QPushButton):
    """shadcn/ui Button component"""
    
    def __init__(self, text: str = "", variant: str = "default", size: str = "default", parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self.size = size
        self._setup_styling()
    
    def _setup_styling(self):
        """Apply shadcn button styling"""
        base_style = """
            QPushButton {
                font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-weight: 500;
                border-radius: 6px;
                border: 1px solid transparent;
            }
            QPushButton:disabled {
                color: #52525b;
            }
        """
        
        # Size variants
        if self.size == "sm":
            size_style = "padding: 6px 12px; font-size: 12px; min-height: 32px;"
        elif self.size == "lg":
            size_style = "padding: 12px 24px; font-size: 16px; min-height: 44px;"
        else:  # default
            size_style = "padding: 8px 16px; font-size: 14px; min-height: 36px;"
        
        # Variant styles
        if self.variant == "default":
            variant_style = """
                background-color: #fafafa;
                color: #0a0a0b;
                border-color: #27272a;
            }
            QPushButton:hover {
                background-color: #f4f4f5;
            }
            QPushButton:pressed {
                background-color: #e4e4e7;
            """
        elif self.variant == "destructive":
            variant_style = """
                background-color: #ef4444;
                color: #fafafa;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:pressed {
                background-color: #b91c1c;
            """
        elif self.variant == "outline":
            variant_style = """
                background-color: transparent;
                color: #fafafa;
                border-color: #27272a;
            }
            QPushButton:hover {
                background-color: #27272a;
            }
            QPushButton:pressed {
                background-color: #3f3f46;
            """
        elif self.variant == "secondary":
            variant_style = """
                background-color: #27272a;
                color: #fafafa;
            }
            QPushButton:hover {
                background-color: #3f3f46;
            }
            QPushButton:pressed {
                background-color: #52525b;
            """
        elif self.variant == "ghost":
            variant_style = """
                background-color: transparent;
                color: #fafafa;
            }
            QPushButton:hover {
                background-color: #27272a;
            }
            QPushButton:pressed {
                background-color: #3f3f46;
            """
        else:  # primary
            variant_style = """
                background-color: #3b82f6;
                color: #fafafa;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            """
        
        self.setStyleSheet(base_style + "QPushButton {" + size_style + variant_style)


class ShadcnInput(QLineEdit):
    """shadcn/ui Input component"""
    
    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self._setup_styling()
    
    def _setup_styling(self):
        """Apply shadcn input styling"""
        self.setStyleSheet("""
            QLineEdit {
                background-color: #27272a;
                color: #fafafa;
                border: 1px solid #27272a;
                border-radius: 6px;
                padding: 8px 12px;
                font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 14px;
                min-height: 36px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                outline: 2px solid rgba(59, 130, 246, 0.2);
                outline-offset: 2px;
            }
            QLineEdit:hover {
                border-color: #3f3f46;
            }
            QLineEdit::placeholder {
                color: #71717a;
            }
        """)


class ShadcnTextarea(QTextEdit):
    """shadcn/ui Textarea component"""
    
    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self._setup_styling()
    
    def _setup_styling(self):
        """Apply shadcn textarea styling"""
        self.setStyleSheet("""
            QTextEdit {
                background-color: #27272a;
                color: #fafafa;
                border: 1px solid #27272a;
                border-radius: 6px;
                padding: 8px 12px;
                font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 14px;
                min-height: 80px;
            }
            QTextEdit:focus {
                border-color: #3b82f6;
                outline: 2px solid rgba(59, 130, 246, 0.2);
                outline-offset: 2px;
            }
            QTextEdit:hover {
                border-color: #3f3f46;
            }
        """)


class ShadcnBadge(QLabel):
    """shadcn/ui Badge component"""
    
    def __init__(self, text: str = "", variant: str = "default", parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self._setup_styling()
    
    def _setup_styling(self):
        """Apply shadcn badge styling"""
        base_style = """
            QLabel {
                font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 12px;
                font-weight: 500;
                padding: 4px 8px;
                border-radius: 4px;
                border: 1px solid transparent;
            }
        """
        
        if self.variant == "secondary":
            variant_style = """
                background-color: #27272a;
                color: #fafafa;
                border-color: #3f3f46;
            """
        elif self.variant == "destructive":
            variant_style = """
                background-color: #ef4444;
                color: #fafafa;
            """
        elif self.variant == "outline":
            variant_style = """
                background-color: transparent;
                color: #fafafa;
                border-color: #27272a;
            """
        else:  # default
            variant_style = """
                background-color: #fafafa;
                color: #0a0a0b;
            """
        
        self.setStyleSheet(base_style + "QLabel {" + variant_style + "}")


class ShadcnSeparator(QFrame):
    """shadcn/ui Separator component"""
    
    def __init__(self, orientation: str = "horizontal", parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self._setup_styling()
    
    def _setup_styling(self):
        """Apply shadcn separator styling"""
        if self.orientation == "vertical":
            self.setFrameShape(QFrame.Shape.VLine)
            self.setFixedWidth(1)
        else:
            self.setFrameShape(QFrame.Shape.HLine)
            self.setFixedHeight(1)
        
        self.setStyleSheet("""
            QFrame {
                background-color: #27272a;
                border: none;
            }
        """)


class ShadcnAlert(QFrame):
    """shadcn/ui Alert component"""
    
    def __init__(self, title: str = "", description: str = "", variant: str = "default", parent=None):
        super().__init__(parent)
        self.title_text = title
        self.description_text = description
        self.variant = variant
        self._setup_ui()
        self._setup_styling()
    
    def _setup_ui(self):
        """Setup alert UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        
        if self.title_text:
            title_label = QLabel(self.title_text)
            title_label.setFont(QFont("Inter", 14, QFont.Weight.DemiBold))
            layout.addWidget(title_label)
        
        if self.description_text:
            desc_label = QLabel(self.description_text)
            desc_label.setFont(QFont("Inter", 13))
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
    
    def _setup_styling(self):
        """Apply shadcn alert styling"""
        base_style = """
            ShadcnAlert {
                border-radius: 6px;
                border: 1px solid;
                font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
        """
        
        if self.variant == "destructive":
            variant_style = """
                background-color: rgba(239, 68, 68, 0.1);
                border-color: #ef4444;
                color: #fecaca;
            """
        else:  # default
            variant_style = """
                background-color: #27272a;
                border-color: #3f3f46;
                color: #fafafa;
            """
        
        self.setStyleSheet(base_style + "ShadcnAlert {" + variant_style + "}")


class ShadcnProgress(QWidget):
    """shadcn/ui Progress component"""
    
    def __init__(self, value: int = 0, maximum: int = 100, parent=None):
        super().__init__(parent)
        self.value = value
        self.maximum = maximum
        self.setFixedHeight(8)
        self.setMinimumWidth(200)
    
    def set_value(self, value: int):
        """Set progress value"""
        self.value = max(0, min(value, self.maximum))
        self.update()
    
    def paintEvent(self, event):
        """Custom paint for progress bar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        bg_path = QPainterPath()
        bg_path.addRoundedRect(self.rect(), 4, 4)
        painter.fillPath(bg_path, QColor("#27272a"))
        
        # Progress
        if self.value > 0:
            progress_width = int((self.value / self.maximum) * self.width())
            progress_rect = self.rect()
            progress_rect.setWidth(progress_width)
            
            progress_path = QPainterPath()
            progress_path.addRoundedRect(progress_rect, 4, 4)
            painter.fillPath(progress_path, QColor("#3b82f6"))


class ShadcnSwitch(QWidget):
    """shadcn/ui Switch component"""
    
    toggled = pyqtSignal(bool)
    
    def __init__(self, checked: bool = False, parent=None):
        super().__init__(parent)
        self.checked = checked
        self.setFixedSize(44, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def toggle(self):
        """Toggle switch state"""
        self.checked = not self.checked
        self.toggled.emit(self.checked)
        self.update()
    
    def set_checked(self, checked: bool):
        """Set switch state"""
        if self.checked != checked:
            self.checked = checked
            self.toggled.emit(self.checked)
            self.update()
    
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle()
        super().mousePressEvent(event)
    
    def paintEvent(self, event):
        """Custom paint for switch"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        bg_color = QColor("#3b82f6") if self.checked else QColor("#3f3f46")
        bg_path = QPainterPath()
        bg_path.addRoundedRect(self.rect(), 12, 12)
        painter.fillPath(bg_path, bg_color)
        
        # Thumb
        thumb_x = 20 if self.checked else 2
        thumb_rect = self.rect()
        thumb_rect.setX(thumb_x)
        thumb_rect.setY(2)
        thumb_rect.setWidth(20)
        thumb_rect.setHeight(20)
        
        thumb_path = QPainterPath()
        thumb_path.addRoundedRect(thumb_rect, 10, 10)
        painter.fillPath(thumb_path, QColor("#fafafa"))