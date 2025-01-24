import mediated_schema_creation
import time

# Funzione principale che orchestra l'intera esecuzione del programma
def main():
    start_time = time.time()
    mediated_schema_creation.schema_creator()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Mediated-Schema created in {execution_time:.6f} secondi")

# Funzione starter dello script che fa partire la funzione principale
if __name__ == "__main__":
    main()