from requests import post

import os
import certifi

# Forza Python a usare il bundle di certificati corretto ed esistente
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['CURL_CA_BUNDLE'] = certifi.where()


payload = {'datetime': '2013-01-15 00:00:00'}
r = post('https://europe-west8-pcloud2026-495807.cloudfunctions.net/train_model_rhu', json=payload)
print(r.status_code)
print(r.text)
