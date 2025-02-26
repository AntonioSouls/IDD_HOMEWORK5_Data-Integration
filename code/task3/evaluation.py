from tqdm import tqdm

# Function that computes the calculation of metrics on a single file
def evaluation(pairwise_file,groundtruth_file):
    pairwise_dati = []                # Initializing the list in which we will save pairwise file's lines
    groundtruth_dati = []             # Initializing the list in which we will save groundtruth file's lines
    pairwise_waiting_removed = []     # Initializing the list in which we will save the elements that will be removed from pairwise data
    groundtruth_waiting_removed = []  # Initializing the list in which we will save the elements that will be removed from groundtruth data
    stats = [0,0,0]                   # Stats that we want to store (in this order): Number of TRUE POSITIVES, Number of FALSE POSITIVES, Number of FALSE NEGATIVES
    
    # Read the pairwise_matching.txt filtering lines with the third element equal to "1"
    with open(pairwise_file, "r", encoding="utf-8") as file:
        for linea in file:
            elementi = [parola.strip() for parola in linea.split("\t")]
            pairwise_dati.append(tuple(elementi))
    
    # Read groundtruth.txt file
    with open(groundtruth_file, "r", encoding="utf-8") as file:
        for linea in file:
            elementi = [parola.strip() for parola in linea.split("||")]
            groundtruth_dati.append(tuple(elementi))
    
    # Calculating the number of TRUE POSITIVES
    for element in pairwise_dati:
        if element[2] == "1":
            for line in groundtruth_dati:
                if (element[0] == line[0] and element[1] == line[1]) or (element[1] == line[0] and element[0] == line[1]):
                    stats[0] += 1
                    pairwise_waiting_removed.append(element)
                    groundtruth_waiting_removed.append(line)
                    break
    
    # Removing all TRUE POSITIVES from the sources files
    for el in pairwise_waiting_removed:
        pairwise_dati.remove(el)
    for line in groundtruth_waiting_removed:
        groundtruth_dati.remove(line)
    
    # Calculating the number of FALSE POSITIVES
    for element in pairwise_dati:
        if element[2] == "1":
            stats[1] += 1
    
    # Calculating the number of FALSE NEGATIVES
    stats[2]=len(groundtruth_dati)

    # Calculation of metrics
    precision = stats[0]/(stats[0]+stats[1])         # PRECISION: measure of how many of the records that the model thought were similar are actually similar
    recall = stats[0]/(stats[0]+stats[2])            # RECALL: measure of how much the model was able to "recover" compared to the total number of actual similar pairs
    if (precision + recall) == 0:
        f_measure = 0
    else:
        f_measure = (2*precision*recall)/(precision + recall)

    return precision, recall, f_measure


# Main function that orchestrate the calculation of metrics for each result obtained
def main():
    groundtruth_file = "evaluation_data/ground_truth.txt"
    base_dir = "evaluation_data/PairwiseMatching_results/"
    stats_file = "evaluation_data/execution_times.txt"

    files = ["LSH_RLT_pairwise_matching.txt","LSH_DITTO_pairwise_matching.txt","QGRAM_RLT_pairwise_matching.txt","QGRAM_DITTO_pairwise_matching.txt"]
    #files = ["LSH_DITTO_pairwise_matching.txt"]
    for file in tqdm(files, desc="Evaluating files"):
        precision, recall, f_measure = evaluation(f"{base_dir}{file}", groundtruth_file)
        with open(stats_file, 'a', encoding='utf-8') as f:
            f.write(f"PRESTAZIONI PER {file}:\n")
            f.write(f"\t\tPRECISION: {precision:.2f}\n")
            f.write(f"\t\tRECALL: {recall:.2f}\n")
            f.write(f"\t\tF-MEASURE: {f_measure:.2f}\n\n")
    
    return


# Script's starter
if __name__ == "__main__":
    main()