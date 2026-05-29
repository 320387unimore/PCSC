def hello_http(request):
    from google.cloud import firestore
    import json
    import re

    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET,POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600',
        }
        return ('', 204, headers)

    headers = {'Access-Control-Allow-Origin': '*'}

    try:
        request_json = json.loads(request.values['data'])
    except Exception as e:
        return (f'Errore parsing JSON: {e}', 400, headers)

    db = firestore.Client(database='prova4')

    timestamp = request_json.get('timestamp', '')
    # Rende il timestamp sicuro come ID documento Firestore
    # Es: "01/01/2013 23:34" → "01-01-2013_23-34"
    safe_id = re.sub(r'/', '-', timestamp).replace(':', '-').replace(' ', '_')

    CATEGORIE = [
        'occupancy', 'windows', 'lighting', 'plug_loads',
        'temp_indoor', 'humidity_indoor', 'solar_radiation',
        'temp_outdoor', 'humidity_outdoor', 'wind_speed', 'wind_direction'
    ]

    # Usa un batch per scrivere tutte le categorie in una sola operazione atomica
    batch = db.batch()
    for categoria in CATEGORIE:
        if categoria in request_json:
            doc_ref = (
                db.collection('sensori')
                  .document(categoria)
                  .collection('rilevazioni')
                  .document(safe_id)
            )
            dati = {'timestamp': timestamp, **request_json[categoria]}
            batch.set(doc_ref, dati)

    batch.commit()
    return ('ok', 200, headers)
