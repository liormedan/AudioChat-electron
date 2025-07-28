"""
Advanced Theme Service for Audio Chat Studio
Provides modern theme management with custom colors and styling
"""

import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any

import json


class ThemeService:
    
    def __init__(self):
        
        self.current_theme = "kiro_modern_dark"
        self.custom_themes_dir = os.path.join(os.path.dirname(__file__), "../../theme")
        self.current_colors = {}
    
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


