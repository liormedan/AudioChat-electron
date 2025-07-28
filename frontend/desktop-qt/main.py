import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# 📁 הוספת תיקיית src לנתיב המודולים (PYTHONPATH)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(CURRENT_DIR, 'src')

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# 🖼️ ייבוא חלון ראשי אחרי שהנתיב הוגדר
from ui.main_window import MainWindow
from app_context import settings_service
from services.theme_service import theme_service


def main():
    app = QApplication(sys.argv)
    
    # 🎨 Set application properties for better appearance
    app.setApplicationName("Audio Chat Studio")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Kiro Audio")
    
    # 🔤 Set default font for better text rendering (shadcn style)
    font = QFont("Inter", 14)
    if not font.exactMatch():
        # Fallback fonts if Inter is not available
        font = QFont("SF Pro Display", 14)
        if not font.exactMatch():
            font = QFont("Segoe UI", 14)
    
    font.setWeight(QFont.Weight.Normal)
    font.setHintingPreference(QFont.HintingPreference.PreferDefaultHinting)
    app.setFont(font)
    
    # 🎨 Apply modern theme from settings (default to kiro_modern_dark)
    theme = settings_service.get_setting("theme", "kiro_modern_dark")
    theme_service.apply_theme(theme)
    
    # 🖼️ Create and show main window
    window = MainWindow()
    window.showMaximized()  # לפתוח בחלון מלא
    
    # 🔄 Connect theme service to settings updates
    def on_theme_changed(theme_name):
        settings_service.set_setting("theme", theme_name)
    
    theme_service.theme_changed.connect(on_theme_changed)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
