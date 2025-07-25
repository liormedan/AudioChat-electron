# LLM Manager Page
import sys
from typing import Dict, Any, Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, 
    QFrame, QPushButton, QMessageBox, QApplication, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from app_context import settings_service, llm_service
from services.usage_service import UsageService
from models.llm_models import LLMParameters

# Import full implementations of the LLM management widgets
from ..components.llm import (
    ProviderCard,
    ModelSelector,
    ModelDetailsWidget,
    ParameterEditor,
    ModelTester,
)
from ..components.llm.usage_monitor import UsageMonitor

class LLMManagerPage(QWidget):
    """דף ניהול מודלי LLM"""
    
    # Signals
    model_changed = pyqtSignal(str)
    settings_changed = pyqtSignal(dict)
    provider_connected = pyqtSignal(str, bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("llmManagerPage")

        self.settings_service = settings_service
        self.llm_service = llm_service
        self.usage_service = UsageService()
        
        # State management
        self.current_provider = None
        self.current_model = None
        self.current_parameters = {}
        self.providers_data = {}
        
        # Initialize UI
        self._setup_ui()
        self._setup_connections()
        self._load_initial_data()
        self._apply_styling()
        QTimer.singleShot(100, self._show_welcome_if_needed)
    
    def _setup_ui(self):
        """הגדרת ממשק המשתמש"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Page header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # Create tabs
        self._create_providers_tab()
        self._create_models_tab()
        self._create_settings_tab()
        self._create_usage_tab()
        self._create_testing_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        status_bar = self._create_status_bar()
        main_layout.addWidget(status_bar)
    
    def _create_header(self):
        """יצירת כותרת הדף"""
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title = QLabel("🤖 LLM Manager")
        title.setObjectName("pageTitle")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        
        # Subtitle
        subtitle = QLabel("Manage AI models, settings, and usage")
        subtitle.setObjectName("pageSubtitle")
        subtitle.setStyleSheet("color: #888; font-size: 14px;")
        
        # Title layout
        title_layout = QVBoxLayout()
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        title_layout.setSpacing(5)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self._refresh_data)
        
        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.clicked.connect(self._open_global_settings)
        
        actions_layout.addWidget(self.refresh_button)
        actions_layout.addWidget(self.settings_button)
        
        header_layout.addLayout(actions_layout)
        
        return header_frame
    
    def _create_providers_tab(self):
        """יצירת טאב ספקי LLM"""
        providers_widget = QWidget()
        providers_layout = QVBoxLayout(providers_widget)
        providers_layout.setSpacing(20)
        
        # Tab header
        tab_header = QLabel("🏢 LLM Providers")
        tab_header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        providers_layout.addWidget(tab_header)
        
        # Description
        description = QLabel("Connect and manage different AI service providers")
        description.setStyleSheet("color: #888; margin-bottom: 20px;")
        providers_layout.addWidget(description)
        
        # Providers grid container
        providers_scroll_area = self._create_providers_grid()
        providers_layout.addWidget(providers_scroll_area)
        
        # Add tab
        self.tab_widget.addTab(providers_widget, "🏢 Providers")
    
    def _create_providers_grid(self):
        """יצירת רשת כרטיסי ספקים"""
        # Scroll area for providers
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        # Handle different PyQt6 versions
        try:
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        except AttributeError:
            try:
                scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            except AttributeError:
                # Use numeric values as fallback
                scroll_area.setHorizontalScrollBarPolicy(1)  # ScrollBarAlwaysOff = 1
                scroll_area.setVerticalScrollBarPolicy(0)  # ScrollBarAsNeeded = 0
        
        # Container widget
        container = QWidget()
        grid_layout = QGridLayout(container)
        grid_layout.setSpacing(20)
        
        # Load providers from the service
        providers = self.llm_service.get_all_providers()

        # Create provider cards
        self.provider_cards = {}
        for i, provider in enumerate(providers):
            card = ProviderCard(provider, self.llm_service)
            card.connection_changed.connect(self._on_provider_connection_changed)

            # Store reference
            self.provider_cards[provider.name] = card
            
            # Add to grid (2 columns)
            row = i // 2
            col = i % 2
            grid_layout.addWidget(card, row, col)
        
        # Add stretch to push cards to top
        grid_layout.setRowStretch(grid_layout.rowCount(), 1)
        
        scroll_area.setWidget(container)
        return scroll_area
    
    def _create_models_tab(self):
        """יצירת טאב מודלים"""
        models_widget = QWidget()
        models_layout = QHBoxLayout(models_widget)
        models_layout.setSpacing(20)
        
        # Left panel - Model selector
        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_panel.setFixedWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        # Model selector header
        selector_header = QLabel("🤖 Available Models")
        selector_header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        left_layout.addWidget(selector_header)
        
        # Model selector
        self.model_selector = ModelSelector(self.llm_service)
        self.model_selector.model_selected.connect(self._on_model_selected)
        left_layout.addWidget(self.model_selector)
        
        models_layout.addWidget(left_panel)
        
        # Right panel - Model details
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        
        # Model details header
        details_header = QLabel("📋 Model Details")
        details_header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        right_layout.addWidget(details_header)
        
        # Model details
        self.model_details = ModelDetailsWidget(self.llm_service)
        right_layout.addWidget(self.model_details)
        
        models_layout.addWidget(right_panel)
        
        # Add tab
        self.tab_widget.addTab(models_widget, "🤖 Models")
    
    def _create_settings_tab(self):
        """יצירת טאב הגדרות"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setSpacing(20)
        
        # Tab header
        tab_header = QLabel("⚙️ Model Parameters")
        tab_header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        settings_layout.addWidget(tab_header)
        
        # Description
        description = QLabel("Configure model parameters and behavior settings")
        description.setStyleSheet("color: #888; margin-bottom: 20px;")
        settings_layout.addWidget(description)
        
        # Parameter editor
        self.parameter_editor = ParameterEditor(self)
        self.parameter_editor.parameters_changed.connect(self._on_parameters_changed)
        settings_layout.addWidget(self.parameter_editor)
        
        # Add tab
        self.tab_widget.addTab(settings_widget, "⚙️ Settings")
    
    def _create_usage_tab(self):
        """יצירת טאב שימוש"""
        usage_widget = QWidget()
        usage_layout = QVBoxLayout(usage_widget)
        usage_layout.setSpacing(20)
        
        # Tab header
        tab_header = QLabel("📊 Usage Analytics")
        tab_header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        usage_layout.addWidget(tab_header)
        
        # Description
        description = QLabel("Monitor usage, costs, and performance metrics")
        description.setStyleSheet("color: #888; margin-bottom: 20px;")
        usage_layout.addWidget(description)
        
        # Usage monitor
        self.usage_monitor = UsageMonitor(self.usage_service, self)
        usage_layout.addWidget(self.usage_monitor)
        
        # Add tab
        self.tab_widget.addTab(usage_widget, "📊 Usage")
    
    def _create_testing_tab(self):
        """יצירת טאב בדיקות"""
        testing_widget = QWidget()
        testing_layout = QVBoxLayout(testing_widget)
        testing_layout.setSpacing(20)
        
        # Tab header
        tab_header = QLabel("🧪 Model Testing")
        tab_header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        testing_layout.addWidget(tab_header)
        
        # Description
        description = QLabel("Test and compare different models with custom prompts")
        description.setStyleSheet("color: #888; margin-bottom: 20px;")
        testing_layout.addWidget(description)
        
        # Model tester
        self.model_tester = ModelTester(self)
        testing_layout.addWidget(self.model_tester)
        
        # Add tab
        self.tab_widget.addTab(testing_widget, "🧪 Testing")
    
    def _create_status_bar(self):
        """יצירת שורת סטטוס"""
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_layout = QHBoxLayout(status_frame)
        
        # Status indicators
        self.connection_status = QLabel("🔴 Disconnected")
        self.connection_status.setStyleSheet("color: #F44336;")
        
        self.model_status = QLabel("No model selected")
        self.model_status.setStyleSheet("color: #888;")
        
        status_layout.addWidget(QLabel("Status:"))
        status_layout.addWidget(self.connection_status)
        status_layout.addWidget(QLabel("|"))
        status_layout.addWidget(self.model_status)
        status_layout.addStretch()
        
        # Last updated
        self.last_updated = QLabel("Last updated: Never")
        self.last_updated.setStyleSheet("color: #888; font-size: 12px;")
        status_layout.addWidget(self.last_updated)
        
        return status_frame
    
    def _setup_connections(self):
        """הגדרת חיבורי אותות"""
        # Tab change handling
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._auto_refresh)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def _load_initial_data(self):
        """טעינת נתונים ראשוניים"""
        try:
            # Load saved settings
            self._load_settings()

            # Load provider states
            self._load_provider_states()

            active = self.llm_service.get_active_model()
            if active:
                self.current_model = active.id
                self._update_model_status()

            # Update status
            self._update_status()
            
        except Exception as e:
            print(f"Error loading initial data: {e}")
    
    def _apply_styling(self):
        """החלת עיצוב"""
        self.setStyleSheet("""
            QWidget#llmManagerPage {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            
            QFrame#headerFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 10px;
            }
            
            QLabel#pageTitle {
                color: #ffffff;
                font-weight: bold;
            }
            
            QLabel#pageSubtitle {
                color: #888888;
            }
            
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #1e1e1e;
                border-radius: 5px;
            }
            
            QTabWidget::tab-bar {
                alignment: center;
            }
            
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                min-width: 120px;
            }
            
            QTabBar::tab:selected {
                background-color: #3d3d3d;
                border-bottom: 2px solid #4CAF50;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #353535;
            }
            
            QFrame#leftPanel, QFrame#rightPanel {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 15px;
            }
            
            QFrame#statusFrame {
                background-color: #2d2d2d;
                border-radius: 5px;
                padding: 8px 15px;
                margin-top: 10px;
            }
            
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #4d4d4d;
                border-color: #666;
            }
            
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
        """)
    
    # Event handlers
    def _on_provider_connection_changed(self, provider_name: str, connected: bool):
        """טיפול בשינוי חיבור ספק"""
        print(f"Provider {provider_name} connection changed: {connected}")
        
        # Update provider state
        if provider_name in self.providers_data:
            self.providers_data[provider_name]["connected"] = connected
        
        # Update UI
        self._update_connection_status()
        
        # Emit signal
        self.provider_connected.emit(provider_name, connected)
    
    def _on_model_selected(self, model_id: str):
        """טיפול בבחירת מודל"""
        print(f"Model selected: {model_id}")

        self.current_model = model_id
        try:
            self.llm_service.set_active_model(model_id)
        except Exception as e:
            print(f"Error activating model {model_id}: {e}")

        # Update model details
        if hasattr(self, 'model_details'):
            if hasattr(self.model_details, 'show_model_details'):
                self.model_details.show_model_details(model_id)
        
        # Update status
        self._update_model_status()
        
        # Emit signal
        self.model_changed.emit(model_id)
    
    def _on_parameters_changed(self, parameters: Dict[str, Any]):
        """טיפול בשינוי פרמטרים"""
        print(f"Parameters changed: {parameters}")

        self.current_parameters = parameters

        # Save settings
        self._save_settings()
        try:
            params = LLMParameters.from_dict(parameters)
            self.llm_service.set_parameters(params)
        except Exception as e:
            print(f"Error applying parameters: {e}")
        
        # Emit signal
        self.settings_changed.emit(parameters)
    
    def _on_tab_changed(self, index: int):
        """טיפול בשינוי טאב"""
        tab_names = ["Providers", "Models", "Settings", "Usage", "Testing"]
        if 0 <= index < len(tab_names):
            print(f"Switched to tab: {tab_names[index]}")
            
            # Refresh data for specific tabs
            if index == 3:  # Usage tab
                self._refresh_usage_data()
            elif index == 4:  # Testing tab
                self._refresh_testing_data()
    
    # Data management methods
    def _load_settings(self):
        """טעינת הגדרות"""
        # Try loading from the SettingsService first
        params_dict = self.settings_service.get_setting("llm_parameters")
        params_obj = None

        if isinstance(params_dict, dict):
            try:
                params_obj = LLMParameters.from_dict(params_dict)
            except Exception:
                params_obj = None

        if not params_obj:
            # Fallback to values stored in the LLMService
            params_obj = self.llm_service.get_parameters()
            if isinstance(params_obj, LLMParameters):
                params_dict = params_obj.to_dict()
            else:
                params_obj = LLMParameters()
                params_dict = params_obj.to_dict()

        self.current_parameters = params_dict

        # ensure services hold the same parameters
        try:
            self.llm_service.set_parameters(params_obj)
        except Exception:
            pass

        if hasattr(self, "parameter_editor") and hasattr(
            self.parameter_editor, "set_parameters"
        ):
            self.parameter_editor.set_parameters(params_obj)
    
    def _save_settings(self):
        """שמירת הגדרות"""
        try:
            params = LLMParameters.from_dict(self.current_parameters)
            # Persist via both services
            self.llm_service.set_parameters(params)
            self.settings_service.set_setting("llm_parameters", self.current_parameters)
            print("Settings saved")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def _load_provider_states(self):
        """טעינת מצבי ספקים"""
        self.providers_data = {}
        for provider in self.llm_service.get_all_providers():
            api_key = provider.api_key or self.llm_service.get_provider_api_key(provider.name)
            self.providers_data[provider.name] = {
                "connected": provider.is_connected,
                "api_key": api_key,
            }
    
    def _refresh_data(self):
        """רענון כל הנתונים"""
        print("Refreshing all data...")
        
        try:
            # Update status
            self._update_status()
            
            # Update last updated time
            from datetime import datetime
            self.last_updated.setText(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            print(f"Error refreshing data: {e}")
    
    def _refresh_usage_data(self):
        """רענון נתוני שימוש"""
        if not hasattr(self, 'usage_monitor'):
            return

        try:
            summary = self.usage_service.get_usage_summary()

            if hasattr(self.usage_monitor, 'tokens_card'):
                self.usage_monitor.tokens_card.update_value(
                    f"{summary['total_tokens']:,}"
                )
            if hasattr(self.usage_monitor, 'calls_card'):
                self.usage_monitor.calls_card.update_value(
                    f"{summary['total_requests']:,}"
                )
            if hasattr(self.usage_monitor, 'cost_card'):
                self.usage_monitor.cost_card.update_value(
                    f"${summary['total_cost']:.2f}"
                )
            if hasattr(self.usage_monitor, 'errors_card'):
                errors = int(summary['total_requests'] * (1 - summary['success_rate']))
                self.usage_monitor.errors_card.update_value(str(errors))

            if hasattr(self.usage_monitor, 'avg_response_time_label'):
                self.usage_monitor.avg_response_time_label.setText(
                    f"{summary['avg_response_time']:.2f}s"
                )
            if hasattr(self.usage_monitor, 'success_rate_label'):
                self.usage_monitor.success_rate_label.setText(
                    f"{summary['success_rate'] * 100:.1f}%"
                )
            if hasattr(self.usage_monitor, 'active_providers_label'):
                self.usage_monitor.active_providers_label.setText(
                    str(summary['unique_providers'])
                )
            if hasattr(self.usage_monitor, 'active_models_label'):
                self.usage_monitor.active_models_label.setText(
                    str(summary['unique_models'])
                )

            # Fallback for placeholder widget with a single label
            if isinstance(self.usage_monitor, QWidget) and not hasattr(self.usage_monitor, 'tokens_card'):
                label = self.usage_monitor.findChild(QLabel)
                if label:
                    label.setText(
                        f"Requests: {summary['total_requests']}  |  Tokens: {summary['total_tokens']}  |  Cost: ${summary['total_cost']:.2f}"
                    )
        except Exception as e:
            print(f"Error refreshing usage data: {e}")

    def _refresh_testing_data(self):
        """רענון נתוני בדיקות"""
        if not hasattr(self, 'model_tester'):
            return

        try:
            if hasattr(self.model_tester, 'refresh_history'):
                self.model_tester.refresh_history()
            else:
                if hasattr(self.model_tester, 'update_history_table'):
                    self.model_tester.update_history_table()
                if hasattr(self.model_tester, 'update_performance_metrics'):
                    self.model_tester.update_performance_metrics()
        except Exception as e:
            print(f"Error refreshing testing data: {e}")
    
    def _auto_refresh(self):
        """רענון אוטומטי"""
        # Only refresh if page is visible
        if self.isVisible():
            self._refresh_usage_data()
    
    # Status update methods
    def _update_status(self):
        """עדכון סטטוס כללי"""
        self._update_connection_status()
        self._update_model_status()
    
    def _update_connection_status(self):
        """עדכון סטטוס חיבור"""
        connected_providers = [
            name for name, data in self.providers_data.items() 
            if data.get("connected", False)
        ]
        
        if connected_providers:
            self.connection_status.setText(f"🟢 Connected ({len(connected_providers)} providers)")
            self.connection_status.setStyleSheet("color: #4CAF50;")
        else:
            self.connection_status.setText("🔴 Disconnected")
            self.connection_status.setStyleSheet("color: #F44336;")
    
    def _update_model_status(self):
        """עדכון סטטוס מודל"""
        if self.current_model:
            self.model_status.setText(f"Active: {self.current_model}")
            self.model_status.setStyleSheet("color: #4CAF50;")
        else:
            self.model_status.setText("No model selected")
            self.model_status.setStyleSheet("color: #888;")
    
    # Action methods
    def _open_global_settings(self):
        """פתיחת הגדרות כלליות"""
        QMessageBox.information(self, "Settings", "Global settings dialog would open here")
    
    # Public interface methods
    def get_current_model(self) -> Optional[str]:
        """קבלת המודל הנוכחי"""
        return self.current_model
    
    def get_current_parameters(self) -> Dict[str, Any]:
        """קבלת הפרמטרים הנוכחיים"""
        return self.current_parameters.copy()
    
    def get_connected_providers(self) -> List[str]:
        """קבלת רשימת ספקים מחוברים"""
        return [
            name for name, data in self.providers_data.items()
            if data.get("connected", False)
        ]
    
    def set_active_model(self, model_id: str):
        """הגדרת מודל פעיל"""
        self.current_model = model_id
        self._update_model_status()
        self.model_changed.emit(model_id)
    
    def connect_provider(self, provider_name: str, api_key: str) -> bool:
        """חיבור ספק"""
        try:
            # Save API key securely via the service
            saved = self.llm_service.set_provider_api_key(provider_name, api_key)
            if not saved:
                return False

            # Test the connection with the stored key
            success, _msg, _time = self.llm_service.test_provider_connection_secure(
                provider_name
            )

            # Update internal state
            self.providers_data[provider_name] = {
                "connected": success,
                "api_key": api_key,
            }
            self._update_connection_status()
            # Emit change notification
            self.provider_connected.emit(provider_name, success)
            return success
        except Exception as e:
            print(f"Error connecting provider {provider_name}: {e}")
            return False
    
    def disconnect_provider(self, provider_name: str):
        """ניתוק ספק"""
        if provider_name in self.providers_data:
            self.providers_data[provider_name]["connected"] = False
            self.providers_data[provider_name]["api_key"] = None
            self._update_connection_status()

    def _show_welcome_if_needed(self):
        """Display welcome message on first setup"""
        first_run = not self.settings_service.get_setting("llm_setup_complete", False)
        if first_run:
            QMessageBox.information(
                self,
                "Welcome",
                "Welcome to the LLM Manager! Configure a provider to start using AI features."
            )
            self.settings_service.set_setting("llm_setup_complete", True)


# Demo/Testing function
def main():
    """פונקציית הדגמה"""
    app = QApplication(sys.argv)
    
    # Create and show the LLM Manager page
    page = LLMManagerPage()
    page.setWindowTitle("LLM Manager - Demo")
    page.resize(1200, 800)
    page.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
