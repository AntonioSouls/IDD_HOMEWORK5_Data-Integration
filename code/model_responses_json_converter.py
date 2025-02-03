import os
import re
import json

def model_responses_json_converter(model_responses_directory,output_json_file):

    data = {}
    
    # Scan files in the model's responses directory
    for filename in os.listdir(model_responses_directory):
        responses_path = os.path.join(model_responses_directory, filename)
        
        with open(responses_path, 'r', encoding="utf-8") as file:
            txt = file.read()
        
        # Extract json content from the text
        json_match = re.search(r'\{.*\}', txt, re.DOTALL)
        if json_match:
            json_response = json_match.group(0)
            
            try:
                new_data = json.loads(json_response)  # Conversion in dictionary data structure
                if isinstance(new_data, dict):  # Make sure that it is a dictionary
                    data.update(new_data)  # Join new json with the existent one
            except json.JSONDecodeError:
                print(f"Errore nel parsing JSON di {filename}")

    # Salva il JSON unificato
    with open(output_json_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
