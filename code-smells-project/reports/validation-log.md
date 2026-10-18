# Validation log

Start command: `.venv\Scripts\python.exe app.py` (original: `python app.py`) | Port: 5000 | Fresh state: `loja.db` deleted before each run; the app seeds 10 products and 3 users at boot

## Expected deltas
- POST /admin/query: 200 -> 403 (guarded unless `ADMIN_ENABLED=1`, PB05)
- POST /admin/reset-db: 200 -> 403 (guarded unless `ADMIN_ENABLED=1`, PB05)
- GET /usuarios, GET /usuarios/<id>: field `senha` removed (PB04)
- GET /health: fields `secret_key`, `db_path`, `debug` removed (PB04)
- Non-2xx bodies standardized from `{"erro": ..., "sucesso": false}` to `{"error": ...}` (PB11)
- Intentional behavior fixes (not exercised by the happy-path plan; checked in the extra checks below): quantity must be a positive integer, unknown user/order -> 404, duplicate email -> 409, invalid status transition -> 409, cancelling an order returns stock, revenue excludes cancelled orders, list endpoints are capped at 100 rows, product PUT now applies the same validation as POST, passwords are stored hashed.

## Results
| # | Request | Baseline | After | Shape | Result |
| --- | --- | --- | --- | --- | --- |
| 1 | GET /health | 200 | 200 | fields removed | PASS (expected delta) |
| 2 | GET / | 200 | 200 | same | PASS |
| 3 | GET /produtos | 200 | 200 | same | PASS |
| 4 | GET /produtos/busca?q=Mouse&preco_min=10&preco_max=500 | 200 | 200 | same | PASS |
| 5 | GET /produtos/1 | 200 | 200 | same | PASS |
| 6 | GET /produtos/9999 | 404 | 404 | error body standardized | PASS (expected delta) |
| 7 | GET /usuarios | 200 | 200 | `senha` removed | PASS (expected delta) |
| 8 | GET /usuarios/1 | 200 | 200 | `senha` removed | PASS (expected delta) |
| 9 | GET /pedidos | 200 | 200 | same | PASS |
| 10 | GET /pedidos/usuario/2 | 200 | 200 | same | PASS |
| 11 | GET /relatorios/vendas | 200 | 200 | same | PASS |
| 12 | POST /produtos | 201 | 201 | same | PASS |
| 13 | POST /produtos (invalid body) | 400 | 400 | error body standardized | PASS (expected delta) |
| 14 | GET /produtos/11 | 200 | 200 | same | PASS |
| 15 | POST /usuarios | 201 | 201 | same | PASS |
| 16 | POST /pedidos | 201 | 201 | same | PASS |
| 17 | GET /pedidos | 200 | 200 | same | PASS |
| 18 | GET /pedidos/usuario/2 | 200 | 200 | same | PASS |
| 19 | PUT /produtos/11 | 200 | 200 | same | PASS |
| 20 | PUT /pedidos/1/status | 200 | 200 | same | PASS |
| 21 | GET /relatorios/vendas | 200 | 200 | same | PASS |
| 22 | POST /login (seed credentials) | 200 | 200 | same | PASS |
| 23 | POST /login (wrong password) | 401 | 401 | error body standardized | PASS (expected delta) |
| 24 | POST /admin/query | 200 | 403 | n/a | PASS (expected delta) |
| 25 | DELETE /produtos/11 | 200 | 200 | same | PASS |
| 26 | POST /admin/reset-db | 200 | 403 | n/a | PASS (expected delta) |

Boot: PASS (no traceback in reports/boot-after.log)
Summary: 26/26 PASS (18 identical, 8 with expected deltas only; no unexpected status or shape differences)

## Extra checks (Flask test client, temp DB, `ADMIN_ENABLED=1`)
- Login with `' OR '1'='1' --` -> 401 (SQL injection closed)
- POST /pedidos with quantity -5 -> 400; quantity 999 -> 400 "Estoque insuficiente"
- Order of 3 units: stock 10 -> 7; cancel -> stock back to 10; cancelled -> aprovado -> 409
- PUT /pedidos/99/status -> 404; duplicate email -> 409; price as string -> 400
- Admin routes with `ADMIN_ENABLED=1`: /admin/query -> 200, /admin/reset-db -> 200
- Responses carry `X-Content-Type-Options` and `X-Frame-Options`
