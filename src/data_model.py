from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
from rapidfuzz import fuzz

@dataclass
class MatchRule:
    source_column: str
    target_column: str
    match_type: str  # exact, fuzzy
    threshold: float = 0.9  # for fuzzy matching
    case_sensitive: bool = False

@dataclass
class TransformRule:
    source_columns: List[str]
    target_column: str
    transform_type: str  # date_format, number_format, concatenate, etc.
    parameters: Dict[str, Any]

class DataTransformer:
    def __init__(self):
        self.match_rules: List[MatchRule] = []
        self.transform_rules: List[TransformRule] = []
        
    def add_match_rule(self, rule: MatchRule):
        self.match_rules.append(rule)
        
    def add_transform_rule(self, rule: TransformRule):
        self.transform_rules.append(rule)
        
    def match_records(self, source_df: pd.DataFrame, target_df: pd.DataFrame) -> pd.DataFrame:
        matched_records = []
        
        for _, source_row in source_df.iterrows():
            best_match = None
            best_score = 0
            
            for _, target_row in target_df.iterrows():
                match_scores = []
                
                for rule in self.match_rules:
                    source_val = str(source_row[rule.source_column])
                    target_val = str(target_row[rule.target_column])
                    
                    if not rule.case_sensitive:
                        source_val = source_val.lower()
                        target_val = target_val.lower()
                    
                    if rule.match_type == 'exact':
                        score = 1.0 if source_val == target_val else 0.0
                    else:  # fuzzy
                        score = fuzz.ratio(source_val, target_val) / 100
                        
                    match_scores.append(score)
                
                avg_score = sum(match_scores) / len(match_scores)
                if avg_score > best_score and avg_score >= min(rule.threshold for rule in self.match_rules):
                    best_score = avg_score
                    best_match = target_row
            
            if best_match is not None:
                matched_record = {**source_row.to_dict(), **best_match.to_dict()}
                matched_records.append(matched_record)
                
        return pd.DataFrame(matched_records)
    
    def apply_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        result_df = df.copy()
        
        for rule in self.transform_rules:
            try:
                if rule.transform_type == 'date_format':
                    result_df[rule.target_column] = pd.to_datetime(
                        df[rule.source_columns[0]], 
                        format=rule.parameters.get('source_format'),
                    ).dt.strftime(rule.parameters.get('target_format'))
                    
                elif rule.transform_type == 'number_format':
                    result_df[rule.target_column] = pd.to_numeric(
                        df[rule.source_columns[0]], 
                        errors='coerce'
                    ).round(rule.parameters.get('decimals', 2))
                    
                elif rule.transform_type == 'concatenate':
                    result_df[rule.target_column] = df[rule.source_columns].astype(str).agg(
                        rule.parameters.get('separator', ' ').join, axis=1
                    )
                    
            except Exception as e:
                print(f"Error applying transformation {rule.transform_type}: {str(e)}")
                
        return result_df
