import os
import pandas as pd
import json
import re
import time
import chardet
from openai import OpenAI

# Define the API client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="API_KEY",
)

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

# Function to send messages to the chatbot and receive responses
def ask_chatbot(prompt, table_content, max_retries, wait_time):
    for attempt in range(max_retries):
        completion = client.chat.completions.create(
            model="google/gemini-2.0-flash-thinking-exp:free",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{prompt}\n{table_content}"
                        }
                    ]
                }
            ],
        )
        
        # Check if the response is valid
        if completion.choices and completion.choices[0]:
            return completion.choices[0].message.content
            
        # Wait before retrying
        time.sleep(wait_time)
    
    # If it fails after all attempts, return a default value or raise an exception
    print("Error: No valid response obtained after several attempts.")
    return None

# Function to check if a JSON response is complete
def is_response_complete(response):
    try:
        # Use a regex to extract JSON from the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            return False
        
        # Try to parse the JSON
        json.loads(json_match.group(0))
        return True
    except json.JSONDecodeError as e:
        return False

# Function to recover an incomplete response by asking the model to continue
def ask_chatbot_recovery(prompt, continuation_prompt, max_retries, wait_time):
    for attempt in range(max_retries):
        completion = client.chat.completions.create(
            model="google/gemini-2.0-flash-thinking-exp:free",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{prompt}\n{continuation_prompt}"
                        }
                    ]
                }
            ],
        )
        
        # Check if the response is valid
        if completion.choices and completion.choices[0]:
            return completion.choices[0].message.content
            
        # Wait before retrying
        time.sleep(wait_time)
    
    # If it fails after all attempts, return a default value or raise an exception
    print("Error: No valid response obtained after several attempts.")
    return None

# Function to recover an incomplete response by asking the model to continue
def recover_incomplete_response(prompt, incomplete_response, table_content):
    continuation_prompt = f"Continue the incomplete response:\n{incomplete_response}\nFrom the table:\n{table_content}"
    continuation = ask_chatbot_recovery(prompt, continuation_prompt, 10, 10)
    if continuation:
        return incomplete_response + continuation
    return "{}"

# Main function
def main():
    
    # Define the folder containing the source files
    source_folder = 'sources'
    
    # Define the prompt
    prompt = "".join(open("messageForModel.txt", "r", encoding='utf-8').readlines())
    
    # Create the responses directory if it doesn't exist
    if not os.path.exists('responses'):
        os.makedirs('responses')
    
    # Iterate over each file in the source folder
    for file_name in os.listdir(source_folder):
        file_path = os.path.join(source_folder, file_name)
        
        # Read the file based on its extension
        if file_name.endswith('.csv'):
            data = read_csv(file_path)
        elif file_name.endswith('.xls') or file_name.endswith('.xlsx'):
            data = read_xls(file_path)
        elif file_name.endswith('.json'):
            data = read_json(file_path)
        elif file_name.endswith('.jsonl'):
            data = read_jsonl(file_path)
        else:
            print(f"Unsupported file format: {file_name}")
            continue
        
        # Extract attributes and sample data
        attributes, sample_data = extract_attributes_and_sample(data)
        
        # Generate descriptions using the chatbot
        table_content = {
            "attributes": attributes,
            "sample_data": sample_data
        }
        response = ask_chatbot(prompt, json.dumps(table_content), max_retries=10, wait_time=10)
        
        # Check if the response is not None and complete
        if response and not is_response_complete(response):
            response = recover_incomplete_response(prompt, response, json.dumps(table_content))
        
        # Save the response to a text file
        with open(f"responses/{file_name}_response.txt", "w", encoding='utf-8') as response_file:
            response_file.write(response if response else "No valid response obtained.")
        
        # Extract and save the JSON part of the response
        if response:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_response = json_match.group(0)
                with open(f"responses/{file_name}_attributes.json", "w", encoding='utf-8') as json_file:
                    json_file.write(json_response)

if __name__ == "__main__":
    main()
