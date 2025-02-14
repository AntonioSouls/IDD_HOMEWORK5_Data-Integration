import json

# Funzione per creare le coppie dal dizionario
def crea_coppie(dizionario):
    coppie = []
    for key, values in dizionario.items():
        if len(values) < 2:
            continue  # Salta le liste con meno di due elementi
        # Crea tutte le coppie possibili all'interno dello stesso blocco
        for i in range(len(values)):
            for j in range(i+1, len(values)):
                coppie.append(f"{values[i]}\t{values[j]}")
    return coppie

# Funzione per scrivere le coppie su file
def scrivi_su_file(coppie, nome_file):
    with open(nome_file, 'w', encoding='utf-8') as f:
        for coppia in coppie:
            f.write(coppia + '\n')

# Carica il file JSON
def carica_json(nome_file):
    with open(nome_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# Funzione principale
def main(input_json, output_txt):
    dizionario = carica_json(input_json)
    coppie = crea_coppie(dizionario)
    scrivi_su_file(coppie, output_txt)
    print(f"File di coppie creato: {output_txt}")

# Usa la funzione principale
input_json_1 = 'data/blocking_results/lsh_results_for_RLT.json'  # Il file JSON di input
output_txt_1 = 'data/blocking_results/lsh_results_for_DITTO.txt'  # Il file di output

input_json_2 = 'data/blocking_results/QGram_results_for_RLT.json'  # Il file JSON di input
output_txt_2 = 'data/blocking_results/QGram_results_for_DITTO.txt'  # Il file di output

main(input_json_1, output_txt_1)
main(input_json_2, output_txt_2)
