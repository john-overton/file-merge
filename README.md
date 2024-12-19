# Data Transform & Match

A Windows desktop application for data transformation and matching with support for CSV and Excel files.

## Features

- Import multiple CSV and XLSX files simultaneously
- Preview imported data in tabular format
- Define match rules between datasets:
  - Exact matching
  - Fuzzy matching with configurable threshold
  - Case sensitive/insensitive options
- Transform data with configurable rules:
  - Date format conversion
  - Number formatting
  - Text concatenation
- Export results to CSV or Excel

## Installation

1. Ensure Python 3.8+ is installed
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

From the project directory:
```bash
python -m src.main
```

## Usage

1. Click "Import Files" to select CSV or Excel files
2. Add match rules to define relationships between datasets:
   - Select source and target columns
   - Choose match type (exact/fuzzy)
   - Set threshold for fuzzy matching
   - Toggle case sensitivity
3. Add transform rules to modify data:
   - Select source columns and target column
   - Choose transform type
   - Configure parameters in JSON format:
     - Date format: `{"source_format": "%m/%d/%Y", "target_format": "%Y-%m-%d"}`
     - Number format: `{"decimals": 2}`
     - Concatenate: `{"separator": " "}`
4. Click "Apply Rules" to execute the transformation
5. Review results in the preview
6. Click "Export" to save the transformed data
