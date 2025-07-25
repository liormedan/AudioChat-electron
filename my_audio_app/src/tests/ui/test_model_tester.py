"""
Unit tests for ModelTester component
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from datetime import datetime
import uuid

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ui.components.llm.model_tester import (
    ModelTester, TestPrompt, TestResult, ModelComparison,
    TestStatus, TestWorker, CustomPromptDialog, TestDetailsDialog,
    ABTestResult
)
from models.llm_models import LLMModel, LLMProvider, ModelCapability


@pytest.fixture
def app():
    """Create QApplication instance for testing"""
    if not QApplication.instance():
        return QApplication([])
    return QApplication.instance()


@pytest.fixture
def model_tester(app):
    """Create ModelTester instance for testing"""
    return ModelTester()


@pytest.fixture
def sample_test_prompt():
    """Create sample test prompt"""
    return TestPrompt(
        id="test_prompt_1",
        name="Test Prompt",
        category="Audio Processing",
        prompt_text="Test prompt for audio processing",
        expected_keywords=["audio", "processing"],
        evaluation_criteria=["Accuracy", "Completeness"],
        is_audio_specific=True
    )


@pytest.fixture
def sample_test_result():
    """Create sample test result"""
    return TestResult(
        id="result_1",
        test_id="test_1",
        model_id="gpt-4",
        prompt_id="prompt_1",
        response="This is a test response",
        response_time=1.5,
        token_count=100,
        cost=0.002,
        quality_score=0.8,
        status=TestStatus.COMPLETED
    )


class TestModelTester:
    """Test cases for ModelTester component"""
    
    def test_initialization(self, model_tester):
        """Test ModelTester initialization"""
        assert model_tester is not None
        assert hasattr(model_tester, 'test_results')
        assert hasattr(model_tester, 'comparisons')
        assert hasattr(model_tester, 'predefined_prompts')
        assert isinstance(model_tester.test_results, dict)
        assert isinstance(model_tester.comparisons, list)
        assert len(model_tester.predefined_prompts) > 0
    
    def test_ui_components_exist(self, model_tester):
        """Test that all UI components are created"""
        # Check main components
        assert hasattr(model_tester, 'tab_widget')
        assert hasattr(model_tester, 'single_test_tab')
        assert hasattr(model_tester, 'comparison_tab')
        assert hasattr(model_tester, 'performance_tab')
        assert hasattr(model_tester, 'history_tab')
        
        # Check single test tab components
        assert hasattr(model_tester, 'model_combo')
        assert hasattr(model_tester, 'prompt_list')
        assert hasattr(model_tester, 'run_test_button')
        assert hasattr(model_tester, 'response_display')
        assert hasattr(model_tester, 'progress_bar')
        
        # Check comparison tab components
        assert hasattr(model_tester, 'model_checkboxes')
        assert hasattr(model_tester, 'comparison_prompts_list')
        assert hasattr(model_tester, 'start_comparison_button')
        assert hasattr(model_tester, 'comparison_results_table')
        
        # Check history tab components
        assert hasattr(model_tester, 'history_table')
        assert hasattr(model_tester, 'date_from_combo')
        assert hasattr(model_tester, 'model_filter_combo')
    
    def test_predefined_prompts_loaded(self, model_tester):
        """Test that predefined prompts are loaded correctly"""
        prompts = model_tester.predefined_prompts
        assert len(prompts) >= 5
        
        # Check for audio-specific prompts
        audio_prompts = [p for p in prompts if p.is_audio_specific]
        assert len(audio_prompts) >= 2
        
        # Check prompt categories
        categories = set(p.category for p in prompts)
        expected_categories = {"Audio Processing", "General Chat", "Code Generation", "Creative Writing"}
        assert expected_categories.issubset(categories)
    
    def test_prompt_list_update(self, model_tester):
        """Test prompt list updates correctly"""
        initial_count = model_tester.prompt_list.count()
        assert initial_count > 0
        
        # Test category filtering
        model_tester.prompt_category_combo.setCurrentText("Audio Processing")
        model_tester.filter_prompts()
        
        audio_count = model_tester.prompt_list.count()
        assert audio_count <= initial_count
        
        # Reset to all categories
        model_tester.prompt_category_combo.setCurrentText("All Categories")
        model_tester.filter_prompts()
        
        assert model_tester.prompt_list.count() == initial_count
    
    def test_prompt_selection(self, model_tester):
        """Test prompt selection functionality"""
        # Select first prompt
        if model_tester.prompt_list.count() > 0:
            item = model_tester.prompt_list.item(0)
            model_tester.prompt_list.setCurrentItem(item)
            model_tester.on_prompt_selected(item)
            
            # Check that prompt text is displayed
            prompt_text = model_tester.prompt_text_display.toPlainText()
            assert len(prompt_text) > 0
    
    def test_model_combo_populated(self, model_tester):
        """Test that model combo box is populated"""
        assert model_tester.model_combo.count() > 0
        
        # Check for expected models
        model_texts = [model_tester.model_combo.itemText(i) 
                      for i in range(model_tester.model_combo.count())]
        
        expected_models = ["GPT-4", "GPT-3.5-turbo", "Claude-3", "Gemini Pro"]
        for expected in expected_models:
            assert any(expected in text for text in model_texts)
    
    def test_comparison_checkboxes(self, model_tester):
        """Test model comparison checkboxes"""
        assert len(model_tester.model_checkboxes) > 0
        
        expected_models = ["GPT-4", "GPT-3.5-turbo", "Claude-3", "Gemini Pro"]
        for model in expected_models:
            assert model in model_tester.model_checkboxes
            checkbox = model_tester.model_checkboxes[model]
            assert hasattr(checkbox, 'isChecked')
    
    def test_run_single_test_validation(self, model_tester):
        """Test single test validation"""
        # Test without prompt selection
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            model_tester.run_single_test()
            mock_warning.assert_called_once()
    
    def test_comparison_validation(self, model_tester):
        """Test model comparison validation"""
        # Test without model selection
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            model_tester.start_model_comparison()
            mock_warning.assert_called_once()
    
    def test_test_result_storage(self, model_tester, sample_test_result):
        """Test test result storage"""
        test_id = "test_123"
        model_tester.test_results[test_id] = sample_test_result
        
        assert test_id in model_tester.test_results
        assert model_tester.test_results[test_id] == sample_test_result
    
    def test_history_table_update(self, model_tester, sample_test_result):
        """Test history table update"""
        # Add test result
        model_tester.test_results["test_1"] = sample_test_result
        
        # Update history table
        model_tester.update_history_table()
        
        # Check table has data
        assert model_tester.history_table.rowCount() == 1
        
        # Check data in table
        model_item = model_tester.history_table.item(0, 1)
        assert model_item.text() == sample_test_result.model_id
    
    def test_performance_metrics_update(self, model_tester, sample_test_result):
        """Test performance metrics update"""
        # Add test results
        model_tester.test_results["test_1"] = sample_test_result
        model_tester.test_results["test_2"] = sample_test_result
        
        # Update metrics
        model_tester.update_performance_metrics()
        
        # Check that metrics cards exist
        assert hasattr(model_tester, 'avg_response_time_card')
        assert hasattr(model_tester, 'total_tests_card')
        assert hasattr(model_tester, 'success_rate_card')
        assert hasattr(model_tester, 'avg_quality_card')
    
    def test_clear_history(self, model_tester, sample_test_result):
        """Test clear history functionality"""
        # Add test result
        model_tester.test_results["test_1"] = sample_test_result
        
        # Mock confirmation dialog
        with patch('PyQt6.QtWidgets.QMessageBox.question', 
                  return_value=QMessageBox.StandardButton.Yes):
            model_tester.clear_test_history()
        
        # Check that history is cleared
        assert len(model_tester.test_results) == 0
        assert len(model_tester.comparisons) == 0


class TestTestPrompt:
    """Test cases for TestPrompt dataclass"""
    
    def test_test_prompt_creation(self, sample_test_prompt):
        """Test TestPrompt creation"""
        assert sample_test_prompt.id == "test_prompt_1"
        assert sample_test_prompt.name == "Test Prompt"
        assert sample_test_prompt.category == "Audio Processing"
        assert sample_test_prompt.is_audio_specific is True
        assert "audio" in sample_test_prompt.expected_keywords
    
    def test_test_prompt_defaults(self):
        """Test TestPrompt default values"""
        prompt = TestPrompt(
            id="test",
            name="Test",
            category="Test",
            prompt_text="Test prompt"
        )
        
        assert prompt.expected_keywords == []
        assert prompt.evaluation_criteria == []
        assert prompt.is_audio_specific is False
        assert prompt.metadata == {}


class TestTestResult:
    """Test cases for TestResult dataclass"""
    
    def test_test_result_creation(self, sample_test_result):
        """Test TestResult creation"""
        assert sample_test_result.id == "result_1"
        assert sample_test_result.test_id == "test_1"
        assert sample_test_result.model_id == "gpt-4"
        assert sample_test_result.response_time == 1.5
        assert sample_test_result.status == TestStatus.COMPLETED
    
    def test_test_result_defaults(self):
        """Test TestResult default values"""
        result = TestResult(
            id="test",
            test_id="test",
            model_id="model",
            prompt_id="prompt",
            response="response",
            response_time=1.0,
            token_count=100,
            cost=0.001
        )
        
        assert result.quality_score is None
        assert result.status == TestStatus.COMPLETED
        assert result.error_message is None
        assert isinstance(result.timestamp, datetime)


class TestTestWorker:
    """Test cases for TestWorker thread"""
    
    def test_test_worker_creation(self):
        """Test TestWorker creation"""
        config = {
            "models": [{"id": "test", "name": "Test Model", "cost_per_token": 0.001}],
            "prompts": [TestPrompt("1", "Test", "Test", "Test prompt")]
        }
        
        worker = TestWorker(config)
        assert worker.test_config == config
        assert worker.is_cancelled is False
    
    def test_test_worker_cancel(self):
        """Test TestWorker cancellation"""
        config = {"models": [], "prompts": []}
        worker = TestWorker(config)
        
        worker.cancel()
        assert worker.is_cancelled is True
    
    def test_simulate_llm_call(self):
        """Test LLM call simulation"""
        config = {"models": [], "prompts": []}
        worker = TestWorker(config)
        
        model = {"id": "test", "name": "Test Model"}
        prompt = TestPrompt("1", "Audio Test", "Audio", "Test audio prompt")
        
        response = worker._simulate_llm_call(model, prompt)
        assert isinstance(response, str)
        assert len(response) > 0
        assert "audio" in response.lower()
    
    def test_evaluate_response(self):
        """Test response evaluation"""
        config = {"models": [], "prompts": []}
        worker = TestWorker(config)
        
        prompt = TestPrompt(
            "1", "Test", "Test", "Test prompt",
            expected_keywords=["test", "audio"]
        )
        
        response = "This is a test response about audio processing"
        score = worker._evaluate_response(response, prompt)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0


class TestCustomPromptDialog:
    """Test cases for CustomPromptDialog"""
    
    def test_custom_prompt_dialog_creation(self, app):
        """Test CustomPromptDialog creation"""
        dialog = CustomPromptDialog()
        assert dialog is not None
        assert hasattr(dialog, 'name_edit')
        assert hasattr(dialog, 'category_combo')
        assert hasattr(dialog, 'prompt_text_edit')
        assert hasattr(dialog, 'keywords_edit')
        assert hasattr(dialog, 'audio_specific_checkbox')
    
    def test_get_prompt(self, app):
        """Test getting prompt from dialog"""
        dialog = CustomPromptDialog()
        
        # Set test data
        dialog.name_edit.setPlainText("Test Prompt")
        dialog.category_combo.setCurrentText("Audio Processing")
        dialog.prompt_text_edit.setPlainText("Test prompt text")
        dialog.keywords_edit.setPlainText("test, audio, processing")
        dialog.audio_specific_checkbox.setChecked(True)
        
        prompt = dialog.get_prompt()
        
        assert prompt.name == "Test Prompt"
        assert prompt.category == "Audio Processing"
        assert prompt.prompt_text == "Test prompt text"
        assert "test" in prompt.expected_keywords
        assert "audio" in prompt.expected_keywords
        assert prompt.is_audio_specific is True


class TestTestDetailsDialog:
    """Test cases for TestDetailsDialog"""
    
    def test_test_details_dialog_creation(self, app, sample_test_result):
        """Test TestDetailsDialog creation"""
        dialog = TestDetailsDialog(sample_test_result)
        assert dialog is not None
        assert dialog.test_result == sample_test_result


class TestModelComparison:
    """Test cases for ModelComparison dataclass"""
    
    def test_model_comparison_creation(self):
        """Test ModelComparison creation"""
        comparison = ModelComparison(
            id="comp_1",
            name="Test Comparison",
            models=["gpt-4", "claude-3"],
            prompts=["prompt_1", "prompt_2"]
        )
        
        assert comparison.id == "comp_1"
        assert comparison.name == "Test Comparison"
        assert len(comparison.models) == 2
        assert len(comparison.prompts) == 2
        assert comparison.results == {}
        assert isinstance(comparison.created_at, datetime)
        assert comparison.completed_at is None


class TestBenchmarking:
    """Test benchmarking and A/B testing utilities"""

    def test_benchmark_models(self, model_tester, sample_test_prompt):
        models = [{"id": "gpt4", "name": "GPT-4", "cost_per_token": 0.001}]
        summary = model_tester.benchmark_models(models, [sample_test_prompt])
        assert "gpt4" in summary
        assert "avg_response_time" in summary["gpt4"]
        assert "avg_quality" in summary["gpt4"]

    def test_run_ab_test(self, model_tester, sample_test_prompt):
        m1 = {"id": "A", "name": "Model A", "cost_per_token": 0.001}
        m2 = {"id": "B", "name": "Model B", "cost_per_token": 0.001}
        results = model_tester.run_ab_test(m1, m2, [sample_test_prompt])
        assert len(results) == 1
        assert results[0].winner in {"A", "B", "tie"}

    def test_generate_performance_report(self, model_tester, tmp_path):
        summary = {"gpt": {"avg_response_time": 1.0, "avg_quality": 0.8}}
        output_file = tmp_path / "report.png"
        path = model_tester.generate_performance_report(summary, str(output_file))
        assert path == str(output_file)
        assert output_file.exists()


if __name__ == '__main__':
    pytest.main([__file__])
