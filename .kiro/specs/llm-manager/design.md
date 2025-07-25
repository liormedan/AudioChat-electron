# Design Document

## Overview

מסמך זה מתאר את העיצוב המפורט של דף LLM Manager באפליקציית Audio Chat QT. הדף יכלול ממשק מקיף לניהול מודלי שפה גדולים, הגדרת פרמטרים, מעקב אחר שימוש וניהול API keys. העיצוב יתמקד בחוויית משתמש אינטואיטיבית עם דגש על אבטחה וביצועים.

## Architecture

### Component Structure

```
src/ui/pages/
├── llm_manager_page.py (דף ניהול LLM)
│   ├── LLMManagerPage (QWidget)
│   │   ├── ProvidersPanel (ניהול ספקים)
│   │   ├── ModelsPanel (בחירת מודלים)
│   │   ├── SettingsPanel (הגדרות פרמטרים)
│   │   ├── UsagePanel (מעקב שימוש)
│   │   └── TestingPanel (בדיקות ומשוואות)
└── components/llm/
    ├── provider_card.py (כרטיס ספק)
    ├── model_selector.py (בוחר מודלים)
    ├── parameter_editor.py (עורך פרמטרים)
    ├── usage_monitor.py (מוניטור שימוש)
    ├── api_key_manager.py (מנהל API keys)
    └── model_tester.py (בודק מודלים)
```

### Integration Points

1. **Services Layer**: שילוב עם שירותי AI וניהול הגדרות
2. **Security Layer**: הצפנה ואחסון מאובטח של API keys
3. **Database Layer**: שמירת הגדרות, סטטיסטיקות ותוצאות בדיקות
4. **Main Window**: שילוב הדף בניווט הראשי

## Components and Interfaces

### LLMManagerPage Class

```python
class LLMManagerPage(QWidget):
    """דף ניהול מודלי LLM"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("llmManagerPage")
        
        # שירותים
        self.llm_service = LLMService()
        self.settings_service = SettingsService()
        self.usage_service = UsageService()
        
        # לייאאוט ראשי - טאבים
        self.tab_widget = QTabWidget()
        
        # טאבים
        self.providers_tab = self._create_providers_tab()
        self.models_tab = self._create_models_tab()
        self.settings_tab = self._create_settings_tab()
        self.usage_tab = self._create_usage_tab()
        self.testing_tab = self._create_testing_tab()
        
        # הוספת טאבים
        self.tab_widget.addTab(self.providers_tab, "🏢 Providers")
        self.tab_widget.addTab(self.models_tab, "🤖 Models")
        self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")
        self.tab_widget.addTab(self.usage_tab, "📊 Usage")
        self.tab_widget.addTab(self.testing_tab, "🧪 Testing")
        
        # לייאאוט
        layout = QVBoxLayout(self)
        layout.addWidget(self.tab_widget)
        
        # טעינת נתונים
        self.load_data()
    
    def _create_providers_tab(self):
        """יצירת טאב ספקים"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # כותרת
        title = QLabel("LLM Providers")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # רשת כרטיסי ספקים
        self.providers_grid = QGridLayout()
        
        # ספקים זמינים
        providers = [
            {"name": "OpenAI", "icon": "🤖", "models": ["GPT-4", "GPT-3.5-turbo"], "status": "connected"},
            {"name": "Anthropic", "icon": "🧠", "models": ["Claude-3", "Claude-2"], "status": "disconnected"},
            {"name": "Google", "icon": "🔍", "models": ["Gemini Pro", "PaLM 2"], "status": "disconnected"},
            {"name": "Cohere", "icon": "💬", "models": ["Command", "Generate"], "status": "disconnected"},
            {"name": "Hugging Face", "icon": "🤗", "models": ["Various"], "status": "disconnected"}
        ]
        
        # יצירת כרטיסי ספקים
        for i, provider in enumerate(providers):
            card = ProviderCard(provider)
            card.connection_changed.connect(self.on_provider_connection_changed)
            self.providers_grid.addWidget(card, i // 2, i % 2)
        
        layout.addLayout(self.providers_grid)
        layout.addStretch()
        
        return widget
    
    def _create_models_tab(self):
        """יצירת טאב מודלים"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # חלק שמאלי - רשימת מודלים
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # בוחר ספק
        provider_label = QLabel("Provider:")
        self.provider_combo = QComboBox()
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        
        left_layout.addWidget(provider_label)
        left_layout.addWidget(self.provider_combo)
        
        # רשימת מודלים
        models_label = QLabel("Available Models:")
        self.models_list = QListWidget()
        self.models_list.itemClicked.connect(self.on_model_selected)
        
        left_layout.addWidget(models_label)
        left_layout.addWidget(self.models_list)
        
        # חלק ימני - פרטי מודל
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # פרטי מודל נבחר
        self.model_details = ModelDetailsWidget()
        right_layout.addWidget(self.model_details)
        
        # כפתורי פעולה
        actions_layout = QHBoxLayout()
        
        self.set_active_button = QPushButton("Set as Active")
        self.set_active_button.clicked.connect(self.set_active_model)
        
        self.test_model_button = QPushButton("Test Model")
        self.test_model_button.clicked.connect(self.test_selected_model)
        
        actions_layout.addWidget(self.set_active_button)
        actions_layout.addWidget(self.test_model_button)
        
        right_layout.addLayout(actions_layout)
        
        # הוספת פאנלים
        layout.addWidget(left_panel, 1)
        layout.addWidget(right_panel, 2)
        
        return widget
    
    def _create_settings_tab(self):
        """יצירת טאב הגדרות"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # עורך פרמטרים
        self.parameter_editor = ParameterEditor()
        self.parameter_editor.parameters_changed.connect(self.on_parameters_changed)
        
        layout.addWidget(self.parameter_editor)
        
        return widget
    
    def _create_usage_tab(self):
        """יצירת טאב שימוש"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # מוניטור שימוש
        self.usage_monitor = UsageMonitor()
        layout.addWidget(self.usage_monitor)
        
        return widget
    
    def _create_testing_tab(self):
        """יצירת טאב בדיקות"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # בודק מודלים
        self.model_tester = ModelTester()
        layout.addWidget(self.model_tester)
        
        return widget
```

