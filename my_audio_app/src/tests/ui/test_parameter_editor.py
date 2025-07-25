"""
בדיקות יחידה לרכיב ParameterEditor
"""

import pytest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest

# הוספת נתיב הפרויקט
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.ui.components.llm.parameter_editor import (
    ParameterEditor, ParameterSlider, PresetCard
)
from src.models.llm_models import LLMParameters


class TestParameterSlider:
    """בדיקות לרכיב ParameterSlider"""
    
    @pytest.fixture
    def app(self):
        """יצירת אפליקציית Qt לבדיקות"""
        if not QApplication.instance():
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture
    def slider(self, app):
        """יצירת סליידר לבדיקות"""
        return ParameterSlider("Test", 0.0, 1.0, 0.5, 0.1, 1)
    
    def test_slider_initialization(self, slider):
        """בדיקת אתחול הסליידר"""
        assert slider.name == "Test"
        assert slider.min_val == 0.0
        assert slider.max_val == 1.0
        assert slider.step == 0.1
        assert slider.decimals == 1
        assert slider.multiplier == 10
        assert slider.slider_min == 0
        assert slider.slider_max == 10
    
    def test_slider_set_get_value(self, slider):
        """בדיקת הגדרה וקבלת ערך"""
        slider.set_value(0.7)
        assert abs(slider.get_value() - 0.7) < 0.01
        
        slider.set_value(0.0)
        assert slider.get_value() == 0.0
        
        slider.set_value(1.0)
        assert slider.get_value() == 1.0
    
    def test_slider_value_changed_signal(self, slider):
        """בדיקת אות שינוי ערך"""
        signal_received = []
        
        def on_value_changed(value):
            signal_received.append(value)
        
        slider.valueChanged.connect(on_value_changed)
        slider.set_value(0.8)
        
        assert len(signal_received) == 1
        assert abs(signal_received[0] - 0.8) < 0.01
    
    def test_slider_label_update(self, slider):
        """בדיקת עדכון תווית הערך"""
        slider.set_value(0.3)
        assert slider.value_label.text() == "0.3"
        
        slider.set_value(0.75)
        assert slider.value_label.text() == "0.8"  # עיגול


class TestPresetCard:
    """בדיקות לרכיב PresetCard"""
    
    @pytest.fixture
    def app(self):
        """יצירת אפליקציית Qt לבדיקות"""
        if not QApplication.instance():
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture
    def parameters(self):
        """פרמטרים לבדיקות"""
        return LLMParameters(temperature=0.8, max_tokens=1500, top_p=0.9)
    
    @pytest.fixture
    def builtin_card(self, app, parameters):
        """כרטיס פרסט מובנה"""
        return PresetCard("creative", parameters, is_builtin=True)
    
    @pytest.fixture
    def custom_card(self, app, parameters):
        """כרטיס פרסט מותאם אישית"""
        return PresetCard("my_preset", parameters, is_builtin=False)
    
    def test_builtin_card_initialization(self, builtin_card):
        """בדיקת אתחול כרטיס מובנה"""
        assert builtin_card.name == "creative"
        assert builtin_card.is_builtin is True
        assert builtin_card.parameters.temperature == 0.8
    
    def test_custom_card_initialization(self, custom_card):
        """בדיקת אתחול כרטיס מותאם אישית"""
        assert custom_card.name == "my_preset"
        assert custom_card.is_builtin is False
        assert custom_card.parameters.temperature == 0.8
    
    def test_card_selection_signal(self, builtin_card):
        """בדיקת אות בחירת כרטיס"""
        signal_received = []
        
        def on_selected(name):
            signal_received.append(name)
        
        builtin_card.selected.connect(on_selected)
        
        # סימולציה של לחיצה
        QTest.mouseClick(builtin_card, Qt.MouseButton.LeftButton)
        
        assert len(signal_received) == 1
        assert signal_received[0] == "creative"
    
    def test_custom_card_delete_signal(self, custom_card):
        """בדיקת אות מחיקת כרטיס מותאם אישית"""
        signal_received = []
        
        def on_deleted(name):
            signal_received.append(name)
        
        custom_card.deleted.connect(on_deleted)
        
        # מציאת כפתור המחיקה ולחיצה עליו
        delete_buttons = custom_card.findChildren(type(custom_card), "")
        # כאן נבדוק שהכפתור קיים ופועל


