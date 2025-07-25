import sys
import os
from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet

# 📁 הוספת תיקיית src לנתיב המודולים (PYTHONPATH)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(CURRENT_DIR, 'src')

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# 🖼️ ייבוא חלון ראשי אחרי שהנתיב הוגדר
from ui.main_window import MainWindow
from app_context import settings_service


def main():
    app = QApplication(sys.argv)

    # 🎨 Apply theme from settings (default to dark_blue.xml)
    theme = settings_service.get_setting("theme", "dark_blue.xml")
    apply_stylesheet(app, theme=theme)

    window = MainWindow()
    window.showMaximized()  # לפתוח בחלון מלא

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
