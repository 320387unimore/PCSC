from requests import post
import json
import csv
import time

# indirizzo della Cloud Function
url = 'https://europe-west8-pcloud2026-495807.cloudfunctions.net/connessione_db'

# dizionario che associa ad ogni nome di file CSV il nome del sensore corrispondente
files_config = {
    '01_occ.csv': '01_occ',
    '02_win.csv': '02_win',
    '03_light.csv': '03_light',
    '04_plug.csv': '04_plug',
    '05_temp_in.csv': '05_temp_in',
    '06_rhu_in.csv': '06_rhu_in',
    '07_rad_global.csv': '07_rad_global',
    '08_temp_out.csv': '08_temp_out',
    '09_rhu_out.csv': '09_rhu_out',
    '10_wsp.csv': '10_wsp',
    '11_wdi.csv': '11_wdi',
}

# 1. Apriamo TUTTI i file contemporaneamente e creiamo i relativi reader csv
opened_files = []
readers = []

try:
    # ciclo che itera su ciascun file 
    for filename, sensor_name in files_config.items():
        # si apre il file csv in modalità di lettura (r)
        f = open('data/' + filename, mode='r')
        # aggiungiamo il file aperto alla lista
        opened_files.append(f)
        
        #crea un oggetto reader per leggere il file CSV, specificando il delimitatore come punto e virgola
        reader = csv.reader(f, delimiter=';')
        next(reader)  # Salta l'intestazione di ciascun file
        
        # Salviamo nella lista reader sia il reader che il nome del sensore associato 
        readers.append({'reader': reader, 'sensor': sensor_name})

    # 2. Ciclo infinito o fino a quando ci sono dati nei file
    while True:
        dati_inviati_in_questo_giro = 0
        
        # Passiamo in rassegna ogni sensore, uno alla volta
        for item in readers:
            try:
                # Legge la riga successiva di QUESTO specifico sensore
                row = next(item['reader'])
                
                time_stamp = row[0] #prende il timestamp dalla prima colonna
                values = row[1:] #prende i valori dalla seconda colonna in poi
                sensor = item['sensor'] #recupera il nome del sensore associato a questo reader
                
                # Invia il dato alla Cloud Function
                payload = {'data': json.dumps({'sensor': sensor, 'time': time_stamp, 'value': values})} # Crea il payload per l'invio (dizionario con chiave 'data' e valore JSON)
                r = post(url, data=payload) # Invia la richiesta POST alla Cloud Function con il payload
                
                # Stampa lo stato della richiesta e il testo della risposta (200 se è andato a buon fine)
                print(f"Inviato {sensor} -> Stato: {r.status_code} | {r.text}")
                dati_inviati_in_questo_giro += 1
                
                # Aspetta 3 secondi tra l'invio di un sensore e il successivo
                time.sleep(3)
                
            except StopIteration: #se il comando next() non trova più righe da leggere, genera un'eccezione StopIteration
                # Questo file specifico è terminato, passa al prossimo
                continue
        
        # Se in un intero giro nessun file aveva più righe da leggere, usciamo dal ciclo
        if dati_inviati_in_questo_giro == 0:
            print("Tutti i file CSV sono stati letti completamente.")
            break

finally:
    # 3. Chiudiamo in sicurezza tutti i file aperti alla fine del programma
    for f in opened_files:
        f.close()