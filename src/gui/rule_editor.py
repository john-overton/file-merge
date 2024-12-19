from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QComboBox, QLabel, QSpinBox, QDoubleSpinBox, 
                            QLineEdit, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Dict
import pandas as pd
from ..data_model import MatchRule, TransformRule

class RuleEditorWidget(QWidget):
    rule_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.match_rules: List[MatchRule] = []
        self.transform_rules: List[TransformRule] = []
        self.source_columns = []
        self.target_columns = []
        self.setup_ui()
        
    def update_columns(self, source_df: pd.DataFrame, target_df: pd.DataFrame):
        """Update available columns when source files are imported"""
        self.source_columns = list(source_df.columns)
        self.target_columns = list(target_df.columns)
        
        # Update existing rule widgets
        for i in range(self.match_container_layout.count()):
            widget = self.match_container_layout.itemAt(i).widget()
            if isinstance(widget, MatchRuleWidget):
                widget.update_columns(self.source_columns, self.target_columns)
                
        for i in range(self.transform_container_layout.count()):
            widget = self.transform_container_layout.itemAt(i).widget()
            if isinstance(widget, TransformRuleWidget):
                widget.update_columns(self.source_columns + self.target_columns)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Match Rules Section
        match_group = QFrame()
        match_group.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        match_layout = QVBoxLayout(match_group)
        match_layout.addWidget(QLabel("Match Rules"))
        
        # Add Match Rule Button
        add_match_btn = QPushButton("Add Match Rule")
        add_match_btn.clicked.connect(self.add_match_rule_widget)
        match_layout.addWidget(add_match_btn)
        
        # Scrollable area for match rules
        self.match_scroll = QScrollArea()
        self.match_scroll.setWidgetResizable(True)
        self.match_container = QWidget()
        self.match_container_layout = QVBoxLayout(self.match_container)
        self.match_scroll.setWidget(self.match_container)
        match_layout.addWidget(self.match_scroll)
        
        # Transform Rules Section
        transform_group = QFrame()
        transform_group.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        transform_layout = QVBoxLayout(transform_group)
        transform_layout.addWidget(QLabel("Transform Rules"))
        
        # Add Transform Rule Button
        add_transform_btn = QPushButton("Add Transform Rule")
        add_transform_btn.clicked.connect(self.add_transform_rule_widget)
        transform_layout.addWidget(add_transform_btn)
        
        # Scrollable area for transform rules
        self.transform_scroll = QScrollArea()
        self.transform_scroll.setWidgetResizable(True)
        self.transform_container = QWidget()
        self.transform_container_layout = QVBoxLayout(self.transform_container)
        self.transform_scroll.setWidget(self.transform_container)
        transform_layout.addWidget(self.transform_scroll)
        
        layout.addWidget(match_group)
        layout.addWidget(transform_group)
    
    def add_match_rule_widget(self):
        rule_widget = MatchRuleWidget(self)
        rule_widget.update_columns(self.source_columns, self.target_columns)
        rule_widget.rule_changed.connect(self.update_rules)
        self.match_container_layout.addWidget(rule_widget)
        
    def add_transform_rule_widget(self):
        rule_widget = TransformRuleWidget(self)
        rule_widget.update_columns(self.source_columns + self.target_columns)
        rule_widget.rule_changed.connect(self.update_rules)
        self.transform_container_layout.addWidget(rule_widget)
        
    def update_rules(self):
        # Collect all rules from widgets
        self.match_rules = []
        self.transform_rules = []
        
        # Gather match rules
        for i in range(self.match_container_layout.count()):
            widget = self.match_container_layout.itemAt(i).widget()
            if isinstance(widget, MatchRuleWidget):
                rule = widget.get_rule()
                if rule:
                    self.match_rules.append(rule)
        
        # Gather transform rules
        for i in range(self.transform_container_layout.count()):
            widget = self.transform_container_layout.itemAt(i).widget()
            if isinstance(widget, TransformRuleWidget):
                rule = widget.get_rule()
                if rule:
                    self.transform_rules.append(rule)
        
        self.rule_updated.emit()

