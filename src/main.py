import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QSplitter, QPushButton, QLabel, 
                            QFileDialog, QTableView, QStatusBar, QTabWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import pandas as pd
from pathlib import Path
from .gui.data_preview import DataPreviewWidget
from .gui.rule_editor import RuleEditorWidget
from .data_model import DataTransformer

class DataTransformApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Transform & Match")
        self.setGeometry(100, 100, 1400, 800)
        
        # Initialize components
        self.source_data = {}
        self.transformed_data = None
        self.transformer = DataTransformer()
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Toolbar
        toolbar = QHBoxLayout()
        import_btn = QPushButton("Import Files")
        import_btn.clicked.connect(self.import_files)
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_data)
        apply_btn = QPushButton("Apply Rules")
        apply_btn.clicked.connect(self.apply_rules)
        
        toolbar.addWidget(import_btn)
        toolbar.addWidget(apply_btn)
        toolbar.addWidget(export_btn)
        toolbar.addStretch()
        
        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Data previews
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        # Tab widget for source files
        self.preview_tabs = QTabWidget()
        preview_layout.addWidget(self.preview_tabs)
        
        # Transformed data preview
        self.transformed_preview = DataPreviewWidget()
        preview_layout.addWidget(QLabel("Transformed Data"))
        preview_layout.addWidget(self.transformed_preview)
        
        content_splitter.addWidget(preview_widget)
        
        # Right side: Rule editor
        self.rule_editor = RuleEditorWidget()
        self.rule_editor.rule_updated.connect(self.on_rules_updated)
        content_splitter.addWidget(self.rule_editor)
        
        # Set initial splitter sizes
        content_splitter.setSizes([600, 400])
        
        # Add to main layout
        layout.addLayout(toolbar)
        layout.addWidget(content_splitter)
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def import_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Data Files",
            "",
            "Data Files (*.csv *.xlsx);;CSV Files (*.csv);;Excel Files (*.xlsx)"
        )
        if files:
            # Clear existing data
            self.source_data.clear()
            self.preview_tabs.clear()
            self.transformed_preview.clear()
            
            for file_path in files:
                try:
                    path = Path(file_path)
                    if path.suffix == '.csv':
                        df = pd.read_csv(file_path)
                    else:
                        df = pd.read_excel(file_path)
                    
                    self.source_data[path.name] = df
                    
                    # Create preview widget for the file
                    preview = DataPreviewWidget()
                    preview.set_data(df)
                    self.preview_tabs.addTab(preview, path.name)
                    
                    self.statusBar.showMessage(f"Imported: {path.name}")
                except Exception as e:
                    self.statusBar.showMessage(f"Error importing {path.name}: {str(e)}")
            
            # Update rule editor with columns from first two files
            if len(self.source_data) >= 2:
                source_dfs = list(self.source_data.values())
                self.rule_editor.update_columns(source_dfs[0], source_dfs[1])

    def apply_rules(self):
        if not self.source_data:
            self.statusBar.showMessage("No source data to transform")
            return
            
        try:
            # Apply match rules between first two datasets
            if len(self.source_data) >= 2:
                source_dfs = list(self.source_data.values())
                self.transformer.match_rules = self.rule_editor.match_rules
                matched_data = self.transformer.match_records(source_dfs[0], source_dfs[1])
                
                # Apply transformations
                self.transformer.transform_rules = self.rule_editor.transform_rules
                self.transformed_data = self.transformer.apply_transformations(matched_data)
                
                # Update preview
                self.transformed_preview.set_data(self.transformed_data)
                self.statusBar.showMessage("Rules applied successfully")
            else:
                self.statusBar.showMessage("Need at least 2 datasets for matching")
        except Exception as e:
            self.statusBar.showMessage(f"Error applying rules: {str(e)}")
    
    def export_data(self):
        if self.transformed_data is None or self.transformed_data.empty:
            self.statusBar.showMessage("No data to export")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Transformed Data",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )
        if file_path:
            try:
                path = Path(file_path)
                if path.suffix == '.csv':
                    self.transformed_data.to_csv(file_path, index=False)
                else:
                    self.transformed_data.to_excel(file_path, index=False)
                self.statusBar.showMessage(f"Data exported to: {path.name}")
            except Exception as e:
                self.statusBar.showMessage(f"Error exporting data: {str(e)}")
    
    def on_rules_updated(self):
        self.statusBar.showMessage("Rules updated")

def main():
    app = QApplication(sys.argv)
    window = DataTransformApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
