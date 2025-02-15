""" Script needed to keep only groundtruth tuples in the mediated schema. 
    This allows us a statistical evaluation of the accuracy of our solution. """

import pandas as pd

# Files definitions
file_txt = "evaluation_data/ground_truth.txt"  
file_csv = "data/mediated_schema_populated.csv"  
file_output = "evaluation_data/mediated_schema_groundtruth.csv"

# Read the groundtruth file and extract names
with open(file_txt, "r", encoding="utf-8") as f:
    lines = f.readlines()
    names = set()
    for line in lines:
        parts = set(p.strip() for p in line.strip().split("||"))  # Rimuove duplicati per riga
        names.update(parts)

# Load CSV file
df = pd.read_csv(file_csv)

# DataFrame Filtering
df_filtered = df[df['name'].isin(names)]

# Save the filtered DataFrame
df_filtered.to_csv(file_output, index=False, encoding="utf-8")

print(f"File filtrato salvato come {file_output}")