class MatchRuleWidget(QWidget):
    rule_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        
        self.source_col = QComboBox()
        self.source_col.setPlaceholderText("Source Column")
        self.source_col.setMinimumWidth(150)
        
        self.target_col = QComboBox()
        self.target_col.setPlaceholderText("Target Column")
        self.target_col.setMinimumWidth(150)
        
        self.match_type = QComboBox()
        self.match_type.addItems(["exact", "fuzzy"])
        
        self.threshold = QDoubleSpinBox()
        self.threshold.setRange(0, 1)
        self.threshold.setSingleStep(0.1)
        self.threshold.setValue(0.9)
        
        self.case_sensitive = QComboBox()
        self.case_sensitive.addItems(["Case Insensitive", "Case Sensitive"])
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.deleteLater)
        delete_btn.clicked.connect(self.rule_changed)
        
        layout.addWidget(QLabel("Source:"))
        layout.addWidget(self.source_col)
        layout.addWidget(QLabel("Target:"))
        layout.addWidget(self.target_col)
        layout.addWidget(QLabel("Match:"))
        layout.addWidget(self.match_type)
        layout.addWidget(QLabel("Threshold:"))
        layout.addWidget(self.threshold)
        layout.addWidget(self.case_sensitive)
        layout.addWidget(delete_btn)
        
        # Connect signals
        self.source_col.currentTextChanged.connect(self.rule_changed)
        self.target_col.currentTextChanged.connect(self.rule_changed)
        self.match_type.currentTextChanged.connect(self.rule_changed)
        self.threshold.valueChanged.connect(self.rule_changed)
        self.case_sensitive.currentTextChanged.connect(self.rule_changed)
    
    def update_columns(self, source_columns: List[str], target_columns: List[str]):
        """Update available columns in dropdowns"""
        current_source = self.source_col.currentText()
        current_target = self.target_col.currentText()
        
        self.source_col.clear()
        self.source_col.addItems(source_columns)
        if current_source in source_columns:
            self.source_col.setCurrentText(current_source)
            
        self.target_col.clear()
        self.target_col.addItems(target_columns)
        if current_target in target_columns:
            self.target_col.setCurrentText(current_target)
    
    def get_rule(self) -> MatchRule:
        return MatchRule(
            source_column=self.source_col.currentText(),
            target_column=self.target_col.currentText(),
            match_type=self.match_type.currentText(),
            threshold=self.threshold.value(),
            case_sensitive=self.case_sensitive.currentText() == "Case Sensitive"
        )

class TransformRuleWidget(QWidget):
    rule_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        
        self.source_cols = QComboBox()
        self.source_cols.setPlaceholderText("Source Column")
        self.source_cols.setMinimumWidth(150)
        
        self.target_col = QLineEdit()
        self.target_col.setPlaceholderText("New Column Name")
        self.target_col.setMinimumWidth(150)
        
        self.transform_type = QComboBox()
        self.transform_type.addItems(["date_format", "number_format", "concatenate"])
        
        # Add parameter widgets based on transform type
        self.params_widget = QWidget()
        self.params_layout = QHBoxLayout(self.params_widget)
        self.setup_params_ui()
        
        self.transform_type.currentTextChanged.connect(self.setup_params_ui)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.deleteLater)
        delete_btn.clicked.connect(self.rule_changed)
        
        layout.addWidget(QLabel("Source:"))
        layout.addWidget(self.source_cols)
        layout.addWidget(QLabel("Target:"))
        layout.addWidget(self.target_col)
        layout.addWidget(QLabel("Type:"))
        layout.addWidget(self.transform_type)
        layout.addWidget(self.params_widget)
        layout.addWidget(delete_btn)
        
        # Connect signals
        self.source_cols.currentTextChanged.connect(self.rule_changed)
        self.target_col.textChanged.connect(self.rule_changed)
        self.transform_type.currentTextChanged.connect(self.rule_changed)
    
    def setup_params_ui(self):
        # Clear existing params
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        transform_type = self.transform_type.currentText()
        
        if transform_type == "date_format":
            self.source_format = QComboBox()
            self.source_format.addItems([
                "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"
            ])
            self.target_format = QComboBox()
            self.target_format.addItems([
                "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d"
            ])
            
            self.params_layout.addWidget(QLabel("From:"))
            self.params_layout.addWidget(self.source_format)
            self.params_layout.addWidget(QLabel("To:"))
            self.params_layout.addWidget(self.target_format)
            
            self.source_format.currentTextChanged.connect(self.rule_changed)
            self.target_format.currentTextChanged.connect(self.rule_changed)
            
        elif transform_type == "number_format":
            self.decimals = QSpinBox()
            self.decimals.setRange(0, 10)
            self.decimals.setValue(2)
            
            self.params_layout.addWidget(QLabel("Decimals:"))
            self.params_layout.addWidget(self.decimals)
            
            self.decimals.valueChanged.connect(self.rule_changed)
            
        elif transform_type == "concatenate":
            self.separator = QLineEdit()
            self.separator.setPlaceholderText("Separator")
            self.separator.setText(" ")
            self.separator.setMaximumWidth(50)
            
            self.params_layout.addWidget(QLabel("Separator:"))
            self.params_layout.addWidget(self.separator)
            
            self.separator.textChanged.connect(self.rule_changed)
    
    def update_columns(self, columns: List[str]):
        """Update available columns in dropdown"""
        current = self.source_cols.currentText()
        self.source_cols.clear()
        self.source_cols.addItems(columns)
        if current in columns:
            self.source_cols.setCurrentText(current)
    
    def get_rule(self) -> TransformRule:
        transform_type = self.transform_type.currentText()
        params = {}
        
        if transform_type == "date_format":
            params = {
                "source_format": self.source_format.currentText(),
                "target_format": self.target_format.currentText()
            }
        elif transform_type == "number_format":
            params = {
                "decimals": self.decimals.value()
            }
        elif transform_type == "concatenate":
            params = {
                "separator": self.separator.text()
            }
            
        return TransformRule(
            source_columns=[self.source_cols.currentText()],
            target_column=self.target_col.text(),
            transform_type=transform_type,
            parameters=params
        )
