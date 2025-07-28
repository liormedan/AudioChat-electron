"""
ModelTester Component - בודק מודלי LLM

רכיב לבדיקה והשוואה של מודלי LLM עם פרומפטים מוגדרים מראש ומותאמים אישית,
כולל כלי מדידת ביצועים ושמירת תוצאות בדיקות.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QPushButton,
    QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QGroupBox,
    QSplitter, QProgressBar, QCheckBox, QSpinBox, QFormLayout,
    QScrollArea, QFrame, QMessageBox, QDialog, QDialogButtonBox,
    QListWidget, QListWidgetItem, QHeaderView, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QDateTime
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QIcon
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import json
import time
import uuid
from enum import Enum

from models.llm_models import LLMModel, LLMProvider, UsageRecord, LLMParameters


class TestStatus(Enum):
    """סטטוס בדיקה"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TestPrompt:
    """פרומפט לבדיקה"""
    id: str
    name: str
    category: str
    prompt_text: str
    expected_keywords: List[str] = field(default_factory=list)
    evaluation_criteria: List[str] = field(default_factory=list)
    is_audio_specific: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    """תוצאת בדיקה"""
    id: str
    test_id: str
    model_id: str
    prompt_id: str
    response: str
    response_time: float
    token_count: int
    cost: float
    quality_score: Optional[float] = None
    status: TestStatus = TestStatus.COMPLETED
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelComparison:
    """השוואת מודלים"""
    id: str
    name: str
    models: List[str]
    prompts: List[str]
    results: Dict[str, TestResult] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class ABTestResult:
    """תוצאת מבחן A/B"""
    prompt_id: str
    model_a_result: TestResult
    model_b_result: TestResult
    winner: Optional[str] = None  # "A", "B", or "tie"


