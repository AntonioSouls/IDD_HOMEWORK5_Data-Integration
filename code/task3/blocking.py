import os
import re
import time
import json
import pandas as pd
from datasketch import MinHash, MinHashLSH
from unidecode import unidecode


#################### Section of the script where we define the auxiliary functions #############################################

def remove_noise_words(text: str) -> str:
    # Define a set of common noise words
    noise_words = {
        "inc", "ltd", "llc", "corp", "corporation", "co", "company", "srl", "spa", "limited", "ou", "as", "firm",
        "group", "tbk", "hf", "gmbh", "ag", "plc", "pty", "nv", "sa", "saa", "bv", "ab", "aps", "oy", "kk", "kabushiki", 
        "ulc", "eeig", "sarl", "sas", "snc", "societa", "gesellschaft", "aktiengesellschaft", "trust", "holdings", "llp",
        "associates", "partners", "enterprise", "enterprises", "ventures", "corporate", "uc", "lp", "constructions",
        "industries", "solutions", "services", "technologies", "systems", "global", "studios", "construction", "pllc",
        "regional", "private", "public", "joint stock company", "proprietary", "foundation", "chartered", "kaisha",
        "unlimited", "partnership", "society", "incorporated", "vereniging", "foundation", "grupo",  "technology",
        "nonprofit", "kabushiki", "gaisha", "financial", "gayrimenkul", "yatirim", "ortakligi", "gyo", "gruppo", "groupe",
        "gruppen", "holdings", "holding", "finance", "finances", "careers", "consultants", "consult", "consults",
        "communication", "communications", "business", "international"
    }   

    # Split the text into tokens and remove noise words
    tokens = [token for token in text.split() if token not in noise_words]

    # Return the filtered text
    return ' '.join(tokens)


def split_pascal_case(text):
    return re.sub(r'(?<!^)(?<![A-Z])(?=[A-Z])', ' ', text)


def clean_text(text: str):

    # Remove words between parenthesis
    text = re.sub(r"\(.*\)", "", text)
    text = re.sub(r"\[.*\]", "", text)

    # Replace dashes with spaces
    text = re.sub(r"[-_]", " ", text)

    # Remove accents and special characters
    text = unidecode(text)

    # Convert to lowercase, remove extra spaces and punctuation
    text = re.sub(r"[^a-zA-Z0-9&\s]", "", text.lower().strip())

    # Split pascal case
    text = split_pascal_case(text)

    # Remove words that are usally not relevant for matching
    text = remove_noise_words(text)

    return text


def get_word_minhash(cleaned_text):
    minhash = MinHash(num_perm=128)
    for token in cleaned_text.split():
        minhash.update(token.encode('utf8'))
    return minhash



 
#################### Section of the script where we define the various blocking logics #########################################

''' Locality Sensitive Hasing Blocking '''
def lsh_blocking(df: pd.DataFrame ,blocking_output_file):

    # For each name in DataFrame, clean the text and compute a MinHashing on the cleaned string 
    df["minhash"] = df["name"].apply(lambda x : get_word_minhash(clean_text(str(x))))

    # Create the LSHIndex whit a Similarity threshold and insert each rows into the index
    lsh_index = MinHashLSH(threshold=0.5, num_perm=128)
    for i, row in df.iterrows():
        lsh_index.insert(i, row["minhash"])

    # Create the dictionary that will contain blocks of similar names
    blocks = {}

    # For each name in DataFrame, find similar ones
    for i, row in df.iterrows():
        similar_indices = lsh_index.query(row["minhash"])  # Find similar IDs
        similar_names = df.iloc[similar_indices]["name"].tolist()  # Recover the original names

        blocks[row["name"]] = similar_names
    for key, values in blocks.items():                              # Ensures that Nan values ​​do not affect json formatting
        blocks[key] = [v if not pd.isna(v) else "" for v in values]

    # Store blocks into a specific JSON file
    with open(blocking_output_file, "w", encoding="utf-8") as f:
        json.dump(blocks, f, indent=4, ensure_ascii=False)
    
    return

# ''' Blocking based on text QGram division '''
# def QGram_blocking(df,blocking_output_file):
#     return



#################### Section of the script where we orchestrate the various blocking logic  ####################################

''' Orchestrator of the two blocking logic '''
def main():
    # Read the mediated schema as Pandas DataFrame useful as input for blocking
    df = pd.read_csv("data/mediated_schema_populated.csv", usecols=["name"])

    # Create the directory in which to save the blocking results
    output_directory = "data/blocking_results"
    os.makedirs(output_directory, exist_ok=True)
    lsh_output_file = f"{output_directory}/lsh_results.json"
    QGram_output_file = f"{output_directory}/QGram_results.json"

    # Starting the LSH_Blocking strategy
    print("Starting LOCALITY SENSITIVE HASHING ... ")
    start_time = time.time() 
    lsh_blocking(df, lsh_output_file)
    end_time = time.time()
    total_time = end_time - start_time
    print(f"LOCALITY SENSITIVE HASHING executed in {total_time: .6f} secondi\n\n")

    # Storage of the LSH_statistics
    stats_file = "data/blocking_results/blocking_statistics.txt"
    with open(stats_file, "w", encoding="utf-8") as f:
        f.write(f"LOCALITY SENSITIVE HASHING executed in {total_time:.6f} seconds\n")

    # # Starting the QGram_blocking strategy
    # print("Starting QGRAM BLOCKING ... ")
    # start_time = time.time()
    # QGram_blocking(df,QGram_output_file)
    # end_time = time.time()
    # total_time = end_time - start_time
    # print(f"QGRAM BLOCKING executed in {total_time: .6f} secondi\n\n")
    
    return

''' Script's starter '''
if __name__ == "__main__":
    main()