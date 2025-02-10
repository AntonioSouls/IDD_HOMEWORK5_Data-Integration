def get_shingles(text, k=3):
    """Genera un insieme di k-shingles (n-grammi) da una stringa."""
    return {text[i:i+k] for i in range(len(text) - k + 1)}

def get_minhash_ngram(text, num_perm=128, k=3):
    """Genera una firma MinHash usando n-grammi invece delle parole."""
    minhash = MinHash(num_perm=num_perm)
    
    shingles = get_shingles(text.lower(), k)  # Creiamo i trigrammi
    for shingle in shingles:
        minhash.update(shingle.encode('utf8'))  # Aggiungiamo alla MinHash

    return minhash


import os
import re
import time
import json
import pandas as pd
from datasketch import MinHash, MinHashLSH
from unidecode import unidecode


''' ______________________ Section of the script where we define the auxiliary functions _________________________________________ '''

# Function that removes noisy words from the company name
def remove_noise_words(text: str):
    # Define a set of common noise words
    noise_words = {
        'technologies', 'snc', 'services', 'corporate', 'tbk', 'company', 'incorporated', 'regional', 'hf', 'ltd',
        'llp', 'vereniging', 'pty', 'gesellschaft', 'industries', 'corporation', 'firm', 'partnership', 'gyo', 'solutions',
        'consults', 'ortakligi', 'international', 'careers', 'aps', 'inc', 'construction', 'financial', 'nonprofit', 'plc',
        'corp', 'enterprises', 'societa', 'pllc', 'foundation', 'saa', 'gruppo', 'gmbh', 'chartered', 'constructions', 'nv',
        'kk', 'uc', 'society', 'co', 'consultants', 'finances', 'kaisha', 'holding', 'eeig', 'lp', 'grupo', 'partners', 'as',
        'communications', 'associates', 'private', 'ulc', 'limited', 'sas', 'yatirim', 'sarl', 'llc', 'consult', 'global',
        'business', 'enterprise', 'unlimited', 'gayrimenkul', 'public', 'aktiengesellschaft', 'holdings', 'ag', 'group',
        'trust', 'groupe', 'systems', 'joint stock company', 'spa', 'communication', 'sa', 'ou', 'proprietary', 'bv', 'studios',
        'technology', 'kabushiki', 'gruppen', 'finance', 'gaisha', 'ab', 'srl', 'ventures', 'oy'
    }   

    # Split the text into tokens and remove noise words
    tokens = [token for token in text.split() if token not in noise_words]

    # Return the filtered text
    return ' '.join(tokens)

# Function which divides words written in Pascal Case 
def split_pascal_case(text):
    return re.sub(r'(?<!^)(?<![A-Z])(?=[A-Z])', ' ', text)

# Function that clean a noisy text
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

# Function useful to generating the acronym of a name
def generate_acronym(clean_name: str):
    words = clean_name.split()
    if len(words) < 2:
        return ""
    acronym = ''.join([word[0] for word in words])
    return acronym.lower()

# Function that aims to clean the input DataFrame to remove noise that could be a problem for the blocking operation
def clean_Data_Frame(df: pd.DataFrame):
    acronym_dict = {}
    df["clean_name"] = df["name"].apply(lambda x: clean_text(str(x)))
    for clean_name in df["clean_name"]:
        acronym = generate_acronym(clean_name)
        if acronym and acronym not in acronym_dict:
            acronym_dict[acronym] = clean_name
    
    df["clean_name"] = df["clean_name"].apply(lambda x: acronym_dict.get(x, x))
    return df

# Function which generates a MinHash based on the words that make up the text it receives as input
def get_word_minhash(cleaned_text):
    minhash = MinHash(num_perm=128)
    for token in cleaned_text.split():
        minhash.update(token.encode('utf8'))
    return minhash



''' ______________________ Section of the script where we define the various blocking logics _________________________________________ '''

# Locality Sensitive Hasing Blocking 
def lsh_blocking(df: pd.DataFrame ,blocking_output_file):
    
    # For each name in DataFrame, clean the text and compute a MinHashing on the cleaned string 
    df["minhash"] = df["clean_name"].apply(lambda x : get_word_minhash(x))
    
    # Create the LSHIndex whit a Similarity threshold and insert each rows into the index
    lsh_index = MinHashLSH(threshold=0.5, num_perm=128)
    for i, row in df.iterrows():
        lsh_index.insert(i, row["minhash"])

    # Create the dictionary that will contain blocks of similar names
    blocks = {}

    # For each name in DataFrame, find similar ones
    for i, row in df.iterrows():
        similar_indices = lsh_index.query(row["minhash"])  # Find similar IDs
        similar_names = set(df.iloc[similar_indices]["name"].tolist())  # Recover the original names
        similar_names = {name for name in similar_names if isinstance(name, str)}
        if not similar_names:
            continue

        key_name = min(similar_names)

        if key_name not in blocks:
            blocks[key_name] = list(similar_names)

    for key, values in blocks.items():                              # Ensures that Nan values ​​do not affect json formatting
        blocks[key] = [v if not pd.isna(v) else "" for v in values]

    # Store blocks into a specific JSON file
    with open(blocking_output_file, "w", encoding="utf-8") as f:
        json.dump(blocks, f, indent=4, ensure_ascii=False)
    
    return


# Blocking based on text QGram division
def QGram_blocking(df,blocking_output_file):
    return


''' ______________________ Section of the script where we orchestrate the various blocking logics _________________________________________ '''

# Orchestrator of the two blocking logic '''
def main():
    # Read the mediated schema as Pandas DataFrame useful as input for blocking
    df = pd.read_csv("data/mediated_schema_populated.csv", usecols=["name"])

    # Clean the Pandas DataFrame to allow a more accurate blocking
    df = clean_Data_Frame(df)
    
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

    # Starting the QGram_blocking strategy
    print("Starting QGRAM BLOCKING ... ")
    start_time = time.time()
    QGram_blocking(df,QGram_output_file)
    end_time = time.time()
    total_time = end_time - start_time
    print(f"QGRAM BLOCKING executed in {total_time: .6f} secondi\n\n")

    # Storage of the QGram_statistics
    with open(stats_file, "a", encoding='utf-8') as f:
        f.write(f"QGRAM BLOCKING executed in {total_time: .6f} secondi\n\n")
    
    return

# Script's starter
if __name__ == "__main__":
    main()