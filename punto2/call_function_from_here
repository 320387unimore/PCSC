from requests import post, exceptions
import json
import pandas as pd
import re
import os
import time

os.environ.pop('REQUESTS_CA_BUNDLE', None)
os.environ.pop('CURL_CA_BUNDLE', None)

# ─── CONFIGURAZIONE ────────────────────────────────────────────────────────────
URL = 'https://europe-west8-pcloud2026-495807.cloudfunctions.net/hello_http'

DATA_INIZIO = None   # formato dd/mm/yyyy HH:MM
DATA_FINE   = None   # formato dd/mm/yyyy HH:MM

MAX_RETRIES = 3      # tentativi massimi per ogni riga
RETRY_DELAY = 2      # secondi di attesa tra un retry e l'altro
# ───────────────────────────────────────────────────────────────────────────────

def clean_col(name):
    return re.sub(r'\s*\[.*?\].*', '', name).strip()

def load_csv(filename, label):
    df = pd.read_csv(f'./{filename}', sep=';')
    df.columns = ['timestamp'] + [f'{label}__{clean_col(c)}' for c in df.columns[1:]]
    return df

# ─── CARICAMENTO ───────────────────────────────────────────────────────────────
df_occ    = load_csv('01_occ.csv',       'occupancy')
df_win    = load_csv('02_win.csv',       'windows')
df_light  = load_csv('03_light.csv',     'lighting')
df_plug   = load_csv('04_plug.csv',      'plug_loads')
df_tin    = load_csv('05_temp_in.csv',   'temp_indoor')
df_rhin   = load_csv('06_rhu_in.csv',    'humidity_indoor')
df_rad    = load_csv('07_rad_global.csv','solar_radiation')
df_tout   = load_csv('08_temp_out.csv',  'temp_outdoor')
df_rhout  = load_csv('09_rhu_out.csv',   'humidity_outdoor')
df_wsp    = load_csv('10_wsp.csv',       'wind_speed')
df_wdi    = load_csv('11_wdi.csv',       'wind_direction')

# ─── UNIONE ────────────────────────────────────────────────────────────────────
df = df_occ
for other in [df_win, df_light, df_plug, df_tin, df_rhin,
              df_rad, df_tout, df_rhout, df_wsp, df_wdi]:
    df = df.merge(other, on='timestamp', how='outer')

df = df.sort_values('timestamp').reset_index(drop=True)

# ─── FILTRO DATE ───────────────────────────────────────────────────────────────
if DATA_INIZIO and DATA_FINE:
    df['_dt'] = pd.to_datetime(df['timestamp'], dayfirst=True)
    t0 = pd.to_datetime(DATA_INIZIO, dayfirst=True)
    t1 = pd.to_datetime(DATA_FINE,   dayfirst=True)
    df = df[(df['_dt'] >= t0) & (df['_dt'] <= t1)].drop(columns='_dt')

print(f"Righe da inviare: {len(df)}")

# ─── INVIO CON RETRY ───────────────────────────────────────────────────────────
CATEGORIE = [
    'occupancy', 'windows', 'lighting', 'plug_loads',
    'temp_indoor', 'humidity_indoor', 'solar_radiation',
    'temp_outdoor', 'humidity_outdoor', 'wind_speed', 'wind_direction'
]

errori = []

for i, row in df.iterrows():
    documento = {'timestamp': row['timestamp']}

    for categoria in CATEGORIE:
        cols_cat = [c for c in df.columns if c.startswith(f'{categoria}__')]
        if cols_cat:
            documento[categoria] = {
                c.replace(f'{categoria}__', ''): (
                    None if pd.isna(row[c]) else row[c]
                )
                for c in cols_cat
            }

    successo = False
    for tentativo in range(1, MAX_RETRIES + 1):
        try:
            r = post(URL, data={'data': json.dumps(documento)}, timeout=15)
            if r.status_code == 200:
                print(f"[{i+1}/{len(df)}] {row['timestamp']} → OK")
                successo = True
                break
            else:
                print(f"[{i+1}/{len(df)}] {row['timestamp']} → {r.status_code} {r.text} (tentativo {tentativo})")
        except exceptions.RequestException as e:
            print(f"[{i+1}/{len(df)}] {row['timestamp']} → ERRORE RETE: {e} (tentativo {tentativo})")

        if tentativo < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    if not successo:
        errori.append(row['timestamp'])

# ─── RIEPILOGO FINALE ──────────────────────────────────────────────────────────
print(f"\n✅ Completato. Righe fallite: {len(errori)}")
if errori:
    print("Timestamp non inviati:")
    for ts in errori:
        print(f"  - {ts}")
