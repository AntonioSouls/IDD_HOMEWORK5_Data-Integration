import os
import json
import time
import pandas as pd
import recordlinkage


''' ______________________ Section of the script where we define the various pairwise logics _________________________________________ '''

# Function that computes pairwise matching on the blocking operation results using Record Linkage Toolkit
def Record_Linkage_Toolkit_PM(input_blocking_JSON, output_results_file):
    # Load the blocking results
    with open(input_blocking_JSON, 'r', encoding='utf-8') as file:
        blocchi = json.load(file)
    
    blocchi_dataframes = {nome_blocco: pd.DataFrame(nomi_aziende, columns=["name"]) for nome_blocco, nomi_aziende in blocchi.items()}  # Store them into a dictionary
    
    pairs_list = []
    
    for nome_blocco, df_blocco in blocchi_dataframes.items():
        if len(df_blocco) > 1:
            candidate_pairs = df_blocco.index.to_series().reset_index()
            candidate_pairs = candidate_pairs.merge(candidate_pairs, how='cross')
            candidate_pairs = candidate_pairs[candidate_pairs["index_x"] < candidate_pairs["index_y"]]
            
            comparator = recordlinkage.Compare()
            comparator.string("name", "name", method="jarowinkler")  # No threshold here, we store raw scores
            
            pairs_index = pd.MultiIndex.from_frame(candidate_pairs[["index_x", "index_y"]])
            features = comparator.compute(pairs_index, df_blocco)
            
            for (idx1, idx2), score in features.iterrows():
                feature_name = features.columns[0]  # Ottiene dinamicamente il nome della colonna
                decision = 1 if score[feature_name] >= 0.85 else 0

                feature_name = features.columns[0]  # Prende dinamicamente il nome della colonna
                pairs_list.append(f"{df_blocco.iloc[idx1]['name']}\t{df_blocco.iloc[idx2]['name']}\t{decision}\t{score[feature_name]:.4f}")

    
    with open(output_results_file, "w", encoding='utf-8') as f:
        for string in pairs_list:
            f.write(string + "\n")
    
    return






''' ______________________ Section of the script where we orchestrate the various pairwise logics _________________________________________ '''

# Orchestrator of the various pairwise logics
def main():

    # Define the inputs for the Pairwise Matching Phase
    lsh_input_file = "evaluation_data/blocking_results/lsh_results_for_RLT.json"
    QGram_input_file = "evaluation_data/blocking_results/QGram_results_for_RLT.json"

    #Define the outputs for the Pairwise Matching Phase
    output_directory = "evaluation_data/PairwiseMatching_results"
    os.makedirs(output_directory, exist_ok=True)
    LSH_RLT_output_file = f"{output_directory}/LSH_RLT_pairwise_matching.txt"
    QGRAM_RLT_output_file = f"{output_directory}/QGRAM_RLT_pairwise_matching.txt"
    stats_file = "evaluation_data/execution_times.txt"

    # Execution of pairwise matching on the locality sensitive hashing results with RLT
    print("Execution of PAIRWISE MATCHING with RLT on the LOCALITY SENSITIVE HASHING results ...")
    start_time = time.time()
    Record_Linkage_Toolkit_PM(lsh_input_file,LSH_RLT_output_file)
    end_time = time.time()
    total_time = end_time - start_time
    print(f"PAIRWISE MATCHING with RLT on LOCALITY SENSITIVE HASHING executed in {total_time:.2f} seconds\n\n")
    with open(stats_file, "a", encoding='utf-8') as f:
        f.write(f"PAIRWISE MATCHING with RLT on LOCALITY SENSITIVE HASHING executed in {total_time:.2f} seconds\n")

    # Execution of pairwise matching on the QGram Blocking results with RLT
    print("Execution of PAIRWISE MATCHING with RLT on the QGRAM BLOCKING results ...")
    start_time = time.time()
    Record_Linkage_Toolkit_PM(QGram_input_file,QGRAM_RLT_output_file)
    end_time = time.time()
    total_time = end_time - start_time
    print(f"PAIRWISE MATCHING with RLT on QGRAM BLOCKING executed in {total_time:.2f} seconds\n\n")
    with open(stats_file, "a", encoding='utf-8') as f:
        f.write(f"PAIRWISE MATCHING with RLT on QGRAM BLOCKING executed in {total_time:.2f} seconds\n")

    return

# Script's starter
if __name__ == "__main__":
    main()