""" Script needed to convert blocking results into a format that can be understood by DITTO """

import json

# Function to create dictionary couples
def crea_coppie(dizionario):
    coppie = []
    for key, values in dizionario.items():
        if len(values) < 2:
            continue  # skip lists with less than two items
        # Create all possible pairs within the same block
        for i in range(len(values)):
            for j in range(i+1, len(values)):
                coppie.append(f"{values[i]}\t{values[j]}")
    return coppie

# Function util to write all the couples on a file
def scrivi_su_file(coppie, nome_file):
    with open(nome_file, 'w', encoding='utf-8') as f:
        for coppia in coppie:
            f.write(coppia + '\n')

# Load the JSON file
def carica_json(nome_file):
    with open(nome_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# Main function
def main(input_json, output_txt):
    dizionario = carica_json(input_json)
    coppie = crea_coppie(dizionario)
    scrivi_su_file(coppie, output_txt)
    print(f"File di coppie creato: {output_txt}")

# Script starter
input_json_1 = 'evaluation_data/blocking_results/lsh_results_for_RLT.json' 
output_txt_1 = 'evaluation_data/blocking_results/lsh_results_for_DITTO.txt'

input_json_2 = 'evaluation_data/blocking_results/QGram_results_for_RLT.json'
output_txt_2 = 'evaluation_data/blocking_results/QGram_results_for_DITTO.txt'

main(input_json_1, output_txt_1)
main(input_json_2, output_txt_2)
