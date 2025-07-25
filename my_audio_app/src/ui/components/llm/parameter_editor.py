"""
רכיב עורך פרמטרי LLM
מאפשר למשתמש לערוך פרמטרים של מודלי שפה גדולים עם תצוגה מקדימה ופרסטים
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QSlider, QSpinBox, QDoubleSpinBox, QPushButton, QGroupBox,
    QTextEdit, QComboBox, QCheckBox, QLineEdit, QMessageBox,
    QInputDialog, QListWidget, QListWidgetItem, QFrame,
    QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette
from typing import Dict, Any, Optional, List
import json
import os
from dataclasses import asdict

from models.llm_models import LLMParameters


class ParameterSlider(QWidget):
    """סליידר פרמטר מותאם אישית עם תווית ערך"""
    
    valueChanged = pyqtSignal(float)
    
    def __init__(self, name: str, min_val: float, max_val: float, 
                 default_val: float, step: float = 0.1, decimals: int = 1):
        super().__init__()
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.decimals = decimals
        
        # חישוב טווח הסליידר (מכפלה של 10^decimals)
        self.multiplier = 10 ** decimals
        self.slider_min = int(min_val * self.multiplier)
        self.slider_max = int(max_val * self.multiplier)
        
        self._setup_ui()
        self.set_value(default_val)
    
    def _setup_ui(self):
        """הגדרת ממשק המשתמש"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # סליידר
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(self.slider_min, self.slider_max)
        self.slider.valueChanged.connect(self._on_slider_changed)
        
        # תווית ערך
        self.value_label = QLabel()
        self.value_label.setMinimumWidth(60)
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 2px 8px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.slider, 1)
        layout.addWidget(self.value_label)
    
    def _on_slider_changed(self, value: int):
        """טיפול בשינוי ערך הסליידר"""
        real_value = value / self.multiplier
        self.value_label.setText(f"{real_value:.{self.decimals}f}")
        self.valueChanged.emit(real_value)
    
    def set_value(self, value: float):
        """הגדרת ערך"""
        slider_value = int(value * self.multiplier)
        self.slider.setValue(slider_value)
    
    def get_value(self) -> float:
        """קבלת ערך נוכחי"""
        return self.slider.value() / self.multiplier


