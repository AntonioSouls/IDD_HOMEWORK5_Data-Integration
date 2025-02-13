import json

# Nome del file di input e output
input_file = "data/DITTO_datasets/DITTO_valid_set.jsonl"
output_file = "data/DITTO_datasets/DITTO_valid_set.txt"

with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
    for line in infile:
        line = line.strip()  # Rimuove spazi e newline extra
        if not line:  # Salta righe vuote
            continue
        try:
            data = json.loads(line)
            left_name = data["left"]["name"]
            right_name = data["right"]["name"]
            label = data["label"]
            outfile.write(f"{left_name}\t{right_name}\t{label}\n")
        except json.JSONDecodeError as e:
            print(f"Errore nella riga: {line}\nErrore: {e}")

print("Conversione completata. Output salvato in", output_file)
