"""
Modern UI widgets with beautiful styling and animations
"""

from PyQt6.QtWidgets import (QPushButton, QFrame, QLabel, QWidget, QVBoxLayout, 
                           QHBoxLayout, QGraphicsDropShadowEffect, QLineEdit, QComboBox)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QFont, QPalette
from typing import Optional


class ModernButton(QPushButton):
    """Modern button with hover animations and beautiful styling"""
    
    def __init__(self, text: str = "", icon: str = "", parent=None):
        super().__init__(text, parent)
        self.icon_text = icon
        self.is_primary = False
        self.is_danger = False
        self.is_success = False
        
        self._setup_animations()
        self._apply_styling()
    
    def _setup_animations(self):
        """Setup hover animations"""
        self.hover_animation = QPropertyAnimation(self, b"geometry")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def _apply_styling(self):
        """Apply modern styling"""
        self.setMinimumHeight(44)
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def set_primary(self, primary: bool = True):
        """Set as primary button"""
        self.is_primary = primary
        self._update_style()
    
    def set_danger(self, danger: bool = True):
        """Set as danger button"""
        self.is_danger = danger
        self._update_style()
    
    def set_success(self, success: bool = True):
        """Set as success button"""
        self.is_success = success
        self._update_style()
    
    def _update_style(self):
        """Update button style based on type"""
        if self.is_primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #89b4fa, stop:1 #74c7ec);
                    color: #1e1e2e;
                    border: none;
                    border-radius: 12px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #b4befe, stop:1 #89b4fa);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #74c7ec, stop:1 #89dceb);
                }
            """)
        elif self.is_danger:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f38ba8, stop:1 #eba0ac);
                    color: #1e1e2e;
                    border: none;
                    border-radius: 12px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #eba0ac, stop:1 #f2cdcd);
                }
            """)
        elif self.is_success:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #a6e3a1, stop:1 #94e2d5);
                    color: #1e1e2e;
                    border: none;
                    border-radius: 12px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #94e2d5, stop:1 #89dceb);
                }
            """)
    
    def enterEvent(self, event):
        """Handle mouse enter with animation"""
        current_rect = self.geometry()
        new_rect = QRect(current_rect.x(), current_rect.y() - 2, 
                        current_rect.width(), current_rect.height())
        
        self.hover_animation.setStartValue(current_rect)
        self.hover_animation.setEndValue(new_rect)
        self.hover_animation.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave with animation"""
        current_rect = self.geometry()
        new_rect = QRect(current_rect.x(), current_rect.y() + 2, 
                        current_rect.width(), current_rect.height())
        
        self.hover_animation.setStartValue(current_rect)
        self.hover_animation.setEndValue(new_rect)
        self.hover_animation.start()
        
        super().leaveEvent(event)


class ModernCard(QFrame):
    """Modern card widget with shadow and rounded corners"""
    
    clicked = pyqtSignal()
    
    def __init__(self, title: str = "", subtitle: str = "", parent=None):
        super().__init__(parent)
        self.title_text = title
        self.subtitle_text = subtitle
        self.is_clickable = False
        
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self):
        """Setup card UI"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 16, 20, 16)
        self.layout.setSpacing(8)
        
        if self.title_text:
            self.title_label = QLabel(self.title_text)
            self.title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            self.layout.addWidget(self.title_label)
        
        if self.subtitle_text:
            self.subtitle_label = QLabel(self.subtitle_text)
            self.subtitle_label.setFont(QFont("Segoe UI", 11))
            self.layout.addWidget(self.subtitle_label)
    
    def _apply_styling(self):
        """Apply modern card styling"""
        self.setFrameStyle(QFrame.Shape.NoFrame)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 6)
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet("""
            ModernCard {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #313244, stop:1 #1e1e2e);
                border: 2px solid #45475a;
                border-radius: 16px;
            }
            ModernCard:hover {
                border-color: #89b4fa;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45475a, stop:1 #313244);
            }
        """)
    
    def set_clickable(self, clickable: bool = True):
        """Make card clickable"""
        self.is_clickable = clickable
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if self.is_clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class ModernInput(QLineEdit):
    """Modern input field with floating label effect"""
    
    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.placeholder_text = placeholder
        self.floating_label = QLabel(placeholder, self)
        self.is_focused = False
        
        self._setup_ui()
        self._setup_animations()
    
    def _setup_ui(self):
        """Setup input UI"""
        self.setMinimumHeight(52)
        self.setFont(QFont("Segoe UI", 11))
        
        # Setup floating label
        self.floating_label.setFont(QFont("Segoe UI", 9))
        self.floating_label.move(16, 16)
        self.floating_label.setStyleSheet("color: #6c7086; background: transparent;")
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
    
    def _setup_animations(self):
        """Setup label animations"""
        self.label_animation = QPropertyAnimation(self.floating_label, b"geometry")
        self.label_animation.setDuration(200)
        self.label_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def focusInEvent(self, event):
        """Handle focus in with label animation"""
        self.is_focused = True
        self._animate_label_up()
        super().focusInEvent(event)
    
    def focusOutEvent(self, event):
        """Handle focus out with label animation"""
        self.is_focused = False
        if not self.text():
            self._animate_label_down()
        super().focusOutEvent(event)
    
    def _animate_label_up(self):
        """Animate label to top position"""
        start_rect = self.floating_label.geometry()
        end_rect = QRect(16, 4, start_rect.width(), start_rect.height())
        
        self.label_animation.setStartValue(start_rect)
        self.label_animation.setEndValue(end_rect)
        self.label_animation.start()
        
        self.floating_label.setStyleSheet("color: #89b4fa; background: transparent; font-weight: 600;")
    
    def _animate_label_down(self):
        """Animate label to center position"""
        start_rect = self.floating_label.geometry()
        end_rect = QRect(16, 16, start_rect.width(), start_rect.height())
        
        self.label_animation.setStartValue(start_rect)
        self.label_animation.setEndValue(end_rect)
        self.label_animation.start()
        
        self.floating_label.setStyleSheet("color: #6c7086; background: transparent; font-weight: normal;")


class ModernComboBox(QComboBox):
    """Modern combo box with beautiful styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_styling()
    
    def _setup_styling(self):
        """Setup modern styling"""
        self.setMinimumHeight(48)
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


