def connessione_db(request):
    from google.cloud import firestore
    import json
    # inizia il meccanismo cors
    if request.method == 'OPTIONS':
        print('------ options')
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
            'Access-Control-Allow-Credentials': 'true'
        }
        return ('', 204, headers)
    
    # inizia il codice
    # il campo data inviato dal client viene trasformato da stringa json in un dizionario
    request_json = json.loads(request.values['data'])
    #log di debug: si stampa il dizionario ricevuto
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print(request_json)
    # header cors anche per la risposta "vera" altrimenti il browser blocca la risposta
    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    # il dizionario ha questa struttura: request_json = {'sensor':'01_occ','time':'01-01-2013 00:00','value':[0,0,0]}
    # crea la connessione al database Firestore
    db = firestore.Client()
    # crea una collection per ogni sensore e dentro la collection crea un documento che come ID il valore di time (ogni riga del CSV è un documento distinto)
    #infine salva l'intero dizionario come contenuto del documento
    db.collection(request_json['sensor']).document(request_json['time']).set(request_json)
    return ('ok', 200, headers)
