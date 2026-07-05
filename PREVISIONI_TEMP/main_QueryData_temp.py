#funzione che si attiva alla richiesta HTTP (l'oggetto request contiene i parametri di input passati dal client, cioè il numero di dati da prelevare)
def query_data_temp(request):
    from google.cloud import firestore
    import json
    #inizia il meccanismo CORS
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

    #la stringa data che viene dalla richiesta HTTP lo decodifica in un dizionario python
    request_json = json.loads(request.values['data'])
    N = int(request_json['N']) #estrae dal dizionario il valore associato alla chiave N (che indica quanti ricord si vogliono leggere)

    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    #connessione al db
    db = firestore.Client(database='test1')

    #query: accede alla collezione "tempOut", ordina i documenti in base al campo "datetime" in ordine decrescente, applica un limite di risultati pari a N, si scaricano i documenti salvandoli nella variabile docs
    docs = db.collection('tempOut').order_by('datetime', direction=firestore.Query.DESCENDING).limit(N).stream()

    results = [] #lista vuota che conterrà le temperature estratte
    for doc in docs: #cicla tutti i documenti restituiti dalla query
        item = doc.to_dict() #trasforma il contenuto del documento in un dizionario python
        item['id'] = doc.id #aggiunge una chiave al dizionario che è l'ID del documento
        results.append(item['tempOut']) #aggiunge alla lista results il valore della temperatura esterna

    return (json.dumps(results), 200, headers) #converte la lista di numeri in una stringa JSON e la invia al client insieme al codice di stato HTTP (200) e agli header del cors
