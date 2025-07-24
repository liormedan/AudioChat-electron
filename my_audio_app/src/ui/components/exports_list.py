from PyQt5.QtWidgets import QTableView, QWidget, QVBoxLayout, QLabel, QHeaderView, QAbstractItemView
from PyQt5.QtCore import QAbstractTableModel, Qt, QSortFilterProxyModel, pyqtSignal
from PyQt5.QtGui import QFont

class ExportsListModel(QAbstractTableModel):
    def __init__(self, data=[], parent=None):
        super().__init__(parent)
        self._data = data
        self._headers = ["Name", "Format", "Duration", "Size", "Date", "Status"]

    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        return len(self._headers)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        if role == Qt.SortRole:
            return self._data[section][orientation]
        return None

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        self._data.sort(key=lambda x: x[column])
        if order == Qt.DescendingOrder:
            self._data.reverse()
        self.layoutChanged.emit()

    def update_data(self, new_data):
        self.beginResetModel()
        self._data = new_data
        self.endResetModel()

class ExportsList(QWidget):
    export_selected = pyqtSignal(list) # Emits a list of selected export data

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.empty_state_label = QLabel("No exports available. Start by exporting an audio file!")
        self.empty_state_label.setAlignment(Qt.AlignCenter)
        self.empty_state_label.setFont(QFont("Arial", 12))
        self.empty_state_label.setStyleSheet("color: #888;")
        self.layout.addWidget(self.empty_state_label)

        self.table_view = QTableView()
        self.model = ExportsListModel()
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.table_view.setModel(self.proxy_model)

        self.table_view.setSortingEnabled(True)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.clicked.connect(self._on_table_clicked)

        self.layout.addWidget(self.table_view)
        self.setLayout(self.layout)

        self._update_visibility()

    def _on_table_clicked(self, index):
        selected_rows = self.table_view.selectionModel().selectedRows()
        selected_exports = []
        for row_index in selected_rows:
            source_index = self.proxy_model.mapToSource(row_index)
            export_data = self.model._data[source_index.row()]
            selected_exports.append(export_data)
        self.export_selected.emit(selected_exports)

    def update_exports(self, exports_data):
        self.model.update_data(exports_data)
        self._update_visibility()

    def _update_visibility(self):
        if self.model.rowCount(None) == 0:
            self.table_view.hide()
            self.empty_state_label.show()
        else:
            self.table_view.show()
            self.empty_state_label.hide()
