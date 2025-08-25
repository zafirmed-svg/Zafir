import json
import urllib.request
import urllib.error

BASE = 'http://127.0.0.1:8001/api'

def get(path):
    url = BASE + path
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return None, str(e)

def post(path, data):
    url = BASE + path
    data_bytes = json.dumps(data).encode()
    req = urllib.request.Request(url, data=data_bytes, headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return None, str(e)

if __name__ == '__main__':
    print('GET /api/')
    status, body = get('/')
    print(status)
    print(body)

    print('\nPOST /api/quotes/create')
    payload = {
        'procedure_name': 'Test Procedure',
        'surgery_duration_hours': 2,
        'anesthesia_type': 'General',
        'facility_fee': 1000.0,
        'equipment_costs': 200.0,
        'anesthesia_fee': 100.0,
        'other_costs': 0.0,
        'created_by': 'smoke_test',
        'notes': 'Created by smoke test'
    }
    status, body = post('/quotes/create/', payload)
    print(status)
    print(body)

    print('\nGET /api/quotes/')
    status, body = get('/quotes/')
    print(status)
    print(body)
