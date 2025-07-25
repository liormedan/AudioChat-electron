#!/usr/bin/env python3
"""
Simple test for ModelTester component functionality
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui.components.llm.model_tester import ModelTester, TestPrompt, TestResult, TestStatus


def test_model_tester_basic_functionality():
    """Test basic ModelTester functionality"""
    print("Testing ModelTester basic functionality...")
    
    # Create QApplication
    app = QApplication([])
    
    # Create ModelTester
    model_tester = ModelTester()
    
    # Test 1: Check initialization
    assert model_tester is not None
    assert hasattr(model_tester, 'predefined_prompts')
    assert len(model_tester.predefined_prompts) > 0
    print("✓ Initialization test passed")
    
    # Test 2: Check predefined prompts
    audio_prompts = [p for p in model_tester.predefined_prompts if p.is_audio_specific]
    assert len(audio_prompts) >= 2
    print("✓ Audio-specific prompts test passed")
    
    # Test 3: Check UI components
    assert hasattr(model_tester, 'tab_widget')
    assert model_tester.tab_widget.count() == 4  # 4 tabs
    print("✓ UI components test passed")
    
    # Test 4: Check prompt filtering
    initial_count = model_tester.prompt_list.count()
    model_tester.prompt_category_combo.setCurrentText("Audio Processing")
    model_tester.filter_prompts()
    filtered_count = model_tester.prompt_list.count()
    assert filtered_count <= initial_count
    print("✓ Prompt filtering test passed")
    
    # Test 5: Check test result storage
    test_result = TestResult(
        id="test_1",
        test_id="test_1",
        model_id="gpt-4",
        prompt_id="prompt_1",
        response="Test response",
        response_time=1.5,
        token_count=100,
        cost=0.002,
        quality_score=0.8,
        status=TestStatus.COMPLETED
    )
    
    model_tester.test_results["test_1"] = test_result
    assert "test_1" in model_tester.test_results
    print("✓ Test result storage test passed")
    
    # Test 6: Check history table update
    model_tester.update_history_table()
    assert model_tester.history_table.rowCount() == 1
    print("✓ History table update test passed")
    
    # Test 7: Check performance metrics update
    model_tester.update_performance_metrics()
    print("✓ Performance metrics update test passed")
    
    print("All tests passed! ✓")
    
    # Close application
    app.quit()


def test_test_prompt_creation():
    """Test TestPrompt creation and properties"""
    print("\nTesting TestPrompt creation...")
    
    prompt = TestPrompt(
        id="test_prompt",
        name="Test Audio Prompt",
        category="Audio Processing",
        prompt_text="Analyze this audio file",
        expected_keywords=["audio", "analysis"],
        is_audio_specific=True
    )
    
    assert prompt.id == "test_prompt"
    assert prompt.name == "Test Audio Prompt"
    assert prompt.is_audio_specific is True
    assert "audio" in prompt.expected_keywords
    print("✓ TestPrompt creation test passed")


def test_test_result_creation():
    """Test TestResult creation and properties"""
    print("\nTesting TestResult creation...")
    
    result = TestResult(
        id="result_1",
        test_id="test_1",
        model_id="gpt-4",
        prompt_id="prompt_1",
        response="This is a test response",
        response_time=2.3,
        token_count=150,
        cost=0.003,
        quality_score=0.9,
        status=TestStatus.COMPLETED
    )
    
    assert result.id == "result_1"
    assert result.model_id == "gpt-4"
    assert result.response_time == 2.3
    assert result.status == TestStatus.COMPLETED
    print("✓ TestResult creation test passed")


def main():
    """Main test function"""
    print("Starting ModelTester component tests...\n")
    
    try:
        test_model_tester_basic_functionality()
        test_test_prompt_creation()
        test_test_result_creation()
        
        print("\n🎉 All ModelTester tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
