"""
Modern Notification Widget with beautiful animations and styling
"""

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                           QPushButton, QGraphicsOpacityEffect, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor
from typing import Optional, Callable
from enum import Enum


class NotificationType(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class NotificationWidget(QFrame):
    """Modern notification widget with animations and beautiful styling"""
    
    # Signals
    clicked = pyqtSignal()
    dismissed = pyqtSignal()
    action_clicked = pyqtSignal(str)  # action_id
    
    def __init__(self, message: str, notification_type: NotificationType = NotificationType.INFO, 
                 duration: int = 5000, parent=None):
        super().__init__(parent)
        
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        self.actions = {}
        self.is_persistent = duration == 0
        
        self._setup_ui()
        self._setup_animations()
        self._setup_timer()
        
        # Apply initial styling
        self._apply_styling()
    
    def _setup_ui(self):
        """Setup the notification UI"""
        self.setFixedHeight(80)
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(12)
        
        # Icon label
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_icon()
        main_layout.addWidget(self.icon_label)
        
        # Content layout
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        # Message label
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)
        self.message_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        content_layout.addWidget(self.message_label)
        
        # Actions layout
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setSpacing(8)
        content_layout.addLayout(self.actions_layout)
        
        main_layout.addLayout(content_layout, 1)
        
        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(20, 20)
        self.close_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.close_button.clicked.connect(self.dismiss)
        main_layout.addWidget(self.close_button)
        
        # Make clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _set_icon(self):
        """Set the appropriate icon based on notification type"""
        icons = {
            NotificationType.SUCCESS: "✓",
            NotificationType.ERROR: "✗", 
            NotificationType.WARNING: "⚠",
            NotificationType.INFO: "ℹ"
        }
        
        icon_text = icons.get(self.notification_type, "ℹ")
        self.icon_label.setText(icon_text)
        self.icon_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
    
    def _apply_styling(self):
        """Apply modern styling based on notification type"""
        # Import theme service to get current colors
        try:
            from services.theme_service import theme_service
            colors = theme_service.get_current_colors()
        except:
            # Fallback colors if theme service is not available
            colors = {
                "notificationSuccessColor": "#a6e3a1",
                "notificationErrorColor": "#f38ba8", 
                "notificationWarningColor": "#f9e2af",
                "notificationInfoColor": "#89dceb",
                "primaryColor": "#1e1e2e",
                "primaryTextColor": "#cdd6f4",
                "borderColor": "#45475a"
            }
        
        # Color mapping
        color_map = {
            NotificationType.SUCCESS: colors.get("notificationSuccessColor", "#a6e3a1"),
            NotificationType.ERROR: colors.get("notificationErrorColor", "#f38ba8"),
            NotificationType.WARNING: colors.get("notificationWarningColor", "#f9e2af"),
            NotificationType.INFO: colors.get("notificationInfoColor", "#89dceb")
        }
        
        bg_color = color_map.get(self.notification_type, colors.get("notificationInfoColor", "#89dceb"))
        text_color = colors.get("primaryColor", "#1e1e2e")
        border_color = colors.get("borderColor", "#45475a")
        
        self.setStyleSheet(f"""
            NotificationWidget {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 12px;
                border-left: 4px solid {bg_color};
            }}
            
            QLabel {{
                color: {text_color};
                background-color: transparent;
            }}
            
            QPushButton {{
                background-color: transparent;
                color: {text_color};
                border: none;
                border-radius: 10px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: rgba(0, 0, 0, 0.1);
            }}
            
            QPushButton:pressed {{
                background-color: rgba(0, 0, 0, 0.2);
            }}
        """)
        
        # Set icon color
        self.icon_label.setStyleSheet(f"color: {text_color}; font-weight: bold;")
    
    def _setup_animations(self):
        """Setup entrance and exit animations"""
        # Opacity effect for fade animations
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        # Fade in animation
        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Fade out animation
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out_animation.finished.connect(self._on_fade_out_finished)
    
    def _setup_timer(self):
        """Setup auto-dismiss timer"""
        if not self.is_persistent:
            self.dismiss_timer = QTimer()
            self.dismiss_timer.setSingleShot(True)
            self.dismiss_timer.timeout.connect(self.dismiss)
    
    def show_notification(self):
        """Show the notification with fade-in animation"""
        self.show()
        self.fade_in_animation.start()
        
        # Start dismiss timer if not persistent
        if not self.is_persistent:
            self.dismiss_timer.start(self.duration)
    
    def dismiss(self):
        """Dismiss the notification with fade-out animation"""
        if hasattr(self, 'dismiss_timer'):
            self.dismiss_timer.stop()
        
        self.fade_out_animation.start()
    
    def _on_fade_out_finished(self):
        """Handle fade-out animation completion"""
        self.dismissed.emit()
        self.hide()
        self.deleteLater()
    
    def add_action(self, action_id: str, text: str, callback: Optional[Callable] = None):
        """Add an action button to the notification"""
        action_button = QPushButton(text)
        action_button.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        action_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 4px;
                padding: 4px 12px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        
        def on_action_clicked():
            if callback:
                callback()
            self.action_clicked.emit(action_id)
            self.dismiss()
        
        action_button.clicked.connect(on_action_clicked)
        self.actions_layout.addWidget(action_button)
        self.actions[action_id] = action_button
    
    def set_persistent(self, persistent: bool):
        """Set whether the notification should auto-dismiss"""
        self.is_persistent = persistent
        if persistent and hasattr(self, 'dismiss_timer'):
            self.dismiss_timer.stop()
    
    def mousePressEvent(self, event):
        """Handle mouse click on notification"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        """Handle mouse enter - pause auto-dismiss"""
        if hasattr(self, 'dismiss_timer') and self.dismiss_timer.isActive():
            self.dismiss_timer.stop()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave - resume auto-dismiss"""
        if not self.is_persistent and hasattr(self, 'dismiss_timer'):
            self.dismiss_timer.start(2000)  # Give extra time after hover
        super().leaveEvent(event)


