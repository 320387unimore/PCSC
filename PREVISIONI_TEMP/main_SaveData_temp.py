#CLOUD FUNCTION: l'oggetto request contiene i dati inviati dal client
def save_data_temp(request):
    from google.cloud import firestore
    from datetime import datetime
    import json
    #inizia il meccanismo cors
    if request.method == 'OPTIONS':
        print('------ options')
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'Access-Control-Allow-Credentials': 'true'
        }
        return ('', 204, headers)

    request_json = json.loads(request.values['data']) #trasforma la stringa data in un dizionario python
    request_json['datetime'] = datetime.strptime(request_json['datetime'], '%d/%m/%Y %H:%M') #la stringa della data è convertita in datetime
    request_json['tempOut'] = float(request_json['tempOut']) #la temperatura esterna è convertita in float

    print('>>>>>>>>>>>>>>>>>>>>>>>')
    print(request_json)

    headers = {
        'Access-Control-Allow-Origin': '*'
    } #header per la risposta finale

    db = firestore.Client(database='test1') #connessione al db

    sdatetime = request_json['datetime'].strftime('%Y-%m-%d %H:%M:%S') #la data trasformata nel formato Anno-Mese-Giorno Ore:Minuti:Secondi 
    db.collection('tempOut').document(sdatetime).set(request_json) #accede alla collection "tempOut" e crea un documento usando come ID sdatetime

    doc_ref = db.collection('training_temp').document('last_train') #crea un documento "last_train" nella collezione "training_temp" (registra quando è stato addestrato l'ultimo modello)
    doc = doc_ref.get() #accede al documento "last_train"
    if doc.exists: #se esiste
        last_train = doc.to_dict()['last_train'] #estrae la data dell'ultimo addestramento e la salva nella variabile last_train
        print(f"Last train: {last_train}")
    else: #se non esiste
        print("No such document!")
        return ('ok', 200, headers) #si evita il blocco 

    #se la differenza di giorni tra la data del record appena ricevuto e la data dell'ultimo addestramento è maggiore o uguale a 7
    if (request_json['datetime'] - datetime.strptime(last_train, '%Y-%m-%d %H:%M:%S')).days >= 7:
        import requests #richiesta HTTP POST a un'altra Cloud Function (train_model_temp) che riaddestra il modello coi nuovi dati dell'ultima settimana
        r = requests.post('https://europe-west8-pcloud2026-495807.cloudfunctions.net/train_model_temp')
        print(f"Train model response: {r.status_code} - {r.text}")

    return ('ok', 200, headers)