### ProviderCard Component

```python
class ProviderCard(QFrame):
    """כרטיס ספק LLM"""
    
    connection_changed = pyqtSignal(str, bool)  # provider_name, is_connected
    
    def __init__(self, provider_data, parent=None):
        super().__init__(parent)
        self.provider_data = provider_data
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setFixedSize(300, 200)
        
        # לייאאוט
        layout = QVBoxLayout(self)
        
        # כותרת עם אייקון
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(provider_data["icon"])
        icon_label.setStyleSheet("font-size: 32px;")
        
        name_label = QLabel(provider_data["name"])
        name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        
        # סטטוס חיבור
        self.status_label = QLabel()
        self.update_status_display()
        
        header_layout.addWidget(self.status_label)
        
        layout.addLayout(header_layout)
        
        # מודלים זמינים
        models_label = QLabel("Models:")
        models_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(models_label)
        
        models_text = ", ".join(provider_data["models"])
        models_display = QLabel(models_text)
        models_display.setWordWrap(True)
        models_display.setStyleSheet("color: #666;")
        layout.addWidget(models_display)
        
        layout.addStretch()
        
        # כפתורי פעולה
        actions_layout = QHBoxLayout()
        
        if provider_data["status"] == "connected":
            self.action_button = QPushButton("Configure")
            self.action_button.clicked.connect(self.configure_provider)
        else:
            self.action_button = QPushButton("Connect")
            self.action_button.clicked.connect(self.connect_provider)
        
        self.test_button = QPushButton("Test")
        self.test_button.clicked.connect(self.test_connection)
        self.test_button.setEnabled(provider_data["status"] == "connected")
        
        actions_layout.addWidget(self.action_button)
        actions_layout.addWidget(self.test_button)
        
        layout.addLayout(actions_layout)
        
        # עיצוב
        self.setStyleSheet("""
            ProviderCard {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 10px;
            }
            ProviderCard:hover {
                border-color: #555;
            }
        """)
    
    def update_status_display(self):
        """עדכון תצוגת סטטוס"""
        status = self.provider_data["status"]
        if status == "connected":
            self.status_label.setText("🟢 Connected")
            self.status_label.setStyleSheet("color: #4CAF50;")
        else:
            self.status_label.setText("🔴 Disconnected")
            self.status_label.setStyleSheet("color: #F44336;")
    
    def connect_provider(self):
        """חיבור לספק"""
        dialog = APIKeyDialog(self.provider_data["name"], self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            api_key = dialog.get_api_key()
            # בדיקת חיבור
            if self.test_api_key(api_key):
                self.provider_data["status"] = "connected"
                self.update_status_display()
                self.action_button.setText("Configure")
                self.action_button.clicked.disconnect()
                self.action_button.clicked.connect(self.configure_provider)
                self.test_button.setEnabled(True)
                self.connection_changed.emit(self.provider_data["name"], True)
    
    def configure_provider(self):
        """הגדרת ספק"""
        dialog = ProviderConfigDialog(self.provider_data, self)
        dialog.exec()
    
    def test_connection(self):
        """בדיקת חיבור"""
        # כאן יבוצע test API call
        QMessageBox.information(self, "Test Result", "Connection test successful!")
```

