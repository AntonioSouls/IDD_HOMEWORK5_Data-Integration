import os
import json
import re
from file_reader import read_file
from chatbot_client import ask_chatbot, is_response_complete, recover_incomplete_response

# Function to create a mediated schema using the chatbot
def create_mediated_schema(json_file_path):
    attributes_data = read_file(json_file_path)
    
    # Define the prompt
    prompt = "".join(open("data/messageForModelMediateSchema.txt", "r", encoding='utf-8').readlines())
    
    table_content = json.dumps(attributes_data, indent=4)
    
    # Ask the chatbot to resolve heterogeneities and create the mediated schema
    response = ask_chatbot(prompt, table_content, max_retries=10, wait_time=10)

    # Check if the response is not None and complete    
    if response and not is_response_complete(response):
        response = recover_incomplete_response(prompt, response, table_content)
    
    # Extract JSON from the response
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    if json_match:
        json_response = json_match.group(0)
    else:
        json_response = "{}"
    
    # Ensure the 'data' directory exists
    os.makedirs('data', exist_ok=True)
    
    # Save the JSON response directly
    with open('data/mediated_schema.json', 'w', encoding='utf-8') as json_file:
        json_file.write(json_response)

# Main function
def main():
    json_file_path = 'data/attributes_descriptions.json'
    output_file = 'data/mediated_schema.json'
    
    # Ensure the 'data' directory exists
    os.makedirs('data', exist_ok=True)
    
    # Check if the mediated_schema.json file exists
    if not os.path.exists(output_file):
        # Create an empty mediated schema file
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump({}, file)
    
    create_mediated_schema(json_file_path)
    print(f"Mediated schema saved to {output_file}")

if __name__ == "__main__":
    main()
