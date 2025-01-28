import os
import json
import re
import time
import chardet
from collections import defaultdict
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

# Function to read JSON files
def read_json(file_path):
    encoding = detect_encoding(file_path)
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Function to detect if a JSON response is complete
def is_response_complete(response):
    try:
        # Use a regex to extract JSON from the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            return False
        
        # Try to parse the JSON
        json.loads(json_match.group(0))
        return True
    except json.JSONDecodeError:
        return False

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
        
        # Debugging: Print the completion object
        print(completion)

        # Check if the response is valid
        if completion.choices and completion.choices[0]:
            return completion.choices[0].message.content
            
        # Wait before retrying
        time.sleep(wait_time)
    
    # If it fails after all attempts, return a default value or raise an exception
    print("Error: No valid response obtained after several attempts.")
    return None

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

# Function to create a mediated schema using the chatbot
def create_mediated_schema(source_folder):
    mediated_schema = defaultdict(lambda: {"description": "", "sources": []})
    attributes_data = []

    # Iterate over each file in the source folder
    for file_name in os.listdir(source_folder):
        if file_name.endswith('.json'):
            file_path = os.path.join(source_folder, file_name)
            data = read_json(file_path)
            attributes_data.append(data)
    

    # Define the prompt
    prompt = "".join(open("messageForModelMediateSchema.txt", "r", encoding='utf-8').readlines())
    
    table_content = json.dumps(attributes_data, indent=4)
    
    # Ask the chatbot to resolve heterogeneities and create the mediated schema
    response = ask_chatbot(prompt, table_content, max_retries=10, wait_time=10)
    
    if response and not is_response_complete(response):
        response = recover_incomplete_response(prompt, response, table_content)
    
    # Save the response to a text file
    with open('mediated_schema.txt', 'w', encoding='utf-8') as response_file:
        response_file.write(response if response else "No valid response obtained.")
        
    if response:
        mediated_schema = json.loads(response)
    else:
        print("Error: No valid response obtained.")
        mediated_schema = {}

    
    return mediated_schema

# Function to save mediated schema to a JSON file
def save_mediated_schema(mediated_schema, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(mediated_schema, file, indent=4)

# Main function
def main():
    source_folder = 'responses/json'
    output_file = 'mediated_schema.json'
    
    # Check if the mediated_schema.json file exists
    if not os.path.exists(output_file):
        # Create an empty mediated schema file
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump({}, file)
    
    mediated_schema = create_mediated_schema(source_folder)
    save_mediated_schema(mediated_schema, output_file)
    print(f"Mediated schema saved to {output_file}")

if __name__ == "__main__":
    main()