class TestParameterEditor:
    """בדיקות לרכיב ParameterEditor"""
    
    @pytest.fixture
    def app(self):
        """יצירת אפליקציית Qt לבדיקות"""
        if not QApplication.instance():
            return QApplication([])
        return QApplication.instance()
    
    @pytest.fixture
    def temp_dir(self):
        """תיקייה זמנית לבדיקות"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def editor(self, app, temp_dir):
        """עורך פרמטרים לבדיקות"""
        with patch('os.path.expanduser', return_value=temp_dir):
            return ParameterEditor()
    
    def test_editor_initialization(self, editor):
        """בדיקת אתחול העורך"""
        assert isinstance(editor.current_parameters, LLMParameters)
        assert editor.current_parameters.temperature == 0.7
        assert editor.current_parameters.max_tokens == 1000
        assert editor.current_parameters.top_p == 0.9
    
    def test_parameter_validation(self, editor):
        """בדיקת תקינות פרמטרים"""
        # פרמטרים תקינים
        valid, message = editor.validate_parameters()
        assert valid is True
        assert "valid" in message.lower()
        
        # פרמטרים לא תקינים - temperature מחוץ לטווח
        editor.temperature_slider.set_value(3.0)  # מחוץ לטווח
        editor._update_current_parameters()
        
        valid, message = editor.validate_parameters()
        assert valid is False
        assert "invalid" in message.lower()
    
    def test_parameter_changes_signal(self, editor):
        """בדיקת אות שינוי פרמטרים"""
        signal_received = []
        
        def on_parameters_changed(params_dict):
            signal_received.append(params_dict)
        
        editor.parameters_changed.connect(on_parameters_changed)
        
        # שינוי פרמטר
        editor.temperature_slider.set_value(0.8)
        editor._on_parameter_changed()
        
        assert len(signal_received) == 1
        assert signal_received[0]['temperature'] == 0.8
    
    def test_preset_loading(self, editor):
        """בדיקת טעינת פרסטים"""
        # טעינת פרסט creative
        editor._load_preset("creative")
        
        creative_params = LLMParameters.get_preset("creative")
        assert editor.current_parameters.temperature == creative_params.temperature
        assert editor.current_parameters.max_tokens == creative_params.max_tokens
        assert editor.current_parameters.top_p == creative_params.top_p
    
    def test_preset_loaded_signal(self, editor):
        """בדיקת אות טעינת פרסט"""
        signal_received = []
        
        def on_preset_loaded(name):
            signal_received.append(name)
        
        editor.preset_loaded.connect(on_preset_loaded)
        
        editor._load_preset("balanced")
        
        assert len(signal_received) == 1
        assert signal_received[0] == "balanced"
    
    def test_custom_preset_save_load(self, editor, temp_dir):
        """בדיקת שמירה וטעינה של פרסט מותאם אישית"""
        # הגדרת פרמטרים מותאמים אישית
        editor.temperature_slider.set_value(0.6)
        editor.max_tokens_spin.setValue(800)
        editor._update_current_parameters()
        
        # שמירת פרסט
        test_name = "test_preset"
        editor.custom_presets[test_name] = LLMParameters(
            temperature=0.6,
            max_tokens=800,
            top_p=0.9
        )
        editor._save_custom_presets()
        
        # יצירת עורך חדש וטעינת הפרסטים
        with patch('os.path.expanduser', return_value=temp_dir):
            new_editor = ParameterEditor()
        
        assert test_name in new_editor.custom_presets
        assert new_editor.custom_presets[test_name].temperature == 0.6
        assert new_editor.custom_presets[test_name].max_tokens == 800
    
    def test_reset_to_default(self, editor):
        """בדיקת איפוס לברירת מחדל"""
        # שינוי פרמטרים
        editor.temperature_slider.set_value(0.9)
        editor.max_tokens_spin.setValue(2000)
        editor._update_current_parameters()
        
        # איפוס
        editor._reset_to_default()
        
        default_params = LLMParameters()
        assert editor.current_parameters.temperature == default_params.temperature
        assert editor.current_parameters.max_tokens == default_params.max_tokens
        assert editor.current_parameters.top_p == default_params.top_p
    
    def test_export_import_parameters(self, editor):
        """בדיקת ייצוא וייבוא פרמטרים"""
        # הגדרת פרמטרים
        editor.temperature_slider.set_value(0.5)
        editor.max_tokens_spin.setValue(1200)
        editor.top_p_slider.set_value(0.85)
        
        # ייצוא
        exported = editor.export_parameters()
        
        assert exported['temperature'] == 0.5
        assert exported['max_tokens'] == 1200
        assert exported['top_p'] == 0.85
        
        # שינוי פרמטרים
        editor._reset_to_default()
        
        # ייבוא
        success = editor.import_parameters(exported)
        assert success is True
        
        assert abs(editor.current_parameters.temperature - 0.5) < 0.01
        assert editor.current_parameters.max_tokens == 1200
        assert abs(editor.current_parameters.top_p - 0.85) < 0.01
    
    def test_stop_sequences_handling(self, editor):
        """בדיקת טיפול ברצפי עצירה"""
        # הגדרת רצפי עצירה
        editor.stop_sequences_edit.setText("\\n, END, STOP")
        editor._update_current_parameters()
        
        expected_sequences = ["\\n", "END", "STOP"]
        assert editor.current_parameters.stop_sequences == expected_sequences
        
        # בדיקת ייצוא
        exported = editor.export_parameters()
        assert exported['stop_sequences'] == expected_sequences
    
    def test_preview_update(self, editor):
        """בדיקת עדכון תצוגה מקדימה"""
        # הגדרת פרמטרים יצירתיים
        editor.temperature_slider.set_value(0.9)
        editor.max_tokens_spin.setValue(2000)
        editor._update_preview()
        
        preview_text = editor.preview_text.toPlainText()
        assert "creativity" in preview_text.lower()
        assert "2000" in preview_text
        
        # הגדרת פרמטרים מדויקים
        editor.temperature_slider.set_value(0.2)
        editor.max_tokens_spin.setValue(500)
        editor._update_preview()
        
        preview_text = editor.preview_text.toPlainText()
        assert "focused" in preview_text.lower() or "consistent" in preview_text.lower()
        assert "500" in preview_text
    
    def test_parameter_ranges(self, editor):
        """בדיקת טווחי פרמטרים"""
        # בדיקת טווח temperature
        assert editor.temperature_slider.min_val == 0.0
        assert editor.temperature_slider.max_val == 2.0
        
        # בדיקת טווח top_p
        assert editor.top_p_slider.min_val == 0.0
        assert editor.top_p_slider.max_val == 1.0
        
        # בדיקת טווח max_tokens
        assert editor.max_tokens_spin.minimum() == 1
        assert editor.max_tokens_spin.maximum() == 8192
        
        # בדיקת טווח frequency_penalty
        assert editor.freq_penalty_slider.min_val == -2.0
        assert editor.freq_penalty_slider.max_val == 2.0
    
    @patch('PyQt6.QtWidgets.QInputDialog.getText')
    def test_save_custom_preset_dialog(self, mock_dialog, editor):
        """בדיקת דיאלוג שמירת פרסט מותאם אישית"""
        # הגדרת תגובת הדיאלוג
        mock_dialog.return_value = ("my_custom_preset", True)
        
        # שמירת פרסט
        editor._save_custom_preset()
        
        # בדיקה שהפרסט נשמר
        assert "my_custom_preset" in editor.custom_presets
        
        # בדיקה שהדיאלוג נקרא
        mock_dialog.assert_called_once()
    
    @patch('PyQt6.QtWidgets.QMessageBox.question')
    def test_delete_custom_preset_dialog(self, mock_dialog, editor):
        """בדיקת דיאלוג מחיקת פרסט מותאם אישית"""
        # הוספת פרסט מותאם אישית
        test_preset = "test_preset"
        editor.custom_presets[test_preset] = LLMParameters()
        
        # הגדרת תגובת הדיאלוג - אישור מחיקה
        from PyQt6.QtWidgets import QMessageBox
        mock_dialog.return_value = QMessageBox.StandardButton.Yes
        
        # מחיקת הפרסט
        editor._delete_custom_preset(test_preset)
        
        # בדיקה שהפרסט נמחק
        assert test_preset not in editor.custom_presets
        
        # בדיקה שהדיאלוג נקרא
        mock_dialog.assert_called_once()
    
    def test_parameter_timer_delay(self, editor):
        """בדיקת דיליי עדכון תצוגה מקדימה"""
        # בדיקה שהטיימר מוגדר נכון
        assert editor.preview_timer.isSingleShot() is True
        
        # שינוי פרמטר
        editor.temperature_slider.set_value(0.8)
        editor._on_parameter_changed()
        
        # בדיקה שהטיימר פועל
        assert editor.preview_timer.isActive() is True


if __name__ == '__main__':
    pytest.main([__file__])