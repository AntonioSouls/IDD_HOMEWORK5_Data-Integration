import json
import csv
import os

def create_csv_from_schema_mapping_json(json_schema_mapping_path, csv_output_path):
  
    try:
        with open(json_schema_mapping_path, 'r', encoding='utf-8') as json_file:
            schema_mapping = json.load(json_file)
    except FileNotFoundError:
        print(f"Error: JSON schema mapping file not found at {json_schema_mapping_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_schema_mapping_path}")
        return

    attribute_names = list(schema_mapping.keys())

    # Ensure the directory for the CSV output exists
    os.makedirs(os.path.dirname(csv_output_path), exist_ok=True)

    try:
        with open(csv_output_path, 'w', encoding='utf-8', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(attribute_names)  # Write header row
        print(f"Empty CSV file created successfully at {csv_output_path}")
    except Exception as e:
        print(f"Error writing CSV file: {e}")


def main():
    json_schema_mapping_file = 'data/schema_mapping.json'  # Path to your JSON schema mapping file
    csv_file = 'data/mediated_schema.csv'         # Path for the output CSV file

    create_csv_from_schema_mapping_json(json_schema_mapping_file, csv_file)


if __name__ == "__main__":
    main()
