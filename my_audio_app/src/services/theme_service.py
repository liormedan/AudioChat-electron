"""
Advanced Theme Service for Audio Chat Studio
Provides modern theme management with custom colors and styling
"""

import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
from qt_material import apply_stylesheet, list_themes
import json


class ThemeService(QObject):
    """Advanced theme management service"""
    
    # Signals
    theme_changed = pyqtSignal(str)  # theme_name
    colors_updated = pyqtSignal(dict)  # color_dict
    
    def __init__(self):
        super().__init__()
        self.current_theme = "kiro_modern_dark"
        self.custom_themes_dir = os.path.join(os.path.dirname(__file__), "../../theme")
        self.current_colors = {}
        self._load_available_themes()
    
    def _load_available_themes(self):
        """Load all available themes"""
        self.available_themes = {
            # Built-in qt-material themes
            **{theme: {"type": "builtin", "path": None} for theme in list_themes()},
            
            # Custom themes
            "kiro_modern_dark": {"type": "custom", "path": "kiro_modern_dark.xml"},
            "kiro_modern_light": {"type": "custom", "path": "kiro_modern_light.xml"},
        }
    
    def get_available_themes(self) -> List[str]:
        """Get list of all available theme names"""
        return list(self.available_themes.keys())
    
    def get_theme_info(self, theme_name: str) -> Dict[str, Any]:
        """Get information about a specific theme"""
        return self.available_themes.get(theme_name, {})
    
    def load_custom_theme_colors(self, theme_file: str) -> Dict[str, str]:
        """Load colors from custom theme XML file"""
        theme_path = os.path.join(self.custom_themes_dir, theme_file)
        colors = {}
        
        try:
            if os.path.exists(theme_path):
                tree = ET.parse(theme_path)
                root = tree.getroot()
                
                for color_elem in root.findall(".//color"):
                    name = color_elem.get("name")
                    value = color_elem.text
                    if name and value:
                        colors[name] = value
        except Exception as e:
            print(f"Error loading custom theme {theme_file}: {e}")
        
        return colors
    
    def apply_theme(self, theme_name: str) -> bool:
        """Apply a theme to the application"""
        try:
            app = QApplication.instance()
            if not app:
                return False
            
            theme_info = self.available_themes.get(theme_name)
            if not theme_info:
                return False
            
            if theme_info["type"] == "builtin":
                # Apply built-in qt-material theme
                apply_stylesheet(app, theme=theme_name)
                self.current_colors = self._extract_builtin_colors(theme_name)
            
            elif theme_info["type"] == "custom":
                # Apply custom theme
                self.current_colors = self.load_custom_theme_colors(theme_info["path"])
                self._apply_custom_theme(app, self.current_colors)
            
            self.current_theme = theme_name
            self.theme_changed.emit(theme_name)
            self.colors_updated.emit(self.current_colors)
            return True
            
        except Exception as e:
            print(f"Error applying theme {theme_name}: {e}")
            return False
    
    def _extract_builtin_colors(self, theme_name: str) -> Dict[str, str]:
        """Extract colors from built-in theme"""
        # This is a simplified extraction - in a real implementation,
        # you'd parse the qt-material theme files
        if "dark" in theme_name.lower():
            return {
                "primaryColor": "#1e1e2e",
                "secondaryColor": "#313244",
                "accentColor": "#89b4fa",
                "primaryTextColor": "#cdd6f4",
                "successColor": "#a6e3a1",
                "warningColor": "#f9e2af",
                "errorColor": "#f38ba8",
            }
        else:
            return {
                "primaryColor": "#ffffff",
                "secondaryColor": "#f1f3f4",
                "accentColor": "#1a73e8",
                "primaryTextColor": "#202124",
                "successColor": "#137333",
                "warningColor": "#f9ab00",
                "errorColor": "#d93025",
            }
    
    def _apply_custom_theme(self, app: QApplication, colors: Dict[str, str]):
        """Apply custom theme colors to the application"""
        # Create custom stylesheet based on colors
        stylesheet = self._generate_custom_stylesheet(colors)
        app.setStyleSheet(stylesheet)
    
    def _generate_custom_stylesheet(self, colors: Dict[str, str]) -> str:
        """Generate comprehensive stylesheet from color palette"""
        return f"""
        /* Main Application Styling */
        QMainWindow {{
            background-color: {colors.get('primaryColor', '#0a0a0b')};
            color: {colors.get('primaryTextColor', '#fafafa')};
            font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 14px;
            font-weight: 400;
            line-height: 1.5;
        }}
        
        /* Sidebar Styling */
        QWidget#sidebar {{
            background-color: {colors.get('sidebarColor', '#09090b')};
            border-right: 1px solid {colors.get('borderColor', '#27272a')};
            font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        
        /* Button Styling */
        QPushButton {{
            background-color: {colors.get('buttonColor', '#27272a')};
            color: {colors.get('primaryTextColor', '#fafafa')};
            border: 1px solid {colors.get('borderColor', '#27272a')};
            border-radius: 6px;
            padding: 8px 16px;
            font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-weight: 500;
            font-size: 14px;
            min-height: 36px;
        }}
        
        QPushButton:hover {{
            background-color: {colors.get('buttonHoverColor', '#3f3f46')};
            border-color: {colors.get('borderColor', '#3f3f46')};
        }}
        
        QPushButton:pressed {{
            background-color: {colors.get('buttonPressedColor', '#52525b')};
        }}
        
        QPushButton:disabled {{
            background-color: {colors.get('buttonDisabledColor', '#09090b')};
            color: {colors.get('disabledTextColor', '#52525b')};
            border-color: {colors.get('borderColor', '#27272a')};
        }}
        
        /* Primary Button */
        QPushButton[class="primary"] {{
            background-color: {colors.get('accentColor', '#3b82f6')};
            color: {colors.get('primaryColor', '#0a0a0b')};
            border-color: {colors.get('accentColor', '#3b82f6')};
            font-weight: 600;
        }}
        
        QPushButton[class="primary"]:hover {{
            background-color: {colors.get('accentDarkColor', '#2563eb')};
            border-color: {colors.get('accentDarkColor', '#2563eb')};
        }}
        
        /* Destructive Button */
        QPushButton[class="destructive"] {{
            background-color: {colors.get('errorColor', '#ef4444')};
            color: {colors.get('primaryColor', '#0a0a0b')};
            border-color: {colors.get('errorColor', '#ef4444')};
            font-weight: 600;
        }}
        
        QPushButton[class="destructive"]:hover {{
            background-color: #dc2626;
            border-color: #dc2626;
        }}
        
        /* Sidebar Button Styling */
        QPushButton#sidebarButton {{
            text-align: left;
            padding: 12px 16px;
            border: none;
            border-radius: 6px;
            background-color: transparent;
            color: {colors.get('secondaryTextColor', '#a1a1aa')};
            font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-weight: 500;
            font-size: 14px;
            margin: 1px 8px;
        }}
        
        QPushButton#sidebarButton:checked {{
            background-color: {colors.get('sidebarSelectedColor', '#1e40af')};
            color: {colors.get('primaryTextColor', '#fafafa')};
            font-weight: 600;
        }}
        
        QPushButton#sidebarButton:hover:!checked {{
            background-color: {colors.get('sidebarHoverColor', '#1e293b')};
            color: {colors.get('primaryTextColor', '#fafafa')};
        }}
        
        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {colors.get('inputColor', '#27272a')};
            color: {colors.get('primaryTextColor', '#fafafa')};
            border: 1px solid {colors.get('inputBorderColor', '#27272a')};
            border-radius: 6px;
            padding: 8px 12px;
            selection-background-color: {colors.get('selectionColor', '#27272a')};
            font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 14px;
            font-weight: 400;
            min-height: 36px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {colors.get('inputFocusColor', '#3b82f6')};
            outline: 2px solid rgba(59, 130, 246, 0.2);
            outline-offset: 2px;
        }}
        
        QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
            border-color: {colors.get('accentLightColor', '#60a5fa')};
        }}
        
        QLineEdit::placeholder, QTextEdit::placeholder, QPlainTextEdit::placeholder {{
            color: {colors.get('disabledTextColor', '#52525b')};
        }}
        
        /* ComboBox */
        QComboBox {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors.get('inputColor', '#313244')},
                stop:1 {colors.get('secondaryColor', '#313244')});
            color: {colors.get('primaryTextColor', '#cdd6f4')};
            border: 2px solid {colors.get('inputBorderColor', '#45475a')};
            border-radius: 12px;
            padding: 12px 16px;
            min-width: 120px;
            font-size: 13px;
            font-weight: 500;
        }}
        
        QComboBox:hover {{
            border-color: {colors.get('accentColor', '#89b4fa')};
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors.get('secondaryColor', '#313244')},
                stop:1 {colors.get('inputColor', '#313244')});
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 30px;
            border-top-right-radius: 12px;
            border-bottom-right-radius: 12px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 6px solid {colors.get('primaryTextColor', '#cdd6f4')};
            margin-right: 8px;
        }}
        
        QComboBox QAbstractItemView {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors.get('menuColor', '#1e1e2e')},
                stop:1 {colors.get('secondaryColor', '#313244')});
            color: {colors.get('menuTextColor', '#cdd6f4')};
            border: 2px solid {colors.get('borderColor', '#45475a')};
            border-radius: 12px;
            selection-background-color: {colors.get('menuSelectedColor', '#45475a')};
            padding: 4px;
        }}
        
        QComboBox QAbstractItemView::item {{
            padding: 8px 12px;
            border-radius: 8px;
            margin: 2px;
        }}
        
        QComboBox QAbstractItemView::item:selected {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {colors.get('accentColor', '#89b4fa')},
                stop:1 {colors.get('accentLightColor', '#b4befe')});
            color: {colors.get('primaryColor', '#1e1e2e')};
        }}
        
        /* Tabs */
        QTabWidget::pane {{
            border: 2px solid {colors.get('borderColor', '#45475a')};
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors.get('secondaryColor', '#313244')},
                stop:1 {colors.get('primaryColor', '#1e1e2e')});
            border-radius: 16px;
            margin-top: 10px;
        }}
        
        QTabBar::tab {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors.get('tabColor', '#1e1e2e')},
                stop:1 {colors.get('secondaryColor', '#313244')});
            color: {colors.get('tabTextColor', '#bac2de')};
            padding: 14px 24px;
            margin-right: 4px;
            border-top-left-radius: 16px;
            border-top-right-radius: 16px;
            min-width: 120px;
            font-weight: 600;
            font-size: 13px;
        }}
        
        QTabBar::tab:selected {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {colors.get('accentColor', '#89b4fa')},
                stop:1 {colors.get('accentLightColor', '#b4befe')});
            color: {colors.get('primaryColor', '#1e1e2e')};
            border-bottom: 4px solid {colors.get('accentDarkColor', '#74c7ec')};
            font-weight: 700;
        }}
        
        QTabBar::tab:hover:!selected {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {colors.get('tabHoverColor', '#2a2a3e')},
                stop:1 {colors.get('tabColor', '#1e1e2e')});
            border-bottom: 2px solid {colors.get('accentColor', '#89b4fa')};
        }}
        
        /* Lists and Tables */
        QListWidget, QTableWidget {{
            background-color: {colors.get('secondaryColor', '#27272a')};
            color: {colors.get('primaryTextColor', '#fafafa')};
            border: 1px solid {colors.get('borderColor', '#27272a')};
            border-radius: 8px;
            alternate-background-color: {colors.get('primaryColor', '#0a0a0b')};
            font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-size: 14px;
        }}
        
        QListWidget::item, QTableWidget::item {{
            padding: 12px 16px;
            border-radius: 6px;
            margin: 1px;
            font-weight: 400;
            border-bottom: 1px solid {colors.get('borderColor', '#27272a')};
        }}
        
        QListWidget::item:selected, QTableWidget::item:selected {{
            background-color: {colors.get('accentColor', '#3b82f6')};
            color: {colors.get('primaryColor', '#0a0a0b')};
            font-weight: 500;
        }}
        
        QListWidget::item:hover, QTableWidget::item:hover {{
            background-color: {colors.get('highlightColor', '#3f3f46')};
        }}
        
        QHeaderView::section {{
            background-color: {colors.get('headerColor', '#1e1e2e')};
            color: {colors.get('primaryTextColor', '#cdd6f4')};
            border: 1px solid {colors.get('borderColor', '#45475a')};
            padding: 8px;
            font-weight: 600;
        }}
        
        /* Scrollbars */
        QScrollBar:vertical {{
            background-color: {colors.get('primaryColor', '#1e1e2e')};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors.get('scrollbarColor', '#45475a')};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors.get('scrollbarHoverColor', '#585b70')};
        }}
        
        QScrollBar:horizontal {{
            background-color: {colors.get('primaryColor', '#1e1e2e')};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {colors.get('scrollbarColor', '#45475a')};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {colors.get('scrollbarHoverColor', '#585b70')};
        }}
        
        /* Progress Bars */
        QProgressBar {{
            background-color: {colors.get('progressBackgroundColor', '#313244')};
            border: 1px solid {colors.get('borderColor', '#45475a')};
            border-radius: 6px;
            text-align: center;
            color: {colors.get('primaryTextColor', '#cdd6f4')};
            font-weight: 500;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors.get('progressColor', '#89b4fa')};
            border-radius: 5px;
        }}
        
        /* Menus */
        QMenu {{
            background-color: {colors.get('menuColor', '#1e1e2e')};
            color: {colors.get('menuTextColor', '#cdd6f4')};
            border: 1px solid {colors.get('borderColor', '#45475a')};
            border-radius: 6px;
            padding: 4px;
        }}
        
        QMenu::item {{
            padding: 8px 16px;
            border-radius: 4px;
            margin: 1px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors.get('menuSelectedColor', '#45475a')};
            color: {colors.get('menuSelectedTextColor', '#89b4fa')};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {colors.get('borderColor', '#45475a')};
            margin: 4px 8px;
        }}
        
        /* Tooltips */
        QToolTip {{
            background-color: {colors.get('tooltipColor', '#313244')};
            color: {colors.get('tooltipTextColor', '#cdd6f4')};
            border: 1px solid {colors.get('borderColor', '#45475a')};
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
        }}
        
        /* Group Boxes */
        QGroupBox {{
            color: {colors.get('primaryTextColor', '#fafafa')};
            background-color: {colors.get('secondaryColor', '#27272a')};
            border: 1px solid {colors.get('borderColor', '#27272a')};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            font-family: "Inter", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            font-weight: 600;
            font-size: 14px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 2px 8px;
            background-color: {colors.get('primaryColor', '#0a0a0b')};
            color: {colors.get('accentColor', '#3b82f6')};
            border-radius: 4px;
            font-weight: 600;
        }}
        
        /* Sliders */
        QSlider::groove:horizontal {{
            background-color: {colors.get('progressBackgroundColor', '#313244')};
            height: 6px;
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {colors.get('accentColor', '#89b4fa')};
            width: 18px;
            height: 18px;
            border-radius: 9px;
            margin: -6px 0;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: {colors.get('accentLightColor', '#b4befe')};
        }}
        
        /* Checkboxes and Radio Buttons */
        QCheckBox, QRadioButton {{
            color: {colors.get('primaryTextColor', '#cdd6f4')};
            spacing: 8px;
        }}
        
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border: 2px solid {colors.get('borderColor', '#45475a')};
            border-radius: 3px;
            background-color: {colors.get('inputColor', '#313244')};
        }}
        
        QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
            background-color: {colors.get('accentColor', '#89b4fa')};
            border-color: {colors.get('accentColor', '#89b4fa')};
        }}
        
        /* Status Bar */
        QStatusBar {{
            background-color: {colors.get('statusbarColor', '#181825')};
            color: {colors.get('secondaryTextColor', '#bac2de')};
            border-top: 1px solid {colors.get('borderColor', '#45475a')};
        }}
        
        /* Splitter */
        QSplitter::handle {{
            background-color: {colors.get('borderColor', '#45475a')};
        }}
        
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        
        /* Custom Chat Styling */
        QWidget#chatPanel, QWidget#filePanel {{
            background-color: {colors.get('chatBackgroundColor', '#1e1e2e')};
            border-radius: 8px;
        }}
        
        /* Custom Notification Styling */
        QWidget#notificationSuccess {{
            background-color: {colors.get('notificationSuccessColor', '#a6e3a1')};
            color: {colors.get('primaryColor', '#1e1e2e')};
        }}
        
        QWidget#notificationWarning {{
            background-color: {colors.get('notificationWarningColor', '#f9e2af')};
            color: {colors.get('primaryColor', '#1e1e2e')};
        }}
        
        QWidget#notificationError {{
            background-color: {colors.get('notificationErrorColor', '#f38ba8')};
            color: {colors.get('primaryColor', '#1e1e2e')};
        }}
        
        QWidget#notificationInfo {{
            background-color: {colors.get('notificationInfoColor', '#89dceb')};
            color: {colors.get('primaryColor', '#1e1e2e')};
        }}
        """
    
    def get_current_theme(self) -> str:
        """Get the currently active theme name"""
        return self.current_theme
    
    def get_current_colors(self) -> Dict[str, str]:
        """Get the current color palette"""
        return self.current_colors.copy()
    
    def get_color(self, color_name: str, default: str = "#000000") -> str:
        """Get a specific color from the current theme"""
        return self.current_colors.get(color_name, default)
    
    def create_custom_theme(self, name: str, colors: Dict[str, str]) -> bool:
        """Create a new custom theme"""
        try:
            theme_path = os.path.join(self.custom_themes_dir, f"{name}.xml")
            
            # Create XML structure
            root = ET.Element("resources")
            for color_name, color_value in colors.items():
                color_elem = ET.SubElement(root, "color")
                color_elem.set("name", color_name)
                color_elem.text = color_value
            
            # Write to file
            tree = ET.ElementTree(root)
            tree.write(theme_path, encoding="utf-8", xml_declaration=True)
            
            # Add to available themes
            self.available_themes[name] = {"type": "custom", "path": f"{name}.xml"}
            
            return True
            
        except Exception as e:
            print(f"Error creating custom theme {name}: {e}")
            return False
    
    def export_theme(self, theme_name: str, file_path: str) -> bool:
        """Export theme to file"""
        try:
            theme_data = {
                "name": theme_name,
                "type": self.available_themes.get(theme_name, {}).get("type", "unknown"),
                "colors": self.current_colors if theme_name == self.current_theme else {}
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error exporting theme {theme_name}: {e}")
            return False
    
    def import_theme(self, file_path: str) -> Optional[str]:
        """Import theme from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            theme_name = theme_data.get("name", "imported_theme")
            colors = theme_data.get("colors", {})
            
            if self.create_custom_theme(theme_name, colors):
                return theme_name
            
        except Exception as e:
            print(f"Error importing theme from {file_path}: {e}")
        
        return None


# Global theme service instance
theme_service = ThemeService()