def predict_rhu(request):
    import joblib
    import json
    from google.cloud import storage

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

    print('>>>>>>>>>>>>>>>>>>>>>>>')
    request_json = json.loads(request.values['data'])
    print(request_json)

    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    def download_model(bucket_name, model_name, destination):
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(model_name)
        blob.download_to_filename(destination)
        print(f"Model {model_name} downloaded to {destination}")

    model_path = '/tmp/model_rhu.pkl'
    download_model('previsioni', 'model_rhu.pkl', model_path)
    model = joblib.load(model_path)

    print(request_json)
    print(request_json['rh-1'])
    yp = model.predict([list(request_json.values())])
    return str(yp[0]), 200, headers
