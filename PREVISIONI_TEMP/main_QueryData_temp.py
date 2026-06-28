def query_data_temp(request):
    from google.cloud import firestore
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
    N = int(request_json['N'])

    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    db = firestore.Client(database='test1')

    docs = db.collection('tempOut').order_by('datetime', direction=firestore.Query.DESCENDING).limit(N).stream()

    results = []
    for doc in docs:
        item = doc.to_dict()
        item['id'] = doc.id
        results.append(item['tempOut'])

    return (json.dumps(results), 200, headers)
