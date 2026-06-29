import urllib.request
import urllib.error
import json

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/dangkythi' if False else 'http://127.0.0.1:8000/dangkythi',
    data=json.dumps({
        'malop': 'D22CQCN02',
        'mamh': 'CTDL',
        'trinhdo': 'A',
        'lan': 1,
        'ngaythi': '2030-07-18T17:41:00',
        'thoigian': 60,
        'socauthi': 10
    }).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    res = urllib.request.urlopen(req)
    print("STATUS", res.getcode())
    print(res.read().decode())
except urllib.error.HTTPError as e:
    print("STATUS", e.code)
    print(e.read().decode())
except Exception as e:
    print("ERROR", e)
