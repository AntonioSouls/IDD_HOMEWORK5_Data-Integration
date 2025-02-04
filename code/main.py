import os
import json
from file_reader import read_file
from chatbot_client import ask_chatbot, is_response_complete, recover_incomplete_response
from data_processing import extract_attributes_and_sample
from model_responses_json_converter import model_responses_json_converter

def attributes_descriptions_extractor():

    # Define the folder containing the source files
    source_folder = 'sources'

    # Define the prompt
    prompt = "".join(open("data/messageForModel.txt", "r", encoding='utf-8').readlines())
    
    # Create the model's responses directory if it doesn't exist
    model_responses_directory = "data/model_responses"
    if not os.path.exists(model_responses_directory):
        os.makedirs(model_responses_directory)
    
    # Iterate over each file in the source folder
    for file_name in os.listdir(source_folder):
        file_path = os.path.join(source_folder, file_name)
        file_base_name = os.path.splitext(file_name)[0]   # Get the file name without extension
        
        try:
            data = read_file(file_path)
        except ValueError as e:
            print(e)
            continue
        
        # Extract attributes and sample data
        attributes, sample_data = extract_attributes_and_sample(data)

        # Generate descriptions using the chatbot
        table_content = {
            "file_name": file_base_name,
            "attributes": attributes,
            "sample_data": sample_data
        }        
        response = ask_chatbot(prompt, json.dumps(table_content), max_retries=10, wait_time=10)
        
        # Check if the response is not None and complete
        if response and not is_response_complete(response):
            response = recover_incomplete_response(prompt, response, json.dumps(table_content))
            
        # Save the response to a text file
        with open(f"{model_responses_directory}/{file_base_name}_response.txt", "w", encoding='utf-8') as response_file:
            response_file.write(response if response else "No valid response obtained.")
    
    model_responses_json_converter(model_responses_directory,"data/attributes_descriptions.json")


if __name__ == "__main__":
    attributes_descriptions_extractor()