class PresetCard(QFrame):
    """כרטיס פרסט פרמטרים"""
    
    selected = pyqtSignal(str)
    deleted = pyqtSignal(str)
    
    def __init__(self, name: str, parameters: LLMParameters, is_builtin: bool = False):
        super().__init__()
        self.name = name
        self.parameters = parameters
        self.is_builtin = is_builtin
        
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setFixedSize(200, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        """הגדרת ממשק המשתמש"""
        layout = QVBoxLayout(self)
        
        # שם הפרסט
        name_label = QLabel(self.name.title())
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(name_label)
        
        # פרמטרים עיקריים
        params_text = f"""Temperature: {self.parameters.temperature}
Max Tokens: {self.parameters.max_tokens}
Top P: {self.parameters.top_p}"""
        
        params_label = QLabel(params_text)
        params_label.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(params_label)
        
        layout.addStretch()
        
        # כפתורי פעולה (רק למותאמים אישית)
        if not self.is_builtin:
            actions_layout = QHBoxLayout()
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(24, 24)
            delete_btn.setToolTip("מחק פרסט")
            delete_btn.clicked.connect(lambda: self.deleted.emit(self.name))
            
            actions_layout.addStretch()
            actions_layout.addWidget(delete_btn)
            
            layout.addLayout(actions_layout)
    
    def _apply_style(self):
        """החלת עיצוב"""
        if self.is_builtin:
            self.setStyleSheet("""
                PresetCard {
                    background-color: #1e1e1e;
                    border: 2px solid #333;
                    border-radius: 8px;
                    padding: 8px;
                }
                PresetCard:hover {
                    border-color: #555;
                    background-color: #252525;
                }
            """)
        else:
            self.setStyleSheet("""
                PresetCard {
                    background-color: #1a2332;
                    border: 2px solid #2d4a6b;
                    border-radius: 8px;
                    padding: 8px;
                }
                PresetCard:hover {
                    border-color: #4a7ba7;
                    background-color: #1f2937;
                }
            """)
    
    def mousePressEvent(self, event):
        """טיפול בלחיצה על הכרטיס"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected.emit(self.name)
        super().mousePressEvent(event)


class ParameterEditor(QWidget):
    """עורך פרמטרי מודל LLM"""
    
    parameters_changed = pyqtSignal(dict)
    preset_loaded = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # פרמטרים נוכחיים
        self.current_parameters = LLMParameters()
        
        # פרסטים מותאמים אישית
        self.custom_presets: Dict[str, LLMParameters] = {}
        
        # טיימר לעדכון תצוגה מקדימה
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self._update_preview)
        
        self._setup_ui()
        self._load_custom_presets()
        self._update_all_displays()
    
    def _setup_ui(self):
        """הגדרת ממשק המשתמש"""
        # לייאאוט ראשי עם גלילה
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        main_widget = QWidget()
        scroll_area.setWidget(main_widget)
        
        layout = QVBoxLayout(self)
        layout.addWidget(scroll_area)
        
        content_layout = QVBoxLayout(main_widget)
        
        # כותרת
        title = QLabel("Model Parameters")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        content_layout.addWidget(title)
        
        # קבוצת פרמטרים עיקריים
        main_params_group = self._create_main_parameters_group()
        content_layout.addWidget(main_params_group)
        
        # קבוצת פרמטרים מתקדמים
        advanced_params_group = self._create_advanced_parameters_group()
        content_layout.addWidget(advanced_params_group)
        
        # קבוצת פרסטים
        presets_group = self._create_presets_group()
        content_layout.addWidget(presets_group)
        
        # קבוצת תצוגה מקדימה
        preview_group = self._create_preview_group()
        content_layout.addWidget(preview_group)
        
        content_layout.addStretch()
    
    def _create_main_parameters_group(self) -> QGroupBox:
        """יצירת קבוצת פרמטרים עיקריים"""
        group = QGroupBox("Main Parameters")
        layout = QFormLayout(group)
        
        # Temperature
        self.temperature_slider = ParameterSlider(
            "Temperature", 0.0, 2.0, 0.7, 0.1, 1
        )
        self.temperature_slider.valueChanged.connect(self._on_parameter_changed)
        layout.addRow("Temperature:", self.temperature_slider)
        
        # Max Tokens
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 8192)
        self.max_tokens_spin.setValue(1000)
        self.max_tokens_spin.setSuffix(" tokens")
        self.max_tokens_spin.valueChanged.connect(self._on_parameter_changed)
        layout.addRow("Max Tokens:", self.max_tokens_spin)
        
        # Top P
        self.top_p_slider = ParameterSlider(
            "Top P", 0.0, 1.0, 0.9, 0.01, 2
        )
        self.top_p_slider.valueChanged.connect(self._on_parameter_changed)
        layout.addRow("Top P:", self.top_p_slider)
        
        return group
    
    def _create_advanced_parameters_group(self) -> QGroupBox:
        """יצירת קבוצת פרמטרים מתקדמים"""
        group = QGroupBox("Advanced Parameters")
        layout = QFormLayout(group)
        
        # Frequency Penalty
        self.freq_penalty_slider = ParameterSlider(
            "Frequency Penalty", -2.0, 2.0, 0.0, 0.1, 1
        )
        self.freq_penalty_slider.valueChanged.connect(self._on_parameter_changed)
        layout.addRow("Frequency Penalty:", self.freq_penalty_slider)
        
        # Presence Penalty
        self.presence_penalty_slider = ParameterSlider(
            "Presence Penalty", -2.0, 2.0, 0.0, 0.1, 1
        )
        self.presence_penalty_slider.valueChanged.connect(self._on_parameter_changed)
        layout.addRow("Presence Penalty:", self.presence_penalty_slider)
        
        # Stop Sequences
        self.stop_sequences_edit = QLineEdit()
        self.stop_sequences_edit.setPlaceholderText("Enter stop sequences separated by commas")
        self.stop_sequences_edit.textChanged.connect(self._on_parameter_changed)
        layout.addRow("Stop Sequences:", self.stop_sequences_edit)
        
        return group
    
    def _create_presets_group(self) -> QGroupBox:
        """יצירת קבוצת פרסטים"""
        group = QGroupBox("Parameter Presets")
        layout = QVBoxLayout(group)
        
        # כפתורי פעולה
        actions_layout = QHBoxLayout()
        
        self.save_preset_btn = QPushButton("💾 Save Preset")
        self.save_preset_btn.clicked.connect(self._save_custom_preset)
        
        self.reset_btn = QPushButton("🔄 Reset to Default")
        self.reset_btn.clicked.connect(self._reset_to_default)
        
        actions_layout.addWidget(self.save_preset_btn)
        actions_layout.addWidget(self.reset_btn)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        # אזור פרסטים
        self.presets_scroll = QScrollArea()
        self.presets_scroll.setFixedHeight(150)
        self.presets_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.presets_widget = QWidget()
        self.presets_layout = QHBoxLayout(self.presets_widget)
        self.presets_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.presets_scroll.setWidget(self.presets_widget)
        layout.addWidget(self.presets_scroll)
        
        self._populate_presets()
        
        return group
    
    def _create_preview_group(self) -> QGroupBox:
        """יצירת קבוצת תצוגה מקדימה"""
        group = QGroupBox("Parameter Preview")
        layout = QVBoxLayout(group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(120)
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                border: 1px solid #333;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        
        layout.addWidget(self.preview_text)
        
        return group
    
    def _populate_presets(self):
        """מילוי פרסטים"""
        # ניקוי פרסטים קיימים
        for i in reversed(range(self.presets_layout.count())):
            child = self.presets_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # פרסטים מובנים
        builtin_presets = {
            "creative": LLMParameters.get_preset("creative"),
            "balanced": LLMParameters.get_preset("balanced"),
            "precise": LLMParameters.get_preset("precise"),
            "code": LLMParameters.get_preset("code"),
            "chat": LLMParameters.get_preset("chat")
        }
        
        # הוספת פרסטים מובנים
        for name, params in builtin_presets.items():
            card = PresetCard(name, params, is_builtin=True)
            card.selected.connect(self._load_preset)
            self.presets_layout.addWidget(card)
        
        # הוספת פרסטים מותאמים אישית
        for name, params in self.custom_presets.items():
            card = PresetCard(name, params, is_builtin=False)
            card.selected.connect(self._load_preset)
            card.deleted.connect(self._delete_custom_preset)
            self.presets_layout.addWidget(card)
        
        self.presets_layout.addStretch()
    
    def _on_parameter_changed(self):
        """טיפול בשינוי פרמטר"""
        # עדכון הפרמטרים הנוכחיים
        self._update_current_parameters()
        
        # עדכון תצוגה מקדימה עם דיליי
        self.preview_timer.stop()
        self.preview_timer.start(500)  # 500ms דיליי
        
        # שליחת אות שינוי
        self.parameters_changed.emit(self.current_parameters.to_dict())
    
    def _update_current_parameters(self):
        """עדכון הפרמטרים הנוכחיים מהממשק"""
        # עדכון stop sequences
        stop_text = self.stop_sequences_edit.text().strip()
        stop_sequences = [s.strip() for s in stop_text.split(',') if s.strip()] if stop_text else []
        
        self.current_parameters = LLMParameters(
            temperature=self.temperature_slider.get_value(),
            max_tokens=self.max_tokens_spin.value(),
            top_p=self.top_p_slider.get_value(),
            frequency_penalty=self.freq_penalty_slider.get_value(),
            presence_penalty=self.presence_penalty_slider.get_value(),
            stop_sequences=stop_sequences
        )
    
    def _update_all_displays(self):
        """עדכון כל התצוגות לפי הפרמטרים הנוכחיים"""
        # שמירת הפרמטרים הנוכחיים לפני עדכון הממשק
        saved_params = self.current_parameters
        
        # עדכון הממשק
        self.temperature_slider.set_value(saved_params.temperature)
        self.max_tokens_spin.setValue(saved_params.max_tokens)
        self.top_p_slider.set_value(saved_params.top_p)
        self.freq_penalty_slider.set_value(saved_params.frequency_penalty)
        self.presence_penalty_slider.set_value(saved_params.presence_penalty)
        
        # עדכון stop sequences
        stop_text = ', '.join(saved_params.stop_sequences)
        self.stop_sequences_edit.setText(stop_text)
        
        # שחזור הפרמטרים במקרה שהם השתנו בגלל אותות מהממשק
        self.current_parameters = saved_params
        
        self._update_preview()
    
    def _update_preview(self):
        """עדכון תצוגה מקדימה"""
        params = self.current_parameters
        
        # קביעת סגנון תגובה
        if params.temperature > 0.8:
            creativity = "High creativity - varied and imaginative responses"
        elif params.temperature < 0.4:
            creativity = "Low creativity - focused and consistent responses"
        else:
            creativity = "Balanced creativity - moderate variation"
        
        # קביעת אורך תגובה
        if params.max_tokens > 1500:
            length = "Long responses"
        elif params.max_tokens < 500:
            length = "Short responses"
        else:
            length = "Medium length responses"
        
        # קביעת מגוון מילים
        if params.top_p > 0.9:
            diversity = "High word diversity"
        elif params.top_p < 0.7:
            diversity = "Limited word diversity"
        else:
            diversity = "Balanced word diversity"
        
        # קביעת חזרות
        repetition = ""
        if params.frequency_penalty > 0.5:
            repetition = "Strongly avoids repetition"
        elif params.frequency_penalty > 0:
            repetition = "Moderately avoids repetition"
        elif params.frequency_penalty < -0.5:
            repetition = "May repeat frequently"
        else:
            repetition = "Natural repetition patterns"
        
        # בניית טקסט התצוגה המקדימה
        preview_lines = [
            f"🎨 {creativity}",
            f"📏 {length} (up to {params.max_tokens} tokens)",
            f"🎯 {diversity} (top-p: {params.top_p})",
            f"🔄 {repetition}"
        ]
        
        if params.stop_sequences:
            preview_lines.append(f"⏹️ Stop at: {', '.join(params.stop_sequences[:3])}")
        
        preview_text = "\n".join(preview_lines)
        self.preview_text.setPlainText(preview_text)
    
    def _load_preset(self, preset_name: str):
        """טעינת פרסט"""
        # בדיקה אם זה פרסט מובנה
        if preset_name in ["creative", "balanced", "precise", "code", "chat"]:
            params = LLMParameters.get_preset(preset_name)
        else:
            # פרסט מותאם אישית
            params = self.custom_presets.get(preset_name)
            if not params:
                return
        
        self.current_parameters = params
        self._update_all_displays()
        
        # שליחת אותות
        self.parameters_changed.emit(self.current_parameters.to_dict())
        self.preset_loaded.emit(preset_name)
    
    def _save_custom_preset(self):
        """שמירת פרסט מותאם אישית"""
        name, ok = QInputDialog.getText(
            self, 
            "Save Preset", 
            "Enter preset name:",
            text="My Preset"
        )
        
        if ok and name.strip():
            name = name.strip()
            
            # בדיקה שהשם לא קיים כפרסט מובנה
            if name.lower() in ["creative", "balanced", "precise", "code", "chat"]:
                QMessageBox.warning(
                    self,
                    "Invalid Name",
                    "Cannot use built-in preset names. Please choose a different name."
                )
                return
            
            # שמירת הפרסט
            self.custom_presets[name] = LLMParameters(
                temperature=self.current_parameters.temperature,
                max_tokens=self.current_parameters.max_tokens,
                top_p=self.current_parameters.top_p,
                frequency_penalty=self.current_parameters.frequency_penalty,
                presence_penalty=self.current_parameters.presence_penalty,
                stop_sequences=self.current_parameters.stop_sequences.copy()
            )
            
            # שמירה לקובץ
            self._save_custom_presets()
            
            # עדכון תצוגה
            self._populate_presets()
            
            QMessageBox.information(
                self,
                "Preset Saved",
                f"Preset '{name}' has been saved successfully."
            )
    
    def _delete_custom_preset(self, preset_name: str):
        """מחיקת פרסט מותאם אישית"""
        reply = QMessageBox.question(
            self,
            "Delete Preset",
            f"Are you sure you want to delete the preset '{preset_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if preset_name in self.custom_presets:
                del self.custom_presets[preset_name]
                self._save_custom_presets()
                self._populate_presets()
    
    def _reset_to_default(self):
        """איפוס לפרמטרים ברירת מחדל"""
        self.current_parameters = LLMParameters()
        self._update_all_displays()
        self.parameters_changed.emit(self.current_parameters.to_dict())
    
    def _get_presets_file_path(self) -> str:
        """קבלת נתיב קובץ הפרסטים"""
        # יצירת תיקיית הגדרות אם לא קיימת
        settings_dir = os.path.expanduser("~/.audio_chat_qt")
        os.makedirs(settings_dir, exist_ok=True)
        return os.path.join(settings_dir, "parameter_presets.json")
    
    def _save_custom_presets(self):
        """שמירת פרסטים מותאמים אישית לקובץ"""
        try:
            presets_data = {}
            for name, params in self.custom_presets.items():
                presets_data[name] = params.to_dict()
            
            with open(self._get_presets_file_path(), 'w', encoding='utf-8') as f:
                json.dump(presets_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving presets: {e}")
    
    def _load_custom_presets(self):
        """טעינת פרסטים מותאמים אישית מקובץ"""
        try:
            presets_file = self._get_presets_file_path()
            if os.path.exists(presets_file):
                with open(presets_file, 'r', encoding='utf-8') as f:
                    presets_data = json.load(f)
                
                self.custom_presets = {}
                for name, params_dict in presets_data.items():
                    self.custom_presets[name] = LLMParameters.from_dict(params_dict)
        except Exception as e:
            print(f"Error loading presets: {e}")
            self.custom_presets = {}
    
    # Public API
    
    def get_parameters(self) -> LLMParameters:
        """קבלת הפרמטרים הנוכחיים"""
        # עדכון הפרמטרים מהממשק רק אם הם לא עודכנו לאחרונה
        self._update_current_parameters()
        return self.current_parameters
    
    def set_parameters(self, parameters: LLMParameters):
        """הגדרת פרמטרים"""
        self.current_parameters = parameters
        self._update_all_displays()
    
    def validate_parameters(self) -> tuple[bool, str]:
        """בדיקת תקינות הפרמטרים"""
        self._update_current_parameters()
        
        if not self.current_parameters.validate():
            return False, "Invalid parameter values detected"
        
        return True, "Parameters are valid"
    
    def export_parameters(self) -> Dict[str, Any]:
        """ייצוא פרמטרים למילון"""
        self._update_current_parameters()
        return self.current_parameters.to_dict()
    
    def import_parameters(self, params_dict: Dict[str, Any]):
        """ייבוא פרמטרים ממילון"""
        try:
            parameters = LLMParameters.from_dict(params_dict)
            self.set_parameters(parameters)
            return True
        except Exception as e:
            print(f"Error importing parameters: {e}")
            return False