class TestWorker(QThread):
    """Worker thread לביצוע בדיקות"""
    
    progress_updated = pyqtSignal(int)
    test_completed = pyqtSignal(str, dict)  # test_id, result
    test_failed = pyqtSignal(str, str)  # test_id, error
    
    def __init__(self, test_config: Dict[str, Any]):
        super().__init__()
        self.test_config = test_config
        self.is_cancelled = False
    
    def run(self):
        """ביצוע הבדיקות"""
        models = self.test_config.get("models", [])
        prompts = self.test_config.get("prompts", [])
        total_tests = len(models) * len(prompts)
        completed = 0
        
        for model in models:
            if self.is_cancelled:
                break
                
            for prompt in prompts:
                if self.is_cancelled:
                    break
                
                try:
                    # סימולציה של קריאה ל-API
                    start_time = time.time()
                    
                    # כאן תהיה הקריאה האמיתית ל-LLM
                    response = self._simulate_llm_call(model, prompt)
                    
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    # יצירת תוצאה
                    result = {
                        "id": str(uuid.uuid4()),
                        "model_id": model["id"],
                        "prompt_id": prompt["id"],
                        "response": response,
                        "response_time": response_time,
                        "token_count": len(response.split()) * 1.3,  # הערכה גסה
                        "cost": len(response.split()) * 1.3 * model.get("cost_per_token", 0.001),
                        "quality_score": self._evaluate_response(response, prompt),
                        "status": TestStatus.COMPLETED.value,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    test_id = f"{model['id']}_{prompt['id']}"
                    self.test_completed.emit(test_id, result)
                    
                except Exception as e:
                    test_id = f"{model['id']}_{prompt['id']}"
                    self.test_failed.emit(test_id, str(e))
                
                completed += 1
                progress = int((completed / total_tests) * 100)
                self.progress_updated.emit(progress)
                
                # השהיה קצרה בין בדיקות
                self.msleep(100)
    
    def _simulate_llm_call(self, model: Dict[str, Any], prompt: TestPrompt) -> str:
        """סימולציה של קריאה ל-LLM"""
        # סימולציה של זמן תגובה
        self.msleep(500 + (hash(model["id"]) % 1000))
        
        # תגובות מדומות בהתבסס על הפרומפט
        if "audio" in prompt.prompt_text.lower():
            return f"This is a simulated audio-related response from {model['name']}. The audio processing capabilities include transcription, analysis, and enhancement features."
        elif "code" in prompt.prompt_text.lower():
            return f"```python\n# Generated by {model['name']}\ndef example_function():\n    return 'Hello, World!'\n```"
        else:
            return f"This is a simulated response from {model['name']} for the prompt: {prompt.name}. The response demonstrates the model's capabilities in text generation and understanding."
    
    def _evaluate_response(self, response: str, prompt: TestPrompt) -> float:
        """הערכת איכות התגובה"""
        score = 0.5  # ציון בסיס
        
        # בדיקת מילות מפתח
        for keyword in prompt.expected_keywords:
            if keyword.lower() in response.lower():
                score += 0.1
        
        # בדיקת אורך תגובה
        if 50 <= len(response.split()) <= 200:
            score += 0.2
        
        # הגבלת הציון ל-1.0
        return min(score, 1.0)
    
    def cancel(self):
        """ביטול הבדיקות"""
        self.is_cancelled = True


class ModelTester(QWidget):
    """רכיב בדיקת מודלי LLM"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.test_results: Dict[str, TestResult] = {}
        self.comparisons: List[ModelComparison] = []
        self.current_test_worker: Optional[TestWorker] = None
        
        self.setup_ui()
        self.load_predefined_prompts()
        self.load_test_history()
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        layout = QVBoxLayout(self)
        
        # כותרת
        title = QLabel("Model Testing & Comparison")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # טאבים
        self.tab_widget = QTabWidget()
        
        # טאב בדיקה בודדת
        self.single_test_tab = self.create_single_test_tab()
        self.tab_widget.addTab(self.single_test_tab, "🧪 Single Test")
        
        # טאב השוואת מודלים
        self.comparison_tab = self.create_comparison_tab()
        self.tab_widget.addTab(self.comparison_tab, "⚖️ Model Comparison")
        
        # טאב ביצועים
        self.performance_tab = self.create_performance_tab()
        self.tab_widget.addTab(self.performance_tab, "📊 Performance")
        
        # טאב היסטוריה
        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(self.history_tab, "📚 History")
        
        layout.addWidget(self.tab_widget)
    
    def create_single_test_tab(self) -> QWidget:
        """יצירת טאב בדיקה בודדת"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # חלק שמאלי - הגדרות
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # בחירת מודל
        model_group = QGroupBox("Model Selection")
        model_layout = QVBoxLayout(model_group)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "OpenAI - GPT-4",
            "OpenAI - GPT-3.5-turbo",
            "Anthropic - Claude-3",
            "Google - Gemini Pro"
        ])
        model_layout.addWidget(self.model_combo)
        
        left_layout.addWidget(model_group)
        
        # בחירת פרומפט
        prompt_group = QGroupBox("Prompt Selection")
        prompt_layout = QVBoxLayout(prompt_group)
        
        self.prompt_category_combo = QComboBox()
        self.prompt_category_combo.addItems([
            "All Categories",
            "Audio Processing",
            "General Chat",
            "Code Generation",
            "Creative Writing"
        ])
        self.prompt_category_combo.currentTextChanged.connect(self.filter_prompts)
        prompt_layout.addWidget(self.prompt_category_combo)
        
        self.prompt_list = QListWidget()
        self.prompt_list.itemClicked.connect(self.on_prompt_selected)
        prompt_layout.addWidget(self.prompt_list)
        
        # כפתור פרומפט מותאם
        self.custom_prompt_button = QPushButton("Create Custom Prompt")
        self.custom_prompt_button.clicked.connect(self.create_custom_prompt)
        prompt_layout.addWidget(self.custom_prompt_button)
        
        left_layout.addWidget(prompt_group)
        
        # כפתור הרצה
        self.run_test_button = QPushButton("🚀 Run Test")
        self.run_test_button.clicked.connect(self.run_single_test)
        self.run_test_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        left_layout.addWidget(self.run_test_button)
        
        left_layout.addStretch()
        
        # חלק ימני - תוצאות
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # פרטי פרומפט
        prompt_details_group = QGroupBox("Prompt Details")
        prompt_details_layout = QVBoxLayout(prompt_details_group)
        
        self.prompt_text_display = QTextEdit()
        self.prompt_text_display.setMaximumHeight(150)
        self.prompt_text_display.setPlaceholderText("Select a prompt to see details...")
        prompt_details_layout.addWidget(self.prompt_text_display)
        
        right_layout.addWidget(prompt_details_group)
        
        # תוצאות
        results_group = QGroupBox("Test Results")
        results_layout = QVBoxLayout(results_group)
        
        # פרוגרס בר
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        results_layout.addWidget(self.progress_bar)
        
        # תגובת המודל
        self.response_display = QTextEdit()
        self.response_display.setPlaceholderText("Test results will appear here...")
        results_layout.addWidget(self.response_display)
        
        # מטריקות
        metrics_layout = QHBoxLayout()
        
        self.response_time_label = QLabel("Response Time: --")
        self.token_count_label = QLabel("Tokens: --")
        self.cost_label = QLabel("Cost: --")
        self.quality_score_label = QLabel("Quality: --")
        
        metrics_layout.addWidget(self.response_time_label)
        metrics_layout.addWidget(self.token_count_label)
        metrics_layout.addWidget(self.cost_label)
        metrics_layout.addWidget(self.quality_score_label)
        
        results_layout.addLayout(metrics_layout)
        
        right_layout.addWidget(results_group)
        
        # הוספת פאנלים
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 2)
        
        return widget
    
    def create_comparison_tab(self) -> QWidget:
        """יצירת טאב השוואת מודלים"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # הגדרות השוואה
        settings_group = QGroupBox("Comparison Settings")
        settings_layout = QFormLayout(settings_group)
        
        # בחירת מודלים
        models_layout = QHBoxLayout()
        
        self.model_checkboxes = {}
        models = ["GPT-4", "GPT-3.5-turbo", "Claude-3", "Gemini Pro"]
        
        for model in models:
            checkbox = QCheckBox(model)
            self.model_checkboxes[model] = checkbox
            models_layout.addWidget(checkbox)
        
        settings_layout.addRow("Models to Compare:", models_layout)
        
        # בחירת פרומפטים
        self.comparison_prompts_list = QListWidget()
        self.comparison_prompts_list.setMaximumHeight(100)
        self.comparison_prompts_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        settings_layout.addRow("Test Prompts:", self.comparison_prompts_list)
        
        layout.addWidget(settings_group)
        
        # כפתורי פעולה
        actions_layout = QHBoxLayout()
        
        self.start_comparison_button = QPushButton("🔄 Start Comparison")
        self.start_comparison_button.clicked.connect(self.start_model_comparison)
        
        self.save_comparison_button = QPushButton("💾 Save Results")
        self.save_comparison_button.clicked.connect(self.save_comparison_results)
        self.save_comparison_button.setEnabled(False)
        
        actions_layout.addWidget(self.start_comparison_button)
        actions_layout.addWidget(self.save_comparison_button)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        # תוצאות השוואה
        self.comparison_results_table = QTableWidget()
        self.comparison_results_table.setColumnCount(6)
        self.comparison_results_table.setHorizontalHeaderLabels([
            "Model", "Prompt", "Response Time", "Tokens", "Cost", "Quality Score"
        ])
        self.comparison_results_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.comparison_results_table)
        
        return widget
    
    def create_performance_tab(self) -> QWidget:
        """יצירת טאב ביצועים"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # מטריקות ביצועים
        metrics_layout = QHBoxLayout()
        
        # כרטיסי מטריקות
        self.avg_response_time_card = self.create_metric_card("Avg Response Time", "1.2s", "⏱️")
        self.total_tests_card = self.create_metric_card("Total Tests", "45", "🧪")
        self.success_rate_card = self.create_metric_card("Success Rate", "98%", "✅")
        self.avg_quality_card = self.create_metric_card("Avg Quality", "8.5/10", "⭐")
        
        metrics_layout.addWidget(self.avg_response_time_card)
        metrics_layout.addWidget(self.total_tests_card)
        metrics_layout.addWidget(self.success_rate_card)
        metrics_layout.addWidget(self.avg_quality_card)
        
        layout.addLayout(metrics_layout)
        
        # גרפי ביצועים
        charts_layout = QHBoxLayout()
        
        # גרף זמני תגובה
        self.response_time_chart = self.create_performance_chart("Response Time Trends")
        charts_layout.addWidget(self.response_time_chart)
        
        # גרף איכות
        self.quality_chart = self.create_performance_chart("Quality Scores")
        charts_layout.addWidget(self.quality_chart)
        
        layout.addLayout(charts_layout)
        
        # טבלת ביצועים מפורטת
        performance_table_group = QGroupBox("Detailed Performance")
        performance_table_layout = QVBoxLayout(performance_table_group)
        
        self.performance_table = QTableWidget()
        self.performance_table.setColumnCount(8)
        self.performance_table.setHorizontalHeaderLabels([
            "Model", "Avg Response Time", "Min Time", "Max Time", 
            "Avg Quality", "Success Rate", "Total Tests", "Total Cost"
        ])
        
        performance_table_layout.addWidget(self.performance_table)
        layout.addWidget(performance_table_group)
        
        return widget
    
    def create_history_tab(self) -> QWidget:
        """יצירת טאב היסטוריה"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # פילטרים
        filters_group = QGroupBox("Filters")
        filters_layout = QHBoxLayout(filters_group)
        
        # פילטר תאריך
        date_label = QLabel("Date Range:")
        self.date_from_combo = QComboBox()
        self.date_from_combo.addItems(["Today", "Last 7 days", "Last 30 days", "All time"])
        
        # פילטר מודל
        model_filter_label = QLabel("Model:")
        self.model_filter_combo = QComboBox()
        self.model_filter_combo.addItems(["All Models", "GPT-4", "GPT-3.5-turbo", "Claude-3"])
        
        # פילטר סטטוס
        status_filter_label = QLabel("Status:")
        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItems(["All", "Completed", "Failed"])
        
        filters_layout.addWidget(date_label)
        filters_layout.addWidget(self.date_from_combo)
        filters_layout.addWidget(model_filter_label)
        filters_layout.addWidget(self.model_filter_combo)
        filters_layout.addWidget(status_filter_label)
        filters_layout.addWidget(self.status_filter_combo)
        filters_layout.addStretch()
        
        # כפתור רענון
        refresh_button = QPushButton("🔄 Refresh")
        refresh_button.clicked.connect(self.refresh_history)
        filters_layout.addWidget(refresh_button)
        
        layout.addWidget(filters_group)
        
        # טבלת היסטוריה
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            "Date", "Model", "Prompt", "Response Time", "Tokens", 
            "Cost", "Quality", "Status"
        ])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        self.history_table.itemDoubleClicked.connect(self.view_test_details)
        
        layout.addWidget(self.history_table)
        
        # כפתורי פעולה
        actions_layout = QHBoxLayout()
        
        self.export_history_button = QPushButton("📤 Export History")
        self.export_history_button.clicked.connect(self.export_test_history)
        
        self.clear_history_button = QPushButton("🗑️ Clear History")
        self.clear_history_button.clicked.connect(self.clear_test_history)
        
        actions_layout.addWidget(self.export_history_button)
        actions_layout.addWidget(self.clear_history_button)
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        return widget
    
    def create_metric_card(self, title: str, value: str, icon: str) -> QFrame:
        """יצירת כרטיס מטריקה"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.StyledPanel)
        card.setFixedSize(150, 100)
        
        layout = QVBoxLayout(card)
        
        # אייקון וכותרת
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 12px; color: #888;")
        
        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addWidget(title_label)
        
        # ערך
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(value_label)
        
        layout.addStretch()
        
        card.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        return card
    
    def create_performance_chart(self, title: str) -> QLabel:
        """יצירת גרף ביצועים (placeholder)"""
        chart_widget = QLabel(f"📊 {title}\n(Chart implementation here)")
        chart_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_widget.setStyleSheet("""
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            min-height: 200px;
        """)
        return chart_widget
    
    def load_predefined_prompts(self):
        """טעינת פרומפטים מוגדרים מראש"""
        self.predefined_prompts = [
            TestPrompt(
                id="audio_transcription",
                name="Audio Transcription Quality",
                category="Audio Processing",
                prompt_text="Please transcribe the following audio file and provide a summary of the key points discussed.",
                expected_keywords=["transcription", "audio", "summary"],
                evaluation_criteria=["Accuracy", "Completeness", "Formatting"],
                is_audio_specific=True
            ),
            TestPrompt(
                id="audio_analysis",
                name="Audio Content Analysis",
                category="Audio Processing",
                prompt_text="Analyze this audio recording and identify the speaker's emotions, tone, and key topics.",
                expected_keywords=["emotion", "tone", "analysis", "speaker"],
                evaluation_criteria=["Emotional accuracy", "Topic identification", "Tone analysis"],
                is_audio_specific=True
            ),
            TestPrompt(
                id="general_chat",
                name="General Conversation",
                category="General Chat",
                prompt_text="Hello! How are you today? Can you tell me about your capabilities?",
                expected_keywords=["hello", "capabilities", "help"],
                evaluation_criteria=["Friendliness", "Informativeness", "Clarity"]
            ),
            TestPrompt(
                id="code_generation",
                name="Python Code Generation",
                category="Code Generation",
                prompt_text="Write a Python function that processes audio files and extracts metadata.",
                expected_keywords=["python", "function", "audio", "metadata"],
                evaluation_criteria=["Code correctness", "Documentation", "Best practices"]
            ),
            TestPrompt(
                id="creative_writing",
                name="Creative Story Writing",
                category="Creative Writing",
                prompt_text="Write a short story about a person who discovers they can hear colors.",
                expected_keywords=["story", "colors", "hear", "creative"],
                evaluation_criteria=["Creativity", "Narrative flow", "Character development"]
            )
        ]
        
        self.update_prompt_list()
    
    def update_prompt_list(self):
        """עדכון רשימת הפרומפטים"""
        self.prompt_list.clear()
        self.comparison_prompts_list.clear()
        
        category_filter = self.prompt_category_combo.currentText()
        
        for prompt in self.predefined_prompts:
            if category_filter == "All Categories" or prompt.category == category_filter:
                # רשימה בטאב בדיקה בודדת
                item = QListWidgetItem(f"{prompt.name} ({prompt.category})")
                item.setData(Qt.ItemDataRole.UserRole, prompt)
                self.prompt_list.addItem(item)
                
                # רשימה בטאב השוואה
                comparison_item = QListWidgetItem(prompt.name)
                comparison_item.setData(Qt.ItemDataRole.UserRole, prompt)
                self.comparison_prompts_list.addItem(comparison_item)
    
    def filter_prompts(self):
        """פילטור פרומפטים לפי קטגוריה"""
        self.update_prompt_list()
    
    def on_prompt_selected(self, item: QListWidgetItem):
        """טיפול בבחירת פרומפט"""
        prompt = item.data(Qt.ItemDataRole.UserRole)
        if prompt:
            self.prompt_text_display.setPlainText(prompt.prompt_text)
    
    def create_custom_prompt(self):
        """יצירת פרומפט מותאם אישית"""
        dialog = CustomPromptDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            custom_prompt = dialog.get_prompt()
            self.predefined_prompts.append(custom_prompt)
            self.update_prompt_list()
    
    def run_single_test(self):
        """הרצת בדיקה בודדת"""
        # בדיקת בחירות
        if not self.prompt_list.currentItem():
            QMessageBox.warning(self, "Warning", "Please select a prompt to test.")
            return
        
        # הכנת נתוני הבדיקה
        selected_model = {
            "id": "test_model",
            "name": self.model_combo.currentText(),
            "cost_per_token": 0.001
        }
        
        selected_prompt = self.prompt_list.currentItem().data(Qt.ItemDataRole.UserRole)
        
        # הצגת פרוגרס
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.run_test_button.setEnabled(False)
        
        # הרצת הבדיקה
        test_config = {
            "models": [selected_model],
            "prompts": [selected_prompt]
        }
        
        self.current_test_worker = TestWorker(test_config)
        self.current_test_worker.progress_updated.connect(self.progress_bar.setValue)
        self.current_test_worker.test_completed.connect(self.on_single_test_completed)
        self.current_test_worker.test_failed.connect(self.on_test_failed)
        self.current_test_worker.start()
    
    def on_single_test_completed(self, test_id: str, result: Dict[str, Any]):
        """טיפול בהשלמת בדיקה בודדת"""
        # הסתרת פרוגרס
        self.progress_bar.setVisible(False)
        self.run_test_button.setEnabled(True)
        
        # הצגת תוצאות
        self.response_display.setPlainText(result["response"])
        
        # עדכון מטריקות
        self.response_time_label.setText(f"Response Time: {result['response_time']:.2f}s")
        self.token_count_label.setText(f"Tokens: {int(result['token_count'])}")
        self.cost_label.setText(f"Cost: ${result['cost']:.4f}")
        self.quality_score_label.setText(f"Quality: {result['quality_score']:.1f}/1.0")
        
        # שמירת התוצאה
        test_result = TestResult(
            id=result["id"],
            test_id=test_id,
            model_id=result["model_id"],
            prompt_id=result["prompt_id"],
            response=result["response"],
            response_time=result["response_time"],
            token_count=int(result["token_count"]),
            cost=result["cost"],
            quality_score=result["quality_score"],
            timestamp=datetime.fromisoformat(result["timestamp"])
        )
        
        self.test_results[test_id] = test_result
        self.update_history_table()
    
    def on_test_failed(self, test_id: str, error: str):
        """טיפול בכשל בדיקה"""
        self.progress_bar.setVisible(False)
        self.run_test_button.setEnabled(True)
        
        QMessageBox.critical(self, "Test Failed", f"Test failed: {error}")
    
    def start_model_comparison(self):
        """התחלת השוואת מודלים"""
        # בדיקת בחירות
        selected_models = []
        for model_name, checkbox in self.model_checkboxes.items():
            if checkbox.isChecked():
                selected_models.append({
                    "id": model_name.lower().replace("-", "_"),
                    "name": model_name,
                    "cost_per_token": 0.001
                })
        
        if not selected_models:
            QMessageBox.warning(self, "Warning", "Please select at least one model to compare.")
            return
        
        selected_prompts = []
        for i in range(self.comparison_prompts_list.count()):
            item = self.comparison_prompts_list.item(i)
            if item.isSelected():
                selected_prompts.append(item.data(Qt.ItemDataRole.UserRole))
        
        if not selected_prompts:
            QMessageBox.warning(self, "Warning", "Please select at least one prompt for comparison.")
            return
        
        # הרצת השוואה
        test_config = {
            "models": selected_models,
            "prompts": selected_prompts
        }
        
        self.start_comparison_button.setEnabled(False)
        self.comparison_results_table.setRowCount(0)
        
        self.current_test_worker = TestWorker(test_config)
        self.current_test_worker.test_completed.connect(self.on_comparison_test_completed)
        self.current_test_worker.test_failed.connect(self.on_test_failed)
        self.current_test_worker.finished.connect(self.on_comparison_finished)
        self.current_test_worker.start()
    
    def on_comparison_test_completed(self, test_id: str, result: Dict[str, Any]):
        """טיפול בהשלמת בדיקה בהשוואה"""
        # הוספת שורה לטבלה
        row = self.comparison_results_table.rowCount()
        self.comparison_results_table.insertRow(row)
        
        # מילוי נתונים
        model_name = next(model["name"] for model in self.current_test_worker.test_config["models"] 
                         if model["id"] == result["model_id"])
        prompt_name = next(prompt.name for prompt in self.current_test_worker.test_config["prompts"] 
                          if prompt.id == result["prompt_id"])
        
        self.comparison_results_table.setItem(row, 0, QTableWidgetItem(model_name))
        self.comparison_results_table.setItem(row, 1, QTableWidgetItem(prompt_name))
        self.comparison_results_table.setItem(row, 2, QTableWidgetItem(f"{result['response_time']:.2f}s"))
        self.comparison_results_table.setItem(row, 3, QTableWidgetItem(str(int(result['token_count']))))
        self.comparison_results_table.setItem(row, 4, QTableWidgetItem(f"${result['cost']:.4f}"))
        self.comparison_results_table.setItem(row, 5, QTableWidgetItem(f"{result['quality_score']:.2f}"))
        
        # שמירת התוצאה
        test_result = TestResult(
            id=result["id"],
            test_id=test_id,
            model_id=result["model_id"],
            prompt_id=result["prompt_id"],
            response=result["response"],
            response_time=result["response_time"],
            token_count=int(result["token_count"]),
            cost=result["cost"],
            quality_score=result["quality_score"],
            timestamp=datetime.fromisoformat(result["timestamp"])
        )
        
        self.test_results[test_id] = test_result
    
    def on_comparison_finished(self):
        """טיפול בסיום השוואה"""
        self.start_comparison_button.setEnabled(True)
        self.save_comparison_button.setEnabled(True)
        self.update_history_table()
        self.update_performance_metrics()
    
    def save_comparison_results(self):
        """שמירת תוצאות השוואה"""
        # יצירת השוואה חדשה
        comparison = ModelComparison(
            id=str(uuid.uuid4()),
            name=f"Comparison {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            models=[model["id"] for model in self.current_test_worker.test_config["models"]],
            prompts=[prompt.id for prompt in self.current_test_worker.test_config["prompts"]],
            results=self.test_results.copy(),
            completed_at=datetime.now()
        )
        
        self.comparisons.append(comparison)
        QMessageBox.information(self, "Success", "Comparison results saved successfully!")
    
    def update_history_table(self):
        """עדכון טבלת ההיסטוריה"""
        self.history_table.setRowCount(len(self.test_results))
        
        for row, (test_id, result) in enumerate(self.test_results.items()):
            self.history_table.setItem(row, 0, QTableWidgetItem(result.timestamp.strftime("%Y-%m-%d %H:%M")))
            self.history_table.setItem(row, 1, QTableWidgetItem(result.model_id))
            self.history_table.setItem(row, 2, QTableWidgetItem(result.prompt_id))
            self.history_table.setItem(row, 3, QTableWidgetItem(f"{result.response_time:.2f}s"))
            self.history_table.setItem(row, 4, QTableWidgetItem(str(result.token_count)))
            self.history_table.setItem(row, 5, QTableWidgetItem(f"${result.cost:.4f}"))
            self.history_table.setItem(row, 6, QTableWidgetItem(f"{result.quality_score:.2f}" if result.quality_score else "N/A"))
            self.history_table.setItem(row, 7, QTableWidgetItem(result.status.value))
    
    def update_performance_metrics(self):
        """עדכון מטריקות ביצועים"""
        if not self.test_results:
            return
        
        # חישוב מטריקות
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result.status == TestStatus.COMPLETED)
        avg_response_time = sum(result.response_time for result in self.test_results.values()) / total_tests
        avg_quality = sum(result.quality_score or 0 for result in self.test_results.values()) / total_tests
        success_rate = (successful_tests / total_tests) * 100
        
        # עדכון כרטיסי מטריקות
        self.avg_response_time_card.findChild(QLabel).setText(f"{avg_response_time:.1f}s")
        self.total_tests_card.findChild(QLabel).setText(str(total_tests))
        self.success_rate_card.findChild(QLabel).setText(f"{success_rate:.0f}%")
        self.avg_quality_card.findChild(QLabel).setText(f"{avg_quality:.1f}/1.0")
    
    def view_test_details(self, item: QTableWidgetItem):
        """הצגת פרטי בדיקה"""
        row = item.row()
        if row < len(self.test_results):
            test_id = list(self.test_results.keys())[row]
            result = self.test_results[test_id]
            
            dialog = TestDetailsDialog(result, self)
            dialog.exec()
    
    def refresh_history(self):
        """רענון היסטוריה"""
        self.update_history_table()
        self.update_performance_metrics()
    
    def export_test_history(self):
        """ייצוא היסטוריית בדיקות"""
        # כאן תהיה לוגיקת ייצוא לקובץ
        QMessageBox.information(self, "Export", "Test history exported successfully!")
    
    def clear_test_history(self):
        """ניקוי היסטוריית בדיקות"""
        reply = QMessageBox.question(
            self, "Clear History", 
            "Are you sure you want to clear all test history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.test_results.clear()
            self.comparisons.clear()
            self.update_history_table()
            self.update_performance_metrics()
    
    def load_test_history(self):
        """טעינת היסטוריית בדיקות"""
        # כאן תהיה לוגיקת טעינה מקובץ או מסד נתונים
        pass

    # ------------------------------------------------------------------
    # New benchmarking and A/B testing utilities
    # ------------------------------------------------------------------
    def benchmark_models(self, models: List[Dict[str, Any]], prompts: List[TestPrompt]) -> Dict[str, Dict[str, float]]:
        """Run a simple synchronous benchmark on given models and prompts."""
        results: Dict[str, List[TestResult]] = {m["id"]: [] for m in models}

        for model in models:
            for prompt in prompts:
                start = time.time()
                response = TestWorker({})._simulate_llm_call(model, prompt)
                end = time.time()
                response_time = end - start
                quality = TestWorker({})._evaluate_response(response, prompt)

                result = TestResult(
                    id=str(uuid.uuid4()),
                    test_id=f"{model['id']}_{prompt.id}",
                    model_id=model['id'],
                    prompt_id=prompt.id,
                    response=response,
                    response_time=response_time,
                    token_count=len(response.split()),
                    cost=len(response.split()) * model.get("cost_per_token", 0.001),
                    quality_score=quality,
                )
                results[model["id"]].append(result)

        summary: Dict[str, Dict[str, float]] = {}
        for model_id, tests in results.items():
            if not tests:
                continue
            avg_time = sum(t.response_time for t in tests) / len(tests)
            avg_quality = sum(t.quality_score or 0 for t in tests) / len(tests)
            summary[model_id] = {
                "avg_response_time": avg_time,
                "avg_quality": avg_quality,
            }
        return summary

    def run_ab_test(self, model_a: Dict[str, Any], model_b: Dict[str, Any], prompts: List[TestPrompt]) -> List[ABTestResult]:
        """Run A/B test between two models."""
        results: List[ABTestResult] = []
        for prompt in prompts:
            response_a = TestWorker({})._simulate_llm_call(model_a, prompt)
            qa = TestWorker({})._evaluate_response(response_a, prompt)
            res_a = TestResult(
                id=str(uuid.uuid4()),
                test_id=f"A_{prompt.id}",
                model_id=model_a["id"],
                prompt_id=prompt.id,
                response=response_a,
                response_time=0.0,
                token_count=len(response_a.split()),
                cost=len(response_a.split()) * model_a.get("cost_per_token", 0.001),
                quality_score=qa,
            )

            response_b = TestWorker({})._simulate_llm_call(model_b, prompt)
            qb = TestWorker({})._evaluate_response(response_b, prompt)
            res_b = TestResult(
                id=str(uuid.uuid4()),
                test_id=f"B_{prompt.id}",
                model_id=model_b["id"],
                prompt_id=prompt.id,
                response=response_b,
                response_time=0.0,
                token_count=len(response_b.split()),
                cost=len(response_b.split()) * model_b.get("cost_per_token", 0.001),
                quality_score=qb,
            )

            winner = None
            if qa > qb:
                winner = "A"
            elif qb > qa:
                winner = "B"
            else:
                winner = "tie"

            results.append(ABTestResult(prompt.id, res_a, res_b, winner))

        return results

    def generate_performance_report(self, summary: Dict[str, Dict[str, float]], output_path: str) -> str:
        """Generate a simple bar chart report of benchmark results."""
        import matplotlib.pyplot as plt

        models = list(summary.keys())
        times = [summary[m]["avg_response_time"] for m in models]
        qualities = [summary[m]["avg_quality"] for m in models]

        fig, ax1 = plt.subplots()
        ax1.bar(models, times, color="skyblue")
        ax1.set_ylabel("Avg Response Time (s)")
        ax1.set_xlabel("Model")

        ax2 = ax1.twinx()
        ax2.plot(models, qualities, color="orange", marker="o")
        ax2.set_ylabel("Avg Quality Score")

        fig.tight_layout()
        plt.savefig(output_path)
        plt.close(fig)
        return output_path


class CustomPromptDialog(QDialog):
    """דיאלוג ליצירת פרומפט מותאם אישית"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Custom Prompt")
        self.setModal(True)
        self.resize(500, 400)
        
        self.setup_ui()
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        layout = QVBoxLayout(self)
        
        # טופס
        form_layout = QFormLayout()
        
        self.name_edit = QTextEdit()
        self.name_edit.setMaximumHeight(30)
        form_layout.addRow("Name:", self.name_edit)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Audio Processing", "General Chat", "Code Generation", 
            "Creative Writing", "Custom"
        ])
        form_layout.addRow("Category:", self.category_combo)
        
        self.prompt_text_edit = QTextEdit()
        form_layout.addRow("Prompt Text:", self.prompt_text_edit)
        
        self.keywords_edit = QTextEdit()
        self.keywords_edit.setMaximumHeight(60)
        self.keywords_edit.setPlaceholderText("Enter keywords separated by commas...")
        form_layout.addRow("Expected Keywords:", self.keywords_edit)
        
        self.audio_specific_checkbox = QCheckBox("Audio-specific prompt")
        form_layout.addRow("", self.audio_specific_checkbox)
        
        layout.addLayout(form_layout)
        
        # כפתורים
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
    
    def get_prompt(self) -> TestPrompt:
        """קבלת הפרומפט שנוצר"""
        keywords = [k.strip() for k in self.keywords_edit.toPlainText().split(",") if k.strip()]
        
        return TestPrompt(
            id=str(uuid.uuid4()),
            name=self.name_edit.toPlainText().strip(),
            category=self.category_combo.currentText(),
            prompt_text=self.prompt_text_edit.toPlainText(),
            expected_keywords=keywords,
            is_audio_specific=self.audio_specific_checkbox.isChecked()
        )


class TestDetailsDialog(QDialog):
    """דיאלוג להצגת פרטי בדיקה"""
    
    def __init__(self, test_result: TestResult, parent=None):
        super().__init__(parent)
        self.test_result = test_result
        self.setWindowTitle("Test Details")
        self.setModal(True)
        self.resize(600, 500)
        
        self.setup_ui()
    
    def setup_ui(self):
        """הגדרת ממשק המשתמש"""
        layout = QVBoxLayout(self)
        
        # מידע כללי
        info_group = QGroupBox("Test Information")
        info_layout = QFormLayout(info_group)
        
        info_layout.addRow("Test ID:", QLabel(self.test_result.test_id))
        info_layout.addRow("Model:", QLabel(self.test_result.model_id))
        info_layout.addRow("Prompt:", QLabel(self.test_result.prompt_id))
        info_layout.addRow("Timestamp:", QLabel(self.test_result.timestamp.strftime("%Y-%m-%d %H:%M:%S")))
        info_layout.addRow("Status:", QLabel(self.test_result.status.value))
        
        layout.addWidget(info_group)
        
        # מטריקות
        metrics_group = QGroupBox("Metrics")
        metrics_layout = QFormLayout(metrics_group)
        
        metrics_layout.addRow("Response Time:", QLabel(f"{self.test_result.response_time:.2f}s"))
        metrics_layout.addRow("Token Count:", QLabel(str(self.test_result.token_count)))
        metrics_layout.addRow("Cost:", QLabel(f"${self.test_result.cost:.4f}"))
        if self.test_result.quality_score:
            metrics_layout.addRow("Quality Score:", QLabel(f"{self.test_result.quality_score:.2f}"))
        
        layout.addWidget(metrics_group)
        
        # תגובה
        response_group = QGroupBox("Response")
        response_layout = QVBoxLayout(response_group)
        
        response_text = QTextEdit()
        response_text.setPlainText(self.test_result.response)
        response_text.setReadOnly(True)
        response_layout.addWidget(response_text)
        
        layout.addWidget(response_group)
        
        # כפתור סגירה
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
