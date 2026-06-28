from requests import post
import json

url = 'https://europe-west8-pcloud2026-495807.cloudfunctions.net/save_data_rhu'
r = post(url, data={'data': json.dumps({'datetime': '01/01/2013 00:00', 'rh': '97'})})
print(r.status_code)
print(r.text)
