from requests import post

data = {'tempOut-1': 1.6, 'tempOut-2': 1.2, 'tempOut-3': 0.7, 'weekend01': 0}
r = post('https://europe-west8-pcloud2026-495807.cloudfunctions.net/predict_temp', data={'data': __import__('json').dumps(data)})
print(r.status_code)
print(r.text)
