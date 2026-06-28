import csv
import json
import time
from pathlib import Path
from requests import post

import os
import certifi

# Forza Python a usare il bundle di certificati corretto ed esistente
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['CURL_CA_BUNDLE'] = certifi.where()

F_URL = 'https://europe-west8-pcloud2026-495807.cloudfunctions.net/save_data_temp'
CSV_PATH = Path(__file__).with_name('08_temp_out.csv')
INTERVAL_SECONDS = 3


with CSV_PATH.open(newline='', encoding='utf-8') as csv_file:
    reader = csv.DictReader(csv_file, delimiter=';')
    for row in reader:
        print(row)
        response = post(
            F_URL,
            data={'data': json.dumps({'datetime': row['timestamp [dd/mm/yyyy HH:MM]'], 'tempOut': row['tempOut [C]']})},
        )
        print(f"{row['timestamp [dd/mm/yyyy HH:MM]']} -> {response.status_code}")
        time.sleep(INTERVAL_SECONDS)
