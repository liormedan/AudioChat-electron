import unittest
from PyQt5.QtWidgets import QApplication
from my_audio_app.src.ui.components.exports_list import ExportsList, ExportsListModel

class TestExportsList(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def test_exports_list_initialization(self):
        exports_list = ExportsList()
        self.assertIsInstance(exports_list, ExportsList)
        self.assertIsNotNone(exports_list.table_view)
        self.assertIsNotNone(exports_list.model)

    def test_exports_list_model_data(self):
        test_data = [
            ["Export1", "MP3", "00:01:30", "1.5 MB", "2023-01-01", "Completed"],
            ["Export2", "WAV", "00:05:00", "5.0 MB", "2023-01-02", "Failed"]
        ]
        model = ExportsListModel(test_data)
        self.assertEqual(model.rowCount(None), 2)
        self.assertEqual(model.columnCount(None), 6)
        self.assertEqual(model.data(model.index(0, 0), 0), "Export1")
        self.assertEqual(model.data(model.index(1, 1), 0), "WAV")

    def test_exports_list_model_headers(self):
        model = ExportsListModel()
        self.assertEqual(model.headerData(0, Qt.Horizontal, 0), "Name")
        self.assertEqual(model.headerData(5, Qt.Horizontal, 0), "Status")

    @classmethod
    def tearDownClass(cls):
        cls.app = None

if __name__ == '__main__':
    unittest.main()
