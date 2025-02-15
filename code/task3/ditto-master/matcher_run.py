import subprocess
import time

def run_matcher():
    try:
        # Esegui lo script matcher.py come un sottoprocesso
        subprocess.run(['.venv\\Scripts\\python', 'matcher.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione di matcher.py: {e}")

if __name__ == '__main__':
    start_time = time.time()
    run_matcher()
    end_time = time.time()
    total_time = end_time - start_time
    with open("../../../evaluation_data/execution_times.txt",'a',encoding='utf-8')as f:
        f.write(f"PAIRWISE MATCHING with DITTO on QGRAM BLOCKING executed in {total_time:.2f} seconds\n")