import time
import os

# Definisci il percorso della cartella 'sources' rispetto alla cartella 'code'
sources_path = os.path.join(os.path.dirname(__file__), '..', 'sources')

# Funzione principale che orchestra l'intera esecuzione del programma
def main():
    start_time = time.time()
    # call function for mediated schema creation
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Mediated-Schema created in {execution_time:.6f} secondi")

# Funzione starter dello script che fa partire la funzione principale
if __name__ == "__main__":
    main()
