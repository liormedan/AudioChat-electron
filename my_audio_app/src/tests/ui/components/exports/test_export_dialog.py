import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from ui.components.exports.export_dialog import ExportDialog
from ui.components.file_upload.file_info import FileInfo
from datetime import datetime


@pytest.fixture
def app():
    """Create a QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # No need to clean up as we're not calling app.exec()


@pytest.fixture
def mock_file_service():
    """Create a mock FileService"""
    mock = MagicMock()
    
    # Mock recent files
    file1 = FileInfo(
        name="test1.mp3",
        path="/path/to/test1.mp3",
        size=1024 * 1024,
        format="mp3",
        duration=180,
        upload_date=datetime.now()
    )
    
    file2 = FileInfo(
        name="test2.wav",
        path="/path/to/test2.wav",
        size=2 * 1024 * 1024,
        format="wav",
        duration=240,
        upload_date=datetime.now()
    )
    
    mock.get_recent_files.return_value = [file1, file2]
    return mock


@pytest.fixture
def mock_export_service():
    """Create a mock ExportService"""
    mock = MagicMock()
    mock.get_export_formats.return_value = ["mp3", "wav", "flac", "ogg", "m4a", "aac"]
    return mock


@pytest.fixture
def dialog(app, mock_file_service, mock_export_service):
    """Create an ExportDialog instance with mocked services"""
    with patch('ui.components.exports.export_dialog.FileService', return_value=mock_file_service):
        with patch('ui.components.exports.export_dialog.ExportService', return_value=mock_export_service):
            dialog = ExportDialog()
            yield dialog
            dialog.close()


def test_dialog_initialization(dialog):
    """Test that the dialog initializes correctly"""
    assert dialog.windowTitle() == "New Audio Export"
    assert dialog.source_combo.count() == 3  # "Select a file..." + 2 mock files
    assert dialog.format_combo.count() == 6  # 6 mock formats


def test_format_change_updates_quality_options(dialog):
    """Test that changing format updates quality options"""
    # Test MP3 format
    dialog.format_combo.setCurrentText("MP3")
    assert dialog.quality_combo.count() == 4
    assert "256 kbps" in dialog.quality_combo.currentText()
    
    # Test FLAC format
    dialog.format_combo.setCurrentText("FLAC")
    assert dialog.quality_combo.count() == 3
    assert "Level 5" in dialog.quality_combo.currentText()
    
    # Test WAV format
    dialog.format_combo.setCurrentText("WAV")
    assert dialog.quality_combo.count() == 3
    assert "16-bit" in dialog.quality_combo.currentText()


def test_source_selection_updates_info(dialog):
    """Test that selecting a source file updates the file info"""
    # Initially no file selected
    assert "No file selected" in dialog.file_info_label.text()
    
    # Select first file
    dialog.source_combo.setCurrentIndex(1)
    assert "MP3" in dialog.file_info_label.text()
    assert "1.0 MB" in dialog.file_info_label.text()
    assert "3:00" in dialog.file_info_label.text()
    assert dialog.name_edit.text() == "test1"
    
    # Select second file
    dialog.source_combo.setCurrentIndex(2)
    assert "WAV" in dialog.file_info_label.text()
    assert "2.0 MB" in dialog.file_info_label.text()
    assert "4:00" in dialog.file_info_label.text()
    assert dialog.name_edit.text() == "test2"


def test_validation_no_source_file(dialog, monkeypatch):
    """Test validation when no source file is selected"""
    # Mock QMessageBox.warning to avoid actual dialog
    mock_warning = MagicMock()
    monkeypatch.setattr('ui.components.exports.export_dialog.QMessageBox.warning', mock_warning)
    
    # No file selected
    dialog.source_combo.setCurrentIndex(0)
    dialog.name_edit.setText("Test Export")
    
    # Try to accept
    assert not dialog._validate_input()
    mock_warning.assert_called_once()
    assert "Missing Source File" in mock_warning.call_args[0][1]


def test_validation_no_export_name(dialog, monkeypatch):
    """Test validation when no export name is provided"""
    # Mock QMessageBox.warning to avoid actual dialog
    mock_warning = MagicMock()
    monkeypatch.setattr('ui.components.exports.export_dialog.QMessageBox.warning', mock_warning)
    
    # Select file but leave name empty
    dialog.source_combo.setCurrentIndex(1)
    dialog.name_edit.setText("")
    
    # Try to accept
    assert not dialog._validate_input()
    mock_warning.assert_called_once()
    assert "Missing Export Name" in mock_warning.call_args[0][1]


def test_validation_invalid_export_name(dialog, monkeypatch):
    """Test validation when export name contains invalid characters"""
    # Mock QMessageBox.warning to avoid actual dialog
    mock_warning = MagicMock()
    monkeypatch.setattr('ui.components.exports.export_dialog.QMessageBox.warning', mock_warning)
    
    # Select file but use invalid name
    dialog.source_combo.setCurrentIndex(1)
    dialog.name_edit.setText("Invalid/Name")
    
    # Try to accept
    assert not dialog._validate_input()
    mock_warning.assert_called_once()
    assert "Invalid Export Name" in mock_warning.call_args[0][1]


def test_create_export(dialog, mock_export_service, monkeypatch):
    """Test creating an export"""
    # Mock export creation
    mock_export = MagicMock()
    mock_export.id = "test-export-id"
    mock_export_service.create_export.return_value = mock_export
    
    # Mock dialog accept to avoid closing
    monkeypatch.setattr(dialog, 'accept', MagicMock())
    
    # Set up export signal spy
    signal_spy = MagicMock()
    dialog.export_created.connect(signal_spy)
    
    # Select file and set name
    dialog.source_combo.setCurrentIndex(1)
    dialog.name_edit.setText("Test Export")
    dialog.format_combo.setCurrentText("MP3")
    dialog.quality_combo.setCurrentText("320 kbps")
    dialog.normalize_check.setChecked(True)
    
    # Accept dialog
    dialog._on_accept()
    
    # Verify export was created with correct parameters
    mock_export_service.create_export.assert_called_once()
    args = mock_export_service.create_export.call_args[1]
    assert args["name"] == "Test Export"
    assert args["format"] == "mp3"
    assert args["settings"]["bitrate"] == "320 kbps"
    assert args["settings"]["normalize"] is True
    
    # Verify signal was emitted
    signal_spy.assert_called_once_with("test-export-id")
    
    # Verify dialog was accepted
    dialog.accept.assert_called_once()