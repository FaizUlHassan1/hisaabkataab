# FBR Bridge (Django)

A lightweight API bridge between your Azure-hosted ERP and FBR (Federal Board of Revenue) Digital Invoicing APIs. Deploy this on a server in Pakistan so FBR requests originate from an allowed location.

## Architecture

```
ERP (Azure)  --HTTPS-->  FBR Bridge (Pakistan)  --HTTPS-->  FBR API
```

Your ERP calls this bridge with invoice data. The bridge adds the FBR security token and forwards the request to FBR, then returns FBR's response to your ERP.

## Setup

1. **Install dependencies**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Configure environment**

```bash
cp .env.example .env
# Edit .env with your values
```

Required variables:
- `BRIDGE_API_KEY` — shared secret; your ERP sends this in `X-API-Key`
- `FBR_SECURITY_TOKEN` — from FBR portal (e.fbr.gov.pk) after registration
- `FBR_ENVIRONMENT` — `sandbox`, `sandbox_ssl`, or `production`

3. **Run locally**

```bash
python manage.py runserver 0.0.0.0:8001
```

4. **Production (Gunicorn)**

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8001 --workers 2
```

Use nginx or another reverse proxy in front, with HTTPS.

## API Endpoints

### Health check (no auth)

```
GET /api/health/
```

### Post invoice (convenience)

```
POST /api/v1/fbr/invoices/
X-API-Key: your-bridge-api-key
Content-Type: application/json

{ ... FBR invoice JSON ... }
```

Optional: `?environment=sandbox|sandbox_ssl|production`

### Generic proxy (any FBR endpoint)

```
POST /api/v1/fbr/proxy/
X-API-Key: your-bridge-api-key
Content-Type: application/json

{
  "method": "POST",
  "endpoint_name": "post_invoice",
  "data": { ... }
}
```

`endpoint_name` options: `post_invoice`, `get_invoice_details`  
Or use `endpoint_path` / `full_url` for custom FBR URLs.

### Get invoice details (sandbox)

```
POST /api/v1/fbr/invoices/details/
X-API-Key: your-bridge-api-key
Content-Type: application/json

{ ... query JSON ... }
```

## Response format

```json
{
  "success": true,
  "status_code": 200,
  "data": { ... FBR response ... },
  "fbr_url": "https://esp.fbr.gov.pk:8244/DigitalInvoicing/v1/di/PostInvoiceData_sb"
}
```

## ERP integration example (curl)

```bash
curl -X POST https://your-pakistan-server.com/api/v1/fbr/invoices/ \
  -H "X-API-Key: your-bridge-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "bposid": "YOUR_BPOS_ID",
    "invoiceType": 1,
    "invoiceDate": "2024-02-21T11:43:29.568Z",
    "ntN_CNIC": "1234567891234",
    "buyerSellerName": "Buyer Name",
    "destinationAddress": "Address",
    "saleType": "T1000139",
    "totalSalesTaxApplicable": 0,
    "totalRetailPrice": 0
  }'
```

## FBR whitelisting

Register your Pakistan server IP with FBR (helpline@fbr.gov.pk) per FBR technical specifications. Provide:
- NTN
- Hosting company name
- Public IP
- Server location (Pakistan)

## Security notes

- Keep `BRIDGE_API_KEY` and `FBR_SECURITY_TOKEN` secret; only on the Pakistan server
- Use HTTPS for ERP → bridge communication
- Restrict firewall to allow only your ERP's IP if possible
- Set `DEBUG=False` in production
# hisaabkataab
