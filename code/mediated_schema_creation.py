from openai import OpenAI
from tqdm import tqdm
import os
import json
import xml.etree.ElementTree as ET
import pandas as pd
import re
import time

# Definisce la posizione in cui è memorizzato il comando da dare al modello
prompt = """
Crea uno schema mediato con almeno 20 attributi basato sui seguenti dati:
"""

# Definisce l'API da contattare, quindi il modello con cui si comunica
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="API-KEY",
)

# Funzione che invia messaggi all'LLM e riceve le risposte
def ask_chatbot(table_content, max_retries, wait_time):
    for attempt in range(max_retries):
        completion = client.chat.completions.create(
            model="google/gemini-2.0-flash-thinking-exp:free",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{prompt}\n{table_content}"
                        }
                    ]
                }
            ],
        )
        
        # Verifica se la risposta è valida
        if completion.choices and completion.choices[0]:
            return completion.choices[0].message.content
            
        
        # Attendi prima di ritentare
        time.sleep(wait_time)
    
    # Se fallisce dopo tutti i tentativi, ritorna un valore predefinito o lancia un'eccezione
    print("Errore: Non è stata ottenuta una risposta valida dopo diversi tentativi.")
    return None

# Funzione che re-interroga LLM nel caso in cui questo restituisca messaggi incompleti e gli chiede di completare la risposta
# lasciata incompleta
def ask_chatbot_recovery(continuation_prompt, max_retries, wait_time):
    for attempt in range(max_retries):
        completion = client.chat.completions.create(
            model="google/gemini-2.0-flash-thinking-exp:free",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{prompt}\n{continuation_prompt}"
                        }
                    ]
                }
            ],
        )
        
        # Verifica se la risposta è valida
        if completion.choices and completion.choices[0]:
            return completion.choices[0].message.content
            
        
        # Attendi prima di ritentare
        time.sleep(wait_time)
    
    # Se fallisce dopo tutti i tentativi, ritorna un valore predefinito o lancia un'eccezione
    print("Errore: Non è stata ottenuta una risposta valida dopo diversi tentativi.")
    return None

# Funzione che controlla se una risposta JSON è completa.
def is_response_complete(response):
    try:
        # Utilizza una regex per estrarre il JSON dalla risposta
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            return False
        
        # Prova a fare il parsing del JSON
        json.loads(json_match.group(0))
        return True
    except json.JSONDecodeError as e:
        return False

# Funzione che recupera una risposta incompleta chiedendo al modello di continuare
def recover_incomplete_response(incomplete_response, table_content):
    
    continuation_prompt = f"Continua la risposta incompleta:\n{incomplete_response}\nDalla tabella:\n{table_content}"
    continuation = ask_chatbot_recovery(continuation_prompt, 10, 10)
    if continuation:
        return incomplete_response + continuation
    return "{\u007b\u007d}"

# Funzione per leggere i dati dai file JSON, XML, CSV e JSONL
def read_data(file_path):
    if file_path.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    elif file_path.endswith('.xml'):
        tree = ET.parse(file_path)
        root = tree.getroot()
        return ET.tostring(root, encoding='utf-8').decode('utf-8')
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
        return df.to_json(orient='records')
    elif file_path.endswith('.jsonl'):
        with open(file_path, 'r', encoding='utf-8') as file:
            return [json.loads(line) for line in file]
    else:
        raise ValueError("Formato di file non supportato")

# Funzione principale che legge tutti i file e crea lo schema mediato
def schema_creator(cartella_sorgente):
    all_data = []
    for file in tqdm(os.listdir(cartella_sorgente), desc="Reading data from files"):
        input_file_path = os.path.join(cartella_sorgente, file)
        data = read_data(input_file_path)
        if isinstance(data, list):
            all_data.extend(data)
        else:
            all_data.append(data)
    
    combined_data = "\n".join(json.dumps(item) for item in all_data)
    raw_response = ask_chatbot(combined_data, 10, 10)
    if raw_response:
        if not is_response_complete(raw_response):
            raw_response = recover_incomplete_response(raw_response, combined_data)
        
        with open("mediated_schema.json", 'w', encoding='utf-8') as file:
            file.write(raw_response)
    return raw_response

# Esegui la funzione principale
schema_creator("sources")