### ParameterEditor Component

```python
class ParameterEditor(QWidget):
    """עורך פרמטרי מודל"""
    
    parameters_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # לייאאוט
        layout = QVBoxLayout(self)
        
        # כותרת
        title = QLabel("Model Parameters")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        # פרמטרים
        form_layout = QFormLayout()
        
        # Temperature
        self.temperature_slider = QSlider(Qt.Orientation.Horizontal)
        self.temperature_slider.setRange(0, 200)  # 0.0 to 2.0
        self.temperature_slider.setValue(70)  # 0.7 default
        self.temperature_slider.valueChanged.connect(self.on_parameter_changed)
        
        self.temperature_label = QLabel("0.7")
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(self.temperature_slider)
        temp_layout.addWidget(self.temperature_label)
        
        form_layout.addRow("Temperature:", temp_layout)
        
        # Max Tokens
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 4096)
        self.max_tokens_spin.setValue(1000)
        self.max_tokens_spin.valueChanged.connect(self.on_parameter_changed)
        
        form_layout.addRow("Max Tokens:", self.max_tokens_spin)
        
        # Top P
        self.top_p_slider = QSlider(Qt.Orientation.Horizontal)
        self.top_p_slider.setRange(0, 100)
        self.top_p_slider.setValue(90)  # 0.9 default
        self.top_p_slider.valueChanged.connect(self.on_parameter_changed)
        
        self.top_p_label = QLabel("0.9")
        top_p_layout = QHBoxLayout()
        top_p_layout.addWidget(self.top_p_slider)
        top_p_layout.addWidget(self.top_p_label)
        
        form_layout.addRow("Top P:", top_p_layout)
        
        # Frequency Penalty
        self.freq_penalty_slider = QSlider(Qt.Orientation.Horizontal)
        self.freq_penalty_slider.setRange(0, 200)
        self.freq_penalty_slider.setValue(0)
        self.freq_penalty_slider.valueChanged.connect(self.on_parameter_changed)
        
        self.freq_penalty_label = QLabel("0.0")
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(self.freq_penalty_slider)
        freq_layout.addWidget(self.freq_penalty_label)
        
        form_layout.addRow("Frequency Penalty:", freq_layout)
        
        layout.addLayout(form_layout)
        
        # פרסטים
        presets_group = QGroupBox("Presets")
        presets_layout = QHBoxLayout(presets_group)
        
        self.creative_button = QPushButton("Creative")
        self.creative_button.clicked.connect(lambda: self.load_preset("creative"))
        
        self.balanced_button = QPushButton("Balanced")
        self.balanced_button.clicked.connect(lambda: self.load_preset("balanced"))
        
        self.precise_button = QPushButton("Precise")
        self.precise_button.clicked.connect(lambda: self.load_preset("precise"))
        
        self.save_preset_button = QPushButton("Save Preset")
        self.save_preset_button.clicked.connect(self.save_custom_preset)
        
        presets_layout.addWidget(self.creative_button)
        presets_layout.addWidget(self.balanced_button)
        presets_layout.addWidget(self.precise_button)
        presets_layout.addStretch()
        presets_layout.addWidget(self.save_preset_button)
        
        layout.addWidget(presets_group)
        
        # תצוגה מקדימה
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(100)
        self.preview_text.setPlaceholderText("Parameter changes will affect AI responses...")
        
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        layout.addStretch()
    
    def on_parameter_changed(self):
        """טיפול בשינוי פרמטר"""
        # עדכון תוויות
        self.temperature_label.setText(f"{self.temperature_slider.value() / 100:.1f}")
        self.top_p_label.setText(f"{self.top_p_slider.value() / 100:.1f}")
        self.freq_penalty_label.setText(f"{self.freq_penalty_slider.value() / 100:.1f}")
        
        # שליחת אות שינוי
        params = self.get_current_parameters()
        self.parameters_changed.emit(params)
        
        # עדכון תצוגה מקדימה
        self.update_preview()
    
    def get_current_parameters(self):
        """קבלת פרמטרים נוכחיים"""
        return {
            "temperature": self.temperature_slider.value() / 100,
            "max_tokens": self.max_tokens_spin.value(),
            "top_p": self.top_p_slider.value() / 100,
            "frequency_penalty": self.freq_penalty_slider.value() / 100
        }
    
    def load_preset(self, preset_name):
        """טעינת פרסט"""
        presets = {
            "creative": {"temperature": 90, "max_tokens": 1500, "top_p": 95, "frequency_penalty": 30},
            "balanced": {"temperature": 70, "max_tokens": 1000, "top_p": 90, "frequency_penalty": 0},
            "precise": {"temperature": 30, "max_tokens": 800, "top_p": 80, "frequency_penalty": 0}
        }
        
        if preset_name in presets:
            preset = presets[preset_name]
            self.temperature_slider.setValue(preset["temperature"])
            self.max_tokens_spin.setValue(preset["max_tokens"])
            self.top_p_slider.setValue(preset["top_p"])
            self.freq_penalty_slider.setValue(preset["frequency_penalty"])
    
    def update_preview(self):
        """עדכון תצוגה מקדימה"""
        params = self.get_current_parameters()
        
        if params["temperature"] > 0.8:
            style = "Creative and varied responses"
        elif params["temperature"] < 0.4:
            style = "Focused and consistent responses"
        else:
            style = "Balanced responses"
        
        preview_text = f"Style: {style}\nMax length: {params['max_tokens']} tokens"
        self.preview_text.setPlainText(preview_text)
```

### UsageMonitor Component

```python
class UsageMonitor(QWidget):
    """מוניטור שימוש ב-LLM"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # לייאאוט
        layout = QVBoxLayout(self)
        
        # כותרת
        title = QLabel("Usage Statistics")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)
        
        # סטטיסטיקות כלליות
        stats_layout = QHBoxLayout()
        
        # כרטיסי סטטיסטיקה
        self.tokens_card = self.create_stat_card("Tokens Used", "12,345", "📊")
        self.calls_card = self.create_stat_card("API Calls", "234", "📞")
        self.cost_card = self.create_stat_card("Estimated Cost", "$5.67", "💰")
        self.errors_card = self.create_stat_card("Errors", "2", "⚠️")
        
        stats_layout.addWidget(self.tokens_card)
        stats_layout.addWidget(self.calls_card)
        stats_layout.addWidget(self.cost_card)
        stats_layout.addWidget(self.errors_card)
        
        layout.addLayout(stats_layout)
        
        # גרפים
        charts_layout = QHBoxLayout()
        
        # גרף שימוש לאורך זמן
        self.usage_chart = self.create_usage_chart()
        charts_layout.addWidget(self.usage_chart)
        
        # גרף התפלגות מודלים
        self.models_chart = self.create_models_chart()
        charts_layout.addWidget(self.models_chart)
        
        layout.addLayout(charts_layout)
        
        # טבלת היסטוריה
        history_group = QGroupBox("Usage History")
        history_layout = QVBoxLayout(history_group)
        
        # פילטרים
        filters_layout = QHBoxLayout()
        
        date_label = QLabel("Date Range:")
        self.date_from = QDateEdit()
        self.date_to = QDateEdit()
        
        model_label = QLabel("Model:")
        self.model_filter = QComboBox()
        self.model_filter.addItems(["All Models", "GPT-4", "GPT-3.5-turbo", "Claude-3"])
        
        filters_layout.addWidget(date_label)
        filters_layout.addWidget(self.date_from)
        filters_layout.addWidget(QLabel("to"))
        filters_layout.addWidget(self.date_to)
        filters_layout.addWidget(model_label)
        filters_layout.addWidget(self.model_filter)
        filters_layout.addStretch()
        
        history_layout.addLayout(filters_layout)
        
        # טבלה
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Date", "Model", "Tokens", "Cost", "Response Time", "Status"
        ])
        
        history_layout.addWidget(self.history_table)
        
        layout.addWidget(history_group)
    
    def create_stat_card(self, title, value, icon):
        """יצירת כרטיס סטטיסטיקה"""
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
        value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
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
    
    def create_usage_chart(self):
        """יצירת גרף שימוש"""
        # כאן יהיה גרף אמיתי, לעת עתה placeholder
        chart_widget = QLabel("📈 Usage Chart\n(Chart implementation here)")
        chart_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_widget.setStyleSheet("""
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            min-height: 200px;
        """)
        return chart_widget
    
    def create_models_chart(self):
        """יצירת גרף מודלים"""
        # כאן יהיה גרף אמיתי, לעת עתה placeholder
        chart_widget = QLabel("🥧 Models Distribution\n(Pie chart here)")
        chart_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_widget.setStyleSheet("""
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
            min-height: 200px;
        """)
        return chart_widget
```