class ModernProgressBar(QWidget):
    """Modern progress bar with smooth animations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress_value = 0
        self.max_value = 100
        self.setMinimumHeight(8)
        self.setMaximumHeight(8)
        
        # Animation for progress changes
        self.progress_animation = QPropertyAnimation(self, b"progress_value")
        self.progress_animation.setDuration(300)
        self.progress_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.progress_animation.valueChanged.connect(self.update)
    
    def set_value(self, value: int):
        """Set progress value with animation"""
        self.progress_animation.setStartValue(self.progress_value)
        self.progress_animation.setEndValue(max(0, min(value, self.max_value)))
        self.progress_animation.start()
    
    def paintEvent(self, event):
        """Custom paint for modern progress bar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        bg_path = QPainterPath()
        bg_path.addRoundedRect(self.rect(), 4, 4)
        painter.fillPath(bg_path, QColor("#313244"))
        
        # Progress
        if self.progress_value > 0:
            progress_width = int((self.progress_value / self.max_value) * self.width())
            progress_rect = QRect(0, 0, progress_width, self.height())
            
            progress_path = QPainterPath()
            progress_path.addRoundedRect(progress_rect, 4, 4)
            
            # Gradient for progress
            from PyQt6.QtGui import QLinearGradient
            gradient = QLinearGradient(0, 0, progress_width, 0)
            gradient.setColorAt(0, QColor("#89b4fa"))
            gradient.setColorAt(1, QColor("#74c7ec"))
            
            painter.fillPath(progress_path, gradient)


class ModernToggle(QWidget):
    """Modern toggle switch"""
    
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_checked = False
        self.setFixedSize(60, 32)
        
        # Animation for toggle
        self.toggle_animation = QPropertyAnimation(self, b"geometry")
        self.toggle_animation.setDuration(200)
        self.toggle_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def toggle(self):
        """Toggle the switch"""
        self.is_checked = not self.is_checked
        self.toggled.emit(self.is_checked)
        self.update()
    
    def set_checked(self, checked: bool):
        """Set toggle state"""
        if self.is_checked != checked:
            self.is_checked = checked
            self.toggled.emit(self.is_checked)
            self.update()
    
    def paintEvent(self, event):
        """Custom paint for toggle switch"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        bg_color = QColor("#89b4fa") if self.is_checked else QColor("#45475a")
        bg_path = QPainterPath()
        bg_path.addRoundedRect(self.rect(), 16, 16)
        painter.fillPath(bg_path, bg_color)
        
        # Handle
        handle_x = 28 if self.is_checked else 4
        handle_rect = QRect(handle_x, 4, 24, 24)
        handle_path = QPainterPath()
        handle_path.addRoundedRect(handle_rect, 12, 12)
        painter.fillPath(handle_path, QColor("#ffffff"))
    
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle()
        super().mousePressEvent(event)