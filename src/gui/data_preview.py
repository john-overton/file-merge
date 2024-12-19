from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableView, QHeaderView
from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
import pandas as pd
import numpy as np

class PandasTableModel(QAbstractTableModel):
    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self._data = data

    def rowCount(self, parent=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, parent=QModelIndex()):
        return self._data.shape[1]

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            
            # Handle different data types
            if pd.isna(value):
                return ''
            elif isinstance(value, (float, np.floating)):
                return f"{value:.2f}"
            elif isinstance(value, (pd.Timestamp, np.datetime64)):
                return value.strftime('%Y-%m-%d %H:%M:%S')
            else:
                return str(value)

        elif role == Qt.ItemDataRole.BackgroundRole:
            value = self._data.iloc[index.row(), index.column()]
            if pd.isna(value):
                return Qt.GlobalColor.lightGray

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])
            else:
                return str(section + 1)
        return None

class DataPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create table view
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.verticalHeader().setVisible(True)
        
        layout.addWidget(self.table_view)
        
    def set_data(self, df: pd.DataFrame):
        model = PandasTableModel(df)
        self.table_view.setModel(model)
        
    def clear(self):
        self.table_view.setModel(None)
