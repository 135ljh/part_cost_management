## IDME Backend (Module 1: Data Configuration - Unit)

### 1) Install

```bash
pip install -r requirements.txt
```

### 2) Run

```bash
uvicorn app.main:app --reload
```

### 3) API Docs

- Swagger: `http://127.0.0.1:8000/docs`
- Health: `GET /health`

### 4) Unit Configuration APIs

- `GET /api/v1/units` - unit list
- `GET /api/v1/units/{unit_id}` - unit detail
- `POST /api/v1/units` - create
- `PUT /api/v1/units/{unit_id}` - update
- `DELETE /api/v1/units/{unit_id}` - delete

### 5) Currency Configuration APIs

- `GET /api/v1/currencies` - currency list
- `GET /api/v1/currencies/{currency_id}` - currency detail
- `POST /api/v1/currencies` - create
- `PUT /api/v1/currencies/{currency_id}` - update
- `DELETE /api/v1/currencies/{currency_id}` - delete

### 6) Exchange Rate Configuration APIs

- `GET /api/v1/exchange-rates` - exchange rate list
- `GET /api/v1/exchange-rates/{rate_id}` - exchange rate detail
- `POST /api/v1/exchange-rates` - create
- `PUT /api/v1/exchange-rates/{rate_id}` - update
- `DELETE /api/v1/exchange-rates/{rate_id}` - delete

### 7) Region Configuration APIs

- `GET /api/v1/regions` - region list
- `GET /api/v1/regions/{region_id}` - region detail
- `POST /api/v1/regions` - create
- `PUT /api/v1/regions/{region_id}` - update
- `DELETE /api/v1/regions/{region_id}` - delete

### 8) Material Category APIs

- `GET /api/v1/material-categories` - material category list
- `GET /api/v1/material-categories/{category_id}` - material category detail
- `POST /api/v1/material-categories` - create
- `PUT /api/v1/material-categories/{category_id}` - update
- `DELETE /api/v1/material-categories/{category_id}` - delete
- `GET /api/v1/material-categories/tree/all` - category tree with material names

### 9) Material APIs

- `GET /api/v1/materials` - material list
- `GET /api/v1/materials/{material_id}` - material detail
- `POST /api/v1/materials` - create
- `PUT /api/v1/materials/{material_id}` - update
- `DELETE /api/v1/materials/{material_id}` - delete

### 10) Database Config

Default database URL:

`mysql+pymysql://root:123456@127.0.0.1:3306/idme?charset=utf8mb4`

You can override it with environment variable `DATABASE_URL`.

### 11) Region Cost Profile APIs

- `GET /api/v1/region-cost-profiles` - list
- `GET /api/v1/region-cost-profiles/{profile_id}` - detail
- `POST /api/v1/region-cost-profiles` - create
- `PUT /api/v1/region-cost-profiles/{profile_id}` - update
- `DELETE /api/v1/region-cost-profiles/{profile_id}` - delete

### 12) Equipment Rate APIs

- `GET /api/v1/equipment-rates` - list
- `GET /api/v1/equipment-rates/{rate_id}` - detail
- `POST /api/v1/equipment-rates` - create
- `PUT /api/v1/equipment-rates/{rate_id}` - update
- `DELETE /api/v1/equipment-rates/{rate_id}` - delete

### 13) Additional Data Config APIs

- `GET/POST /api/v1/equipment-categories` and `GET/PUT/DELETE /api/v1/equipment-categories/{category_id}`
- `GET/POST /api/v1/equipment` and `GET/PUT/DELETE /api/v1/equipment/{equipment_id}`
- `GET/POST /api/v1/equipment-specifications` and `GET/PUT/DELETE /api/v1/equipment-specifications/{spec_id}`
- `GET/POST /api/v1/equipment-cost-profiles` and `GET/PUT/DELETE /api/v1/equipment-cost-profiles/{profile_id}`
- `GET/POST /api/v1/material-prices` and `GET/PUT/DELETE /api/v1/material-prices/{price_id}`
