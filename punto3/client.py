# File client.py
# Simula il comportamento di 11 sensori che inviano periodicamente
# i propri dati storici (letti da file CSV) a un server Flask,
# rispettando la reale distanza temporale tra le misurazioni.


# Si importano tutte le librerie e moduli necessari per il codice
import csv                          # Permette di leggere i file CSV riga per riga come dizionari
import time                         # permette di far attendere il programma un certo numero di secondi tra un invio e l'altro
import json                         # permette trasformare un dizionario Python in una stringa in formato JSON (e viceversa) da mandare via HTTP
from pathlib import Path            # permette di gestire i percorsi dei file in modo più semplice
from datetime import datetime       # permette di trasformare le stringhe di data/ora in oggetti confrontabili tra loro

from requests import post          # funzione che permette di inviare richieste HTTP di tipo POST al server


# Viene definita una costante che contiene l'indirizzo del server a cui il client deveinviare i dati dei sensori
# "localhost" indica questo stesso computer, "80" è la porta su cui il server è in ascolto
BASE_URL = 'http://localhost:80'


# Viene definita una costante che indica quanti secondi il programma aspetta tra l'invio di un dato e il successivo.
INTERVAL_SECONDS = 3


# Si definisce una costante che indica il formato in cui sono scritte le date nei file CSV: giorno/mese/anno ora:minuto
# Serve a "datetime.strptime" per interpretare correttamente le stringhe di data lette dai file
TIMESTAMP_FORMAT = '%d/%m/%Y %H:%M'

# Array di stringhe, ognuna con il nome di uno degli 11 file CSV, che rappresentano gli 11 sensori
# L'ordine non è importante ai fini della logica: ogni file verrà letto in modo indipendente dagli altri.
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


def parse_timestamp(ts_string):
    # Permette di convertire una stringa di data (es. "01/01/2013 00:00") in un vero
    # oggetto "datetime" di Python. Questo fa si che possano essere confrontati tra loro (es. per capire
    # quale tra due date viene prima) usando <, >, ==.
    return datetime.strptime(ts_string, TIMESTAMP_FORMAT)


# Lista che conterrà un dizionario, per ciascuno degli 11 sensori, contenente: nome del sensore, il suo reader CSV,
# l'ultima riga letta ma non ancora inviata ("next_row"), e se il file è terminato oppure no
sensors = []

# Il ciclo permette di aprire uno per uno tutti gli 11 file CSV e preparare, per ciascuno, gli strumenti
# necessari a leggerlo riga per riga
for csv_filename in CSV_FILES:
    # "__file__" è il percorso di questo stesso script (client.py)
    # ".with_name(csv_filename)" costruisce il percorso del file CSV assumendo
    # che si trovi nella stessa cartella dello script
    csv_path = Path(__file__).with_name(csv_filename)

    # Apre il file CSV in lettura testuale. "newline=''" è la modalità
    # raccomandata quando si usa il modulo "csv", per evitare problemi
    # con gli "a capo" su sistemi operativi diversi
    csv_file = csv_path.open(newline='', encoding='utf-8')

    # Crea un "reader" che, scorrendolo, restituisce ogni riga del file
    # come un dizionario con la struttura: {nome_colonna: valore}
    # "delimiter=';'" indica che nei file le colonne sono separate da punto e virgola
    reader = csv.DictReader(csv_file, delimiter=';')

    # ".stem" restituisce il nome del file senza estensione
    # Es. da "01_occ.csv" ottiene "01_occ": questo diventerà il nome
    # con cui verrà identificato il sensore quando si invieranno i dati al server.
    sensor_name = csv_path.stem

    # Aggiunge alla lista "sensors" una serie di informazioni relative a questo sensore
    # "next_row" è None perché in fase di inizializzazione non è ancora stata letta nessuna riga
    # "exhausted" è False perché in fase di inizializzazione il file non è ancora stato letto tutto
    sensors.append({
        'name': sensor_name,
        'reader': reader,
        'next_row': None,
        'exhausted': False,
    })


