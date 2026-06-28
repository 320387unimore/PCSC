def save_data_temp(request):
    from google.cloud import firestore
    from datetime import datetime
    import json
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

    request_json = json.loads(request.values['data'])
    request_json['datetime'] = datetime.strptime(request_json['datetime'], '%d/%m/%Y %H:%M')
    request_json['tempOut'] = float(request_json['tempOut'])

    print('>>>>>>>>>>>>>>>>>>>>>>>')
    print(request_json)

    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    db = firestore.Client(database='test1')

    sdatetime = request_json['datetime'].strftime('%Y-%m-%d %H:%M:%S')
    db.collection('tempOut').document(sdatetime).set(request_json)

    doc_ref = db.collection('training_temp').document('last_train')
    doc = doc_ref.get()
    if doc.exists:
        last_train = doc.to_dict()['last_train']
        print(f"Last train: {last_train}")
    else:
        print("No such document!")
        return ('ok', 200, headers)

    if (request_json['datetime'] - datetime.strptime(last_train, '%Y-%m-%d %H:%M:%S')).days >= 7:
        import requests
        r = requests.post('https://europe-west8-pcloud2026.cloudfunctions.net/train_model_temp')
        print(f"Train model response: {r.status_code} - {r.text}")

    return ('ok', 200, headers)
