import csv
import time
import json
from pathlib import Path

from requests import post


BASE_URL = 'http://localhost:80'
INTERVAL_SECONDS = 3

CSV_FILES = [
    '01_occ.csv',
    '02_win.csv',
    '03_light.csv',
    '04_plug.csv',
    '05_temp_in.csv',
    '06_rhu_in.csv',
    '07_rad_global.csv',
    '08_temp_out.csv',
    '09_rhu_out.csv',
    '10_wsp.csv',
    '11_wdi.csv',
]

# Apre tutti gli 11 file CSV e crea un reader per ognuno
readers = []
for csv_filename in CSV_FILES:
    csv_path = Path(__file__).with_name(csv_filename)
    csv_file = csv_path.open(newline='', encoding='utf-8')
    reader = csv.DictReader(csv_file, delimiter=';')
    sensor_name = csv_path.stem  # es. '01_occ', '02_win', ...
    readers.append((sensor_name, reader))

# Itera riga per riga su tutti i file contemporaneamente
for rows in zip(*[r for _, r in readers]):
    for i, (sensor_name, _) in enumerate(readers):
        row = rows[i]
        timestamp = list(row.values())[0]  # prima colonna = timestamp
        # Tutte le colonne tranne la prima (timestamp) sono valori del sensore
        values = {k: v for j, (k, v) in enumerate(row.items()) if j != 0}
        response = post(
            f'{BASE_URL}/sensors/{sensor_name}',
            data={'data': timestamp, 'val': json.dumps(values)},
        )
        print(f"[{sensor_name}] {timestamp} -> {response.status_code}")
    time.sleep(INTERVAL_SECONDS)