def advance(sensor):
    # Questa funzione fa avanzare di una riga la lettura di un solo sensore
    # (ossia quello passato come argomento), leggendo la prossima riga disponibile
    # dal suo file CSV e mettendola dentro sensor['next_row'],
    # pronta per essere confrontata o inviata
    try:
        # "next(sensor['reader'])" chiede al reader la prossima riga del CSV.
        row = next(sensor['reader'])
    except StopIteration:
        # Se il file è finito (ossia non ci sono più righe da leggere), "next()" elimina
        # questo errore: viene segnalato per segnare il sensore come esaurito
        # ed evitare che il programma si blocchi a causa di un errore
        sensor['exhausted'] = True
        sensor['next_row'] = None
        return  # esce subito dalla funzione, in quanto non c'è altro da fare siccome il file è già stato letto tutto

    # "row.values()" restituisce tutti i valori della riga che viene letta, in ordine.
    # "[0]" prende il primo valore, ossia il valore della prima colonna, che nei nostri file è sempre
    # il timestamp (data e ora della misurazione).
    timestamp_str = list(row.values())[0]  # prima colonna = timestamp

    # Costruisce un nuovo dizionario con tutte le colonne tranne la prima in quanto è già stata presa prima
    # "enumerate(row.items())" numera ogni coppia (nome_colonna, valore) tenendo solo quelle con indice j diverso da 0.
    values = {k: v for j, (k, v) in enumerate(row.items()) if j != 0}

    # Salva nelle informazioni del sensore la riga appena letta, in tre forme utili:
    #   - la stringa originale del timestamp (da inviare così com'è al server)
    #   - la versione convertita in oggetto datetime (per poterla confrontare con altre date)
    #   - il dizionario con i valori delle misure di questa riga salvati al passo precedente
    sensor['next_row'] = {
        'timestamp_str': timestamp_str,
        'timestamp': parse_timestamp(timestamp_str),
        'values': values,
    }


# Prima di iniziare il ciclo principale, carichiamo in anticipo la prima riga
# di ogni sensore, così da avere subito un timestamp da confrontare per ciascuno
for sensor in sensors:
    advance(sensor)

# Inizia ora il ciclo principale che continua finché c'è almeno UN sensore che non ha ancora
# esaurito il proprio file CSV (cioè ha ancora righe da inviare).
while any(not s['exhausted'] for s in sensors):

    # Prende solo i sensori ancora attivi (non esauriti, quindi che hanno ancora righe che possono essere inviate), 
    # scartando quelli che hanno già finito le loro righe
    pending = [s for s in sensors if not s['exhausted']]

    # Tra tutti i sensori attivi, trova il timestamp più "vecchio" (ossia il più
    # indietro nel tempo) tra quelli in attesa di essere inviati. Questo permette di salvare 
    # il prossimo istante che bisogna simulare e di cui bisogna salvare i dati
    current_timestamp = min(s['next_row']['timestamp'] for s in pending)

    # Scorre tutti i sensori attivi e invia SOLO quelli il cui prossimo
    # timestamp è esattamente uguale a "current_timestamp" (che è il timestamp più vecchio tra quelli in attesa). 
    # Questo è un punto fondamentale, in questo modo i sensori con misure ogni 15 minuti (ossia 01-06) invieranno molto più
    # spesso dei sensori con misure orarie (ossia 07-11)
    for sensor in pending:
        if sensor['next_row']['timestamp'] == current_timestamp:

            # Invia una richiesta POST al server, all'indirizzo specifico
            # del sensore (es. http://localhost:80/sensors/01_occ).
            response = post(
                f"{BASE_URL}/sensors/{sensor['name']}",
                data={
                    # "data" contiene il timestamp originale, come stringa
                    'data': sensor['next_row']['timestamp_str'],
                    # "val" contiene tutte le altre misure di questa riga,
                    # trasformate in una stringa JSON (in quanto il corpo di una
                    # richiesta HTTP può contenere solo testo)
                    'val': json.dumps(sensor['next_row']['values']),
                },
            )

            # Stampa a schermo un log con: nome del sensore tra parentesi
            # quadre, il timestamp inviato e il codice relativo allostato HTTP ricevuto
            # in risposta dal server (200 = ok, 404 = non trovato, ecc.)
            # Questo permette di controllare se tutto sta funzionando correttamente e se i senrori stanno inviando correttamente i dati al server
            print(f"[{sensor['name']}] {sensor['next_row']['timestamp_str']} -> {response.status_code}")

            # Fa avanzare solo il sensore in analisi alla riga successiva del suo file,
            # in modo che al prossimo giro del ciclo abbia un nuovo timestamp
            # pronto da confrontare con gli altri sensori.
            advance(sensor)

    # Aspetta qualche secondo prima di passare al prossimo istante simulato,
    # questo permette di rendere più realistico il comportamento dei sensori
    time.sleep(INTERVAL_SECONDS)
