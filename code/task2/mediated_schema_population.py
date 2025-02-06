import sys
import os

# Add the path of the task1 folder to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'task1')))

import json
import csv
import pandas as pd # Ensure pandas is installed: pip install pandas
from file_reader import read_file  # type: ignore # Assuming file_reader.py is in the same directory

def populate_csv_from_schema_and_sources(json_schema_mapping_path, csv_output_path, sources_folder):
 
    try:
        with open(json_schema_mapping_path, 'r', encoding='utf-8') as json_file:
            schema_mapping = json.load(json_file)
    except FileNotFoundError:
        print(f"Error: JSON schema mapping file not found at {json_schema_mapping_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_schema_mapping_path}")
        return

    mediated_attributes = list(schema_mapping.keys())

    # Ensure the directory for the CSV output exists
    os.makedirs(os.path.dirname(csv_output_path), exist_ok=True)

    try:
        with open(csv_output_path, 'w', encoding='utf-8', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(mediated_attributes)  # Write header row

            for filename in os.listdir(sources_folder):
                if not filename.startswith('.'): # Skip hidden files like .DS_Store
                    source_file_path = os.path.join(sources_folder, filename)
                    source_name = os.path.splitext(filename)[0]

                    try:
                        source_data = read_file(source_file_path)
                    except ValueError as e:
                        print(f"Error reading file {filename}: {e}")
                        continue

                    if isinstance(source_data, pd.DataFrame):
                        records = source_data.to_dict(orient='records')
                    elif isinstance(source_data, list):
                        records = source_data
                    elif isinstance(source_data, dict):
                        records = [source_data] # Treat single dict as one record
                    else:
                        print(f"Unsupported data format from {filename}. Skipping file.")
                        continue

                    for record in records:
                        csv_row_data = []
                        for mediated_attribute in mediated_attributes:
                            attribute_values = []
                            if mediated_attribute in schema_mapping:
                                for source_info in schema_mapping[mediated_attribute]['sources']:
                                    if source_info['source_name'] == source_name:
                                        source_attribute_name = source_info['source_attribute']
                                        if isinstance(record, dict) and source_attribute_name in record:
                                            value = record.get(source_attribute_name)
                                            if value is not None:
                                                attribute_values.append(str(value)) # Convert value to string
                                        elif isinstance(record, pd.Series) and source_attribute_name in record.index: #For DataFrame records
                                            value = record.get(source_attribute_name)
                                            if value is not None:
                                                attribute_values.append(str(value))
                                attribute_value_str = ", ".join(attribute_values)
                                csv_row_data.append(attribute_value_str)
                            else:
                                csv_row_data.append("") # Empty if mediated attribute not found in schema

                        csv_writer.writerow(csv_row_data)

        print(f"Successfully populated CSV file at {csv_output_path}")

    except Exception as e:
        print(f"An error occurred during CSV population: {e}")


def main():
    json_schema_mapping_file = 'data/schema_mapping.json'
    csv_file = 'data/mediated_schema_populated.csv'
    sources_folder = 'sources'  # Assuming 'sources' folder is in the same directory as the script

    populate_csv_from_schema_and_sources(json_schema_mapping_file, csv_file, sources_folder)

if __name__ == "__main__":
    main()
