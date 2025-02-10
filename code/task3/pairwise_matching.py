import json
import pandas as pd
import recordlinkage

''' ______________________ Section of the script where we define the auxiliary functions _________________________________________ '''

''' ______________________ Section of the script where we define the various pairwise logics _________________________________________ '''

# Function that computes pairwise matching on the blocking operation results using Record Linkage Toolkit
def Record_Linkage_Toolkit_PM (input_blocking_JSON):
    # Load the blocking results
    with open(input_blocking_JSON, 'r', encoding='utf-8') as file:
        blocchi = json.load(file)
    blocchi_dataframes = {nome_blocco: pd.DataFrame(nomi_aziende, columns=["name"]) for nome_blocco, nomi_aziende in blocchi.items()}    # Store them into a dictionary
    
    # Create an Indexer that compare only the records inside each block
    indexer = recordlinkage.Index()
    
    pairs_list = []

    for nome_blocco, df_blocco in blocchi_dataframes.items():
        if len(df_blocco) > 1:
            candidate_pairs = df_blocco.index.to_series().reset_index()
            candidate_pairs = candidate_pairs.merge(candidate_pairs, how='cross')
            candidate_pairs = candidate_pairs[candidate_pairs["index_x"] < candidate_pairs["index_y"]]
            
            comparator = recordlinkage.Compare()
            comparator.string("name", "name", method="jarowinkler", threshold=0.85)

            features = comparator.compute(candidate_pairs[["index_x", "index_y"]], df_blocco)

            matched_pairs = features[features.sum(axis=1)>0].index.tolist()

            matched_names = [(df_blocco.iloc[pair[0]]["nome"], df_blocco.iloc[pair[1]]["nome"]) for pair in matched_pairs]
            pairs_list.append((nome_blocco, matched_names))


    print(pairs_list)
    return

# Function that computes pairwise matching on the blocking operation results using DITTO
def DITTO_PM():
    return

''' ______________________ Section of the script where we orchestrate the various pairwise logics _________________________________________ '''

# Orchestrator of the various pairwise logics
def main():
    Record_Linkage_Toolkit_PM("data/blocking_results/lsh_results.json")
    return

# Script's starter
if __name__ == "__main__":
    main()