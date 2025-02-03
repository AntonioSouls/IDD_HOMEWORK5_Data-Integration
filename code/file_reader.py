import os
import pandas as pd
import json
import chardet

# Function to detect file encoding
def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
    result = chardet.detect(raw_data)
    return result['encoding']

# Function to read CSV file
def read_csv(file_path):
    encoding = detect_encoding(file_path)
    return pd.read_csv(file_path, encoding=encoding)

# Function to read XLS file
def read_xls(file_path):
    return pd.read_excel(file_path)

# Function to read JSON file
def read_json(file_path):
    encoding = detect_encoding(file_path)
    with open(file_path, 'r', encoding=encoding) as file:
        return json.load(file)

# Function to read JSONL file
def read_jsonl(file_path):
    encoding = detect_encoding(file_path)
    data = []
    with open(file_path, 'r', encoding=encoding) as file:
        for line in file:
            data.append(json.loads(line))
    return data

# Determines the file type and reads it accordingly.
def read_file(file_path):
    
    if file_path.endswith('.csv'):
        return read_csv(file_path)
    elif file_path.endswith(('.xls', '.xlsx')):
        return read_xls(file_path)
    elif file_path.endswith('.json'):
        return read_json(file_path)
    elif file_path.endswith('.jsonl'):
        return read_jsonl(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path}")
