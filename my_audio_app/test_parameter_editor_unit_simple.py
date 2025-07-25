#!/usr/bin/env python3
"""
בדיקות יחידה פשוטות לרכיב ParameterEditor
"""

import sys
import os
import tempfile
from PyQt6.QtWidgets import QApplication

# הוספת נתיב הפרויקט
sys.path.insert(0, 'src')

from ui.components.llm.parameter_editor import ParameterEditor, ParameterSlider, PresetCard
from models.llm_models import LLMParameters


def test_parameter_slider():
    """בדיקת ParameterSlider"""
    print("🧪 Testing ParameterSlider...")
    
    app = QApplication.instance() or QApplication([])
    
    # יצירת סליידר
    slider = ParameterSlider("Temperature", 0.0, 1.0, 0.5, 0.1, 1)
    
    # בדיקת אתחול
    assert slider.name == "Temperature"
    assert slider.min_val == 0.0
    assert slider.max_val == 1.0
    
    # בדיקת הגדרה וקבלת ערך
    slider.set_value(0.7)
    assert abs(slider.get_value() - 0.7) < 0.01
    
    print("✅ ParameterSlider tests passed")


def test_preset_card():
    """בדיקת PresetCard"""
    print("🧪 Testing PresetCard...")
    
    app = QApplication.instance() or QApplication([])
    
    # יצירת פרמטרים
    params = LLMParameters(temperature=0.8, max_tokens=1500)
    
    # יצירת כרטיס פרסט מובנה
    builtin_card = PresetCard("creative", params, is_builtin=True)
    assert builtin_card.name == "creative"
    assert builtin_card.is_builtin is True
    
    # יצירת כרטיס פרסט מותאם אישית
    custom_card = PresetCard("my_preset", params, is_builtin=False)
    assert custom_card.name == "my_preset"
    assert custom_card.is_builtin is False
    
    print("✅ PresetCard tests passed")


def test_parameter_editor():
    """בדיקת ParameterEditor"""
    print("🧪 Testing ParameterEditor...")
    
    app = QApplication.instance() or QApplication([])
    
    # יצירת עורך פרמטרים
    with tempfile.TemporaryDirectory() as temp_dir:
        import os
        from unittest.mock import patch
        
        with patch('os.path.expanduser', return_value=temp_dir):
            editor = ParameterEditor()
    
    # בדיקת אתחול
    assert isinstance(editor.current_parameters, LLMParameters)
    assert editor.current_parameters.temperature == 0.7
    assert editor.current_parameters.max_tokens == 1000
    
    # בדיקת קבלת פרמטרים
    params = editor.get_parameters()
    assert isinstance(params, LLMParameters)
    
    # בדיקת הגדרת פרמטרים
    new_params = LLMParameters(temperature=0.8, max_tokens=1200)
    editor.set_parameters(new_params)
    
    # בדיקה ישירה של הפרמטרים שהוגדרו
    assert abs(editor.current_parameters.temperature - 0.8) < 0.01
    assert editor.current_parameters.max_tokens == 1200
    
    # בדיקה שהממשק עודכן נכון
    assert abs(editor.temperature_slider.get_value() - 0.8) < 0.01
    assert editor.max_tokens_spin.value() == 1200
    
    # בדיקת תקינות פרמטרים
    valid, message = editor.validate_parameters()
    assert valid is True
    assert "valid" in message.lower()
    
    # בדיקת ייצוא וייבוא
    exported = editor.export_parameters()
    assert isinstance(exported, dict)
    assert 'temperature' in exported
    assert 'max_tokens' in exported
    
    success = editor.import_parameters(exported)
    assert success is True
    
    # בדיקת טעינת פרסט
    editor._load_preset("creative")
    creative_params = LLMParameters.get_preset("creative")
    assert abs(editor.current_parameters.temperature - creative_params.temperature) < 0.01
    
    # בדיקת איפוס
    editor._reset_to_default()
    default_params = LLMParameters()
    assert abs(editor.current_parameters.temperature - default_params.temperature) < 0.01
    
    print("✅ ParameterEditor tests passed")


def test_llm_parameters_presets():
    """בדיקת פרסטי LLMParameters"""
    print("🧪 Testing LLMParameters presets...")
    
    # בדיקת פרסטים מובנים
    presets = ["creative", "balanced", "precise", "code", "chat"]
    
    for preset_name in presets:
        params = LLMParameters.get_preset(preset_name)
        assert isinstance(params, LLMParameters)
        assert params.validate() is True
        print(f"  ✅ {preset_name} preset: temp={params.temperature}, tokens={params.max_tokens}")
    
    print("✅ LLMParameters presets tests passed")


def test_parameter_validation():
    """בדיקת תקינות פרמטרים"""
    print("🧪 Testing parameter validation...")
    
    # פרמטרים תקינים
    valid_params = LLMParameters(
        temperature=0.7,
        max_tokens=1000,
        top_p=0.9,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    assert valid_params.validate() is True
    
    # פרמטרים לא תקינים - temperature מחוץ לטווח
    invalid_params = LLMParameters(temperature=3.0)  # מחוץ לטווח 0-2
    assert invalid_params.validate() is False
    
    # פרמטרים לא תקינים - top_p מחוץ לטווח
    invalid_params2 = LLMParameters(top_p=1.5)  # מחוץ לטווח 0-1
    assert invalid_params2.validate() is False
    
    # פרמטרים לא תקינים - max_tokens שלילי
    invalid_params3 = LLMParameters(max_tokens=-100)
    assert invalid_params3.validate() is False
    
    print("✅ Parameter validation tests passed")


def main():
    """הרצת כל הבדיקות"""
    print("🚀 Starting ParameterEditor unit tests...\n")
    
    try:
        test_parameter_slider()
        test_preset_card()
        test_parameter_editor()
        test_llm_parameters_presets()
        test_parameter_validation()
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)