from requests import post
import json

data = {'rh-1': 97, 'rh-2': 99, 'rh-3': 100, 'weekend01': 0}
r = post('https://europe-west8-pcloud2026-495807.cloudfunctions.net/predict_rhu', data={'data': json.dumps(data)})
print(r.status_code)
print(r.text)
