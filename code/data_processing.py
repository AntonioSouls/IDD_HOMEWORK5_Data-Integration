import pandas as pd

# Function to extract attributes and sample data
def extract_attributes_and_sample(data):
    if isinstance(data, pd.DataFrame):
        attributes = data.columns.tolist()
        sample_data = data.head(5).to_dict(orient='records')
    elif isinstance(data, list):
        attributes = list(data[0].keys())
        sample_data = data[:5]
    elif isinstance(data, dict):
        attributes = list(data.keys())
        sample_data = [data]  # Assuming the dict represents a single record
    return attributes, sample_data
