from requests import post
import json
from datetime import datetime

url = 'https://europe-west8-pcloud2026-495807.cloudfunctions.net/save_data_temp'
r = post(url, data={'data': json.dumps({'datetime': '01/01/2013 00:00', 'tempOut': '1.6'})})
print(r.status_code)
print(r.text)