## Data Models

### LLMProvider Model

```python
@dataclass
class LLMProvider:
    """מודל ספק LLM"""
    name: str
    api_base_url: str
    supported_models: List[str]
    api_key: Optional[str] = None
    is_connected: bool = False
    connection_status: str = "disconnected"
    last_test_date: Optional[datetime] = None
    
    def test_connection(self) -> bool:
        """בדיקת חיבור לספק"""
        # כאן תהיה לוגיקת בדיקת חיבור אמיתית
        return self.api_key is not None
```

### LLMModel Model

```python
@dataclass
class LLMModel:
    """מודל LLM"""
    id: str
    name: str
    provider: str
    description: str
    max_tokens: int
    cost_per_token: float
    capabilities: List[str]
    is_active: bool = False
    
    @property
    def display_name(self) -> str:
        return f"{self.provider} - {self.name}"
```

### UsageRecord Model

```python
@dataclass
class UsageRecord:
    """רשומת שימוש"""
    timestamp: datetime
    model_id: str
    tokens_used: int
    cost: float
    response_time: float
    success: bool
    error_message: Optional[str] = None
```

## Error Handling

### Error Scenarios

1. **שגיאת חיבור API**
   - הצגת הודעת שגיאה ברורה
   - הצעת פתרונות (בדיקת API key, חיבור אינטרנט)
   - אפשרות לנסות שוב

2. **שגיאת אימות**
   - הודעה על API key לא תקין
   - הפניה להגדרות חשבון הספק
   - אפשרות לעדכן credentials

3. **שגיאת מכסה**
   - התראה על חריגה ממכסה
   - הצגת שימוש נוכחי ומגבלות
   - הצעת חלופות

## Testing Strategy

### Unit Tests

1. **בדיקות רכיבי UI**
   - טעינת נתונים
   - אינטראקציות משתמש
   - עדכון תצוגה

2. **בדיקות שירותים**
   - חיבור לספקים
   - שליחת בקשות
   - עיבוד תגובות

### Integration Tests

1. **שילוב עם ספקי API**
   - בדיקת חיבורים אמיתיים
   - טיפול בשגיאות
   - מדידת ביצועים

2. **שילוב עם מסד נתונים**
   - שמירת הגדרות
   - שליפת סטטיסטיקות
   - גיבוי ושחזור