# funzione che risponde alla richiesta HTTP per generare una nuova previsione 
def predict_temp(request):
    import joblib
    import json
    from google.cloud import storage

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

    #estrae la stringa "data" e la converte nel dizionario "request_json" contenente le feature necessarie alla previsione
    print('>>>>>>>>>>>>>>>>>>>>>>>')
    request_json = json.loads(request.values['data'])
    print(request_json)

    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    #funzione che si connette a Google Cloud Storage 
    def download_model(bucket_name, model_name, destination):
        client = storage.Client() #instanzia il client di storage
        bucket = client.bucket(bucket_name) #punta al bucket 
        blob = bucket.blob(model_name) #trova il file del modello binario
        blob.download_to_filename(destination) #scarica il modello
        print(f"Model {model_name} downloaded to {destination}")

    model_path = '/tmp/model_temp.pkl' #definisce il percorso di destinazione locale nella cartella temporanea /temp
    download_model('previsioni', 'model_temp.pkl', model_path) #invoca la funzione appena definita per scaricare il file binario da Cloud
    model = joblib.load(model_path) #si legge il modello e si rende pronto all'uso in Python

    print(request_json)
    print(request_json['tempOut-1'])
    yp = model.predict([list(request_json.values())]) #estrae i valori numerici del dizionario inviato dal client, li racchiude in una lista e li passa al metodo .predict()
    #infine il modello applica l'equazione calcolata durante il training per ottenere un valore stimato yp
    return str(yp[0]), 200, headers
