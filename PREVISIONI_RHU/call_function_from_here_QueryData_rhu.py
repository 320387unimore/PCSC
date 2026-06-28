from requests import post
import json

import os
import certifi

# Forza Python a usare i certificati corretti di certifi
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['CURL_CA_BUNDLE'] = certifi.where()


url = 'https://europe-west8-pcloud2026-495807.cloudfunctions.net/query_data_rhu'
r = post(url, data={'data': json.dumps({'N': 5})})
print(r.status_code)
r = r.json()
print(r)

url = 'https://europe-west8-pcloud2026-495807.cloudfunctions.net/predict_rhu'
d = {'rh-1': r[0], 'rh-2': r[1], 'rh-3': r[2], 'weekend01': 0}
r = post(url, data={'data': json.dumps(d)})
print(r.status_code)
print(r.text)
