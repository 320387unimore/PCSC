import csv
import json
import time
from pathlib import Path
from requests import post

#URL della Cloud Function che elabora le temperature e gestisce il retraining del modello
F_URL = 'https://europe-west8-pcloud2026-495807.cloudfunctions.net/save_data_temp'
CSV_PATH = Path(__file__).with_name('08_temp_out.csv')
INTERVAL_SECONDS = 3

#file CSV aperto in modalità di lettura 
with CSV_PATH.open(newline='', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file, delimiter=';') #lettore speciale che trasforma le righe del CSV in dizionari, con le intestazioni come chiavi
    for row in reader: #crea un dizionario con le righe del CSV, con le intestazioni come chiavi e i valori delle celle come valori; converte il dizionario in stringa JSON e invia tutto tramite una richiesta HTTP POST alla Cloud Function
        print(row)
        response = post(
            F_URL,
            data={'data': json.dumps({'datetime': row['timestamp [dd/mm/yyyy HH:MM]'], 'tempOut': row['tempOut [C]']})},
        )
        print(f"{row['timestamp [dd/mm/yyyy HH:MM]']} -> {response.status_code}")
        time.sleep(INTERVAL_SECONDS)
