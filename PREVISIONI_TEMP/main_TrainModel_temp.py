#funzione che risponde alla chiamata HTTP per fare il riaddestramento del modello predittivo
def train_model_temp(request):
    import calendar
    from datetime import datetime
    import json
    import os

    import joblib #salva il modello predittivo su file
    import pandas as pd
    from google.cloud import firestore
    from google.cloud import storage
    from sklearn.linear_model import LinearRegression #algoritmo di ML

    #inizia il meccanismo cors
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'Access-Control-Allow-Credentials': 'true'
        }
        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    #estrazione dei dai JSON inviati nella richiesta HTTP 
    request_json = request.get_json(silent=True)
    if request_json is None and 'data' in request.values:
        request_json = json.loads(request.values['data'])

    #connessione al db Firestore test1 e prepara una ricerca nella collezione "tempOut" ordinando i documenti dal più recente al più vecchio
    db = firestore.Client(database='test1')
    query = db.collection('tempOut').order_by('datetime', direction=firestore.Query.DESCENDING)

    #se il client ha inviato una data specifica nel payload verranno presi solo i dati registrati in data pari o inferiore a quella indicata
    if request_json and request_json.get('datetime'):
        training_until = datetime.strptime(request_json['datetime'], '%Y-%m-%d %H:%M:%S')
        query = query.where('datetime', '<=', training_until)

    #si esegue la query che richiede solo gli ultimi 10 documenti più recenti e li converte in una lista chiamata docs
    docs = list(query.limit(10).stream())

    #per creare le predizioni basate sullo storico servono almeno 4 record
    if len(docs) < 4:
        return (json.dumps({'error': 'Not enough documents to train the model'}), 400, headers)

    #riporta i documenti all'ordine iniziale: dal più vecchio al più recente ed estrae i dati con .to_dict() e popola la lista records
    records = []
    for doc in reversed(docs):
        item = doc.to_dict()
        records.append(
            {
                'datetime': item['datetime'],
                'tempOut': float(item['tempOut'])
            }
        )

    #dalla lista otteniamo un DataFrame di pandas, la colonna delle date sono trasformate in un formato temporale riconosciuto da pandas
    df = pd.DataFrame(records)
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime').reset_index(drop=True) #riordina la tabella cronologicamente e resetta gli indici di riga

    df['weekday'] = df['datetime'].apply(lambda value: calendar.day_name[value.weekday()]) #colonna chiamata weekday che contiene il giorno della settimana (lunedì, martedì ecc.)
    df['weekend01'] = df['weekday'].apply(lambda value: 1 if value in ('Saturday', 'Sunday') else 0) #variabile binaria (1 se sabato o domenica, 0 altrimenti)
    df['tempOut-1'] = df['tempOut'].shift(1) #contiene il valore della temperatura della riga precedente
    df['tempOut-2'] = df['tempOut'].shift(2)
    df['tempOut-3'] = df['tempOut'].shift(3)
    df = df.iloc[3:, :].copy() #i primi 3 record della tabella hanno valori vuoti nelle colonne create con lo shift, quindi si eliminano le prime 3 righe della tabella

    #ADDESTRAMENTO DEL MODELLO DI ML

    feature_columns = ['tempOut-1', 'tempOut-2', 'tempOut-3', 'weekend01'] #variabili di input
    model = LinearRegression() #inizializzazione dell'algoritmo di Regressione Lineare
    model.fit(df.loc[:, feature_columns], df['tempOut']) #fase di addestramento: l'algoritmo calcola la temperatura attuale y 

    model_path = os.path.join('/tmp', 'model_temp.pkl') #crea un file binario nella cartella temporanea /tmp della CF 
    joblib.dump(model, model_path) #salva il modello usando joblib

    storage_client = storage.Client()
    bucket = storage_client.bucket('previsioni') #seleziona il bucket "previsioni"
    blob = bucket.blob('model_temp.pkl') #definisce il nome del file di destinazione
    blob.upload_from_filename(model_path) #carica il file del modello salvato precedentemente nella cartella temporanea

    #trova la data più recente usata nell'addestramento, la formatta come stringa e aggiorna il documento "last_train" su Firestore 
    latest_datetime = df['datetime'].max().strftime('%Y-%m-%d %H:%M:%S')
    db.collection('training_temp').document('last_train').set({'last_train': latest_datetime})

    #restituisce una risposta HTTP 200 (successo)
    return (
        json.dumps(
            {
                'message': 'Model trained successfully',
                'documents_used': len(records),
                'rows_used_for_training': len(df),
                'training_until': latest_datetime,
                'model_path': 'gs://previsioni/model_temp.pkl'
            }
        ),
        200,
        headers
    )
