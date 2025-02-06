from datasketch import MinHash, MinHashLSH
import pandas as pd

#################### Section of the script where we define the auxiliary functions #############################################

#################### Section of the script where we define the various blocking logics #########################################
def lsh_blocking(df,blocking_output_file):
    return

def QGram_blocking(df,blocking_output_file):
    return

#################### Section of the script where we orchestrate the various blocking logic  ####################################

''' Orchestrator '''
def main():
    df = pd.read_csv("data/mediated_schema_populated.csv", usecols=["name"])
    lsh_blocking(df, "data/blocking_results/lsh_blocking_results.json")
    QGram_blocking(df,"data/blocking_results/QGram_blocking_results.json")
    
    return

''' Script's starter '''
if __name__ == "__main__":
    main()