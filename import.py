import csv
from pathlib import Path

csv_path = Path(__file__).with_name('01_occ.csv')
with csv_path.open(newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter=';')
    row = next(reader)  # legge solo la prima riga di dati
    for k, v in row.items():
        print(repr(k), '->', repr(v))