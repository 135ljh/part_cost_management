from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
code = 'T' + datetime.now().strftime('%H%M%S')

payload = {
    "currency_code": code,
    "currency_name": "test-currency",
    "currency_symbol": "$",
    "precision_scale": 2,
    "is_base_currency": False,
    "is_active": True,
    "remark": "smoke"
}

currency_id = None
r_create = client.post('/api/v1/currencies', json=payload)
print('CREATE', r_create.status_code)
if r_create.status_code == 201:
    currency_id = r_create.json()['id']

if currency_id is not None:
    r_detail = client.get(f'/api/v1/currencies/{currency_id}')
    print('DETAIL', r_detail.status_code)

    r_update = client.put(f'/api/v1/currencies/{currency_id}', json={"currency_name": "test-currency-updated", "currency_symbol": "USD"})
    print('UPDATE', r_update.status_code)

    r_delete = client.delete(f'/api/v1/currencies/{currency_id}')
    print('DELETE', r_delete.status_code)

    r_missing = client.get(f'/api/v1/currencies/{currency_id}')
    print('DETAIL_AFTER_DELETE', r_missing.status_code)
