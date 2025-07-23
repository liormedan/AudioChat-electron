from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QSplitter, QFrame, QLineEdit, QPushButton)
from PyQt6.QtCore import Qt


class AudioExportPage(QWidget):
    """דף ניהול ייצואים"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("audioExportPage")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Toolbar
        toolbar = self._create_toolbar()
        self.main_layout.addWidget(toolbar)

        # Main content area
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # Left panel for the list of exports
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.Shape.StyledPanel)
        self.splitter.addWidget(left_panel)

        # Right panel for the export details
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.Shape.StyledPanel)
        self.splitter.addWidget(right_panel)

        self.splitter.setSizes([300, 700])

    def _create_toolbar(self):
        """Creates the toolbar for the page."""
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 10, 10, 10)
        toolbar_layout.setSpacing(10)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search exports...")
        toolbar_layout.addWidget(self.search_bar)

        # New Export button
        self.new_export_button = QPushButton("New Export")
        toolbar_layout.addWidget(self.new_export_button)

        # Connect signals
        self.search_bar.textChanged.connect(self.on_search_text_changed)
        self.new_export_button.clicked.connect(self.on_new_export_clicked)

        return toolbar

    def on_search_text_changed(self, text):
        """Handles the text changed signal from the search bar."""
        print(f"Search text: {text}")

    def on_new_export_clicked(self):
        """Handles the clicked signal from the new export button."""
        print("New export button clicked")