class NotificationManager(QWidget):
    """Manager for displaying multiple notifications"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notifications = []
        self.max_notifications = 5
        
        # Setup layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        self.layout.addStretch()  # Push notifications to bottom
        
        # Position in parent
        if parent:
            self.setParent(parent)
            self._position_manager()
    
    def _position_manager(self):
        """Position the notification manager in the parent widget"""
        if self.parent():
            parent_rect = self.parent().rect()
            self.setGeometry(
                parent_rect.width() - 520,  # 20px margin + 500px max width
                20,  # Top margin
                500,  # Width
                parent_rect.height() - 40  # Height with margins
            )
    
    def show_notification(self, message: str, notification_type: NotificationType = NotificationType.INFO,
                         duration: int = 5000) -> NotificationWidget:
        """Show a new notification"""
        # Remove oldest notification if at limit
        if len(self.notifications) >= self.max_notifications:
            oldest = self.notifications[0]
            oldest.dismiss()
        
        # Create new notification
        notification = NotificationWidget(message, notification_type, duration, self)
        notification.dismissed.connect(lambda: self._remove_notification(notification))
        
        # Add to layout and list
        self.layout.insertWidget(self.layout.count() - 1, notification)  # Before stretch
        self.notifications.append(notification)
        
        # Show with animation
        notification.show_notification()
        
        return notification
    
    def _remove_notification(self, notification: NotificationWidget):
        """Remove a notification from the manager"""
        if notification in self.notifications:
            self.notifications.remove(notification)
            self.layout.removeWidget(notification)
    
    def show_success(self, message: str, duration: int = 3000) -> NotificationWidget:
        """Show success notification"""
        return self.show_notification(message, NotificationType.SUCCESS, duration)
    
    def show_error(self, message: str, duration: int = 0) -> NotificationWidget:
        """Show error notification (persistent by default)"""
        return self.show_notification(message, NotificationType.ERROR, duration)
    
    def show_warning(self, message: str, duration: int = 5000) -> NotificationWidget:
        """Show warning notification"""
        return self.show_notification(message, NotificationType.WARNING, duration)
    
    def show_info(self, message: str, duration: int = 4000) -> NotificationWidget:
        """Show info notification"""
        return self.show_notification(message, NotificationType.INFO, duration)
    
    def clear_all(self):
        """Clear all notifications"""
        for notification in self.notifications.copy():
            notification.dismiss()
    
    def resizeEvent(self, event):
        """Handle parent resize"""
        self._position_manager()
        super().resizeEvent(event)