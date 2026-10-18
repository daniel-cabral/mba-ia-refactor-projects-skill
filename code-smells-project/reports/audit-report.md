================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 7 | HIGH: 5 | MEDIUM: 6 | LOW: 5

## Findings

### [CRITICAL] AP06 Unprotected dangerous endpoints
File: app.py:47-57, app.py:59-78
Description: `POST /admin/reset-db` deletes every row of `itens_pedido`, `pedidos`, `produtos` and `usuarios`. `POST /admin/query` executes any SQL string received in the body (`cursor.execute(query)`). Neither has any authentication or authorization check.
Impact: Any anonymous caller can wipe the database, read every table (including passwords) or run arbitrary DDL/DML.
Recommendation: PB05. Remove `/admin/query`; keep `/admin/reset-db` only behind an explicit env flag (disabled by default, returns 403) and an admin token check.

### [CRITICAL] AP02 SQL Injection
File: models.py:28, models.py:47-50, models.py:57-61, models.py:68, models.py:92, models.py:109-111, models.py:126-129, models.py:140, models.py:148-151, models.py:155, models.py:157-166, models.py:174, models.py:188, models.py:192, models.py:220, models.py:224, models.py:279-281, models.py:289-297; app.py:69
Description: Queries are built by string concatenation, e.g. `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"` (models.py:109-111) and `"... WHERE nome LIKE '%" + termo + "%'"` (models.py:291). `/admin/query` runs raw client SQL (app.py:69).
Impact: Login bypass (`' OR '1'='1`), data theft and destruction by any client.
Recommendation: PB02. Use `?` placeholders with a params tuple in every query.

### [CRITICAL] AP01 Hardcoded secrets and credentials
File: app.py:7, controllers.py:289, database.py:76-78
Description: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"` is committed in source and echoed by `/health` (`"secret_key": "minha-chave-super-secreta-123"`). Seed users carry literal passwords (`admin123`, `123456`, `senha123`).
Impact: Anyone with repo access, or any caller of `/health`, obtains the signing key; seeded credentials are publicly known.
Recommendation: PB01. Create a config module reading `SECRET_KEY`, `DB_PATH`, `DEBUG` from env vars with safe dev fallbacks; add `.env.example`.

### [CRITICAL] AP05 Debug mode / insecure server config
File: app.py:8, app.py:88
Description: `app.config["DEBUG"] = True` and `app.run(host="0.0.0.0", port=5000, debug=True)`.
Impact: The Werkzeug debugger is reachable from the network and allows remote code execution.
Recommendation: PB01. Drive debug from `FLASK_DEBUG` env var (default off) and bind to `127.0.0.1` by default.

### [CRITICAL] AP04 Sensitive data exposure
File: models.py:83, models.py:100, controllers.py:130-132, controllers.py:138-140, controllers.py:285-289, controllers.py:12, controllers.py:22, controllers.py:62, controllers.py:96, controllers.py:109, controllers.py:126, controllers.py:134, controllers.py:144, controllers.py:165, controllers.py:186, controllers.py:220, controllers.py:227, controllers.py:235, controllers.py:255, controllers.py:262, controllers.py:292, app.py:78, controllers.py:161, controllers.py:179, controllers.py:182
Description: `GET /usuarios` and `GET /usuarios/<id>` return the `senha` field. `/health` returns `secret_key`, `db_path` and `debug`. Every handler returns `str(e)` to the client. User emails are written to logs.
Impact: Leaks credentials and internals (DB path, exception text, SQL errors) to any caller.
Recommendation: PB04. Drop `senha` from serializers, trim `/health` to status and counts, return generic error messages from the central error handler (log details server-side).

### [CRITICAL] AP03 Plaintext password storage
File: models.py:109-111, models.py:126-129, database.py:75-79
Description: Passwords are stored as received (`INSERT INTO usuarios ... senha ...`) and compared in plaintext in the login query (`AND senha = '...'`). Seed data also stores plaintext.
Impact: A DB leak (or the `/usuarios` endpoint) reveals every password.
Recommendation: PB03. Hash with `werkzeug.security.generate_password_hash` on create and seed, verify with `check_password_hash`.

### [CRITICAL] AP07 God module
File: models.py:1-314, database.py:7-86, app.py:11-78
Description: `models.py` holds products, users, orders and sales report in one module, mixing SQL, business rules (stock check, discount tiers) and serialization. `database.py` mixes connection, schema creation and seed data. `app.py` mixes routing, admin SQL execution and app setup.
Impact: Impossible to test in isolation; any change risks every domain.
Recommendation: PB06. Split into `models/` (one per entity), `controllers/`, `routes/`, `database.py`, `config.py`, `middlewares/`.

### [HIGH] AP12 Broken business invariants
File: models.py:133-169, models.py:242, models.py:275-283, controllers.py:188-220, controllers.py:237-255
Description: `criar_pedido` accepts any `quantidade` (zero or negative values pass the stock check and a negative quantity increases stock), does not verify that `usuario_id` exists, and raises `KeyError`/500 on missing item keys. `atualizar_status_pedido` allows any transition and does not check the order exists; on `cancelado` it only prints "Devolver estoque" without restoring stock. `relatorio_vendas` sums `total` of all orders including cancelled ones. `criar_usuario` does not reject duplicate emails.
Impact: Stock corruption, inflated revenue, orphan orders, duplicate accounts.
Recommendation: PB14. Validate quantity as positive integer, check user and order existence, define allowed status transitions, restore stock on cancel inside a transaction, exclude cancelled orders from revenue, enforce unique email.

### [HIGH] AP08 Business logic in controllers / persistence in routes
File: controllers.py:24-62, controllers.py:64-96, controllers.py:188-220, controllers.py:237-255, controllers.py:264-292, controllers.py:3, app.py:47-78, models.py:133-169, models.py:256-262
Description: Handlers hold validation rules, category list, status list and side-effect "notifications"; `health_check` and the `app.py` admin routes execute SQL via `get_db()` directly; `criar_pedido` (models) mixes stock rules, pricing and persistence; discount tiers are computed in the model's report function.
Impact: Logic cannot be reused or tested without HTTP; violates SRP and MVC.
Recommendation: PB07. Thin controllers delegating to model/service functions; no DB access outside models; move rules to the model layer.

### [HIGH] AP10 Non-atomic multi-step writes
File: models.py:133-169
Description: `criar_pedido` checks stock, inserts into `pedidos`, then loops inserting `itens_pedido` and decrementing stock, committing only at the end with no `rollback()` on failure. The stock check is a read-then-write (TOCTOU) with no atomic `UPDATE ... WHERE estoque >= ?`.
Impact: Partial writes on failure and overselling under concurrent requests.
Recommendation: PB09. Wrap in one transaction with rollback on error and use `UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?` checking `rowcount`.

### [HIGH] AP09 Global mutable state
File: database.py:4-5, database.py:9-11
Description: A single module-level `db_connection` is created lazily through `global db_connection` with `check_same_thread=False`, shared by all requests and threads.
Impact: Not thread-safe; cannot be reconfigured or mocked; schema/seed run as a side effect of the first `get_db()` call.
Recommendation: PB08. Per-request connection (`flask.g` + teardown) and an explicit `init_db()` called by the composition root.

### [HIGH] AP13 Permissive CORS
File: app.py:9
Description: `CORS(app)` with no `origins` on an API exposing destructive and unauthenticated routes.
Impact: Any website can call the API from a victim's browser.
Recommendation: PB01. Restrict origins via a `CORS_ORIGINS` env var (default to none/localhost).

### [MEDIUM] AP14 N+1 queries
File: models.py:187-193, models.py:219-225
Description: `get_pedidos_usuario` and `get_todos_pedidos` run one query for items per order and one product-name query per item.
Impact: Query count grows with orders x items.
Recommendation: PB10. Load items with a single JOIN against `produtos` (or one `IN` query) and group in memory.

### [MEDIUM] AP15 Duplicated logic
File: models.py:12-21, models.py:31-40, models.py:304-313, models.py:79-86, models.py:95-102, models.py:178-200, models.py:211-232, controllers.py:30-54, controllers.py:74-90
Description: The same product row-to-dict mapping appears three times, user mapping twice, the order+items assembly twice (identical), and product validation is copied between create and update.
Impact: Fixes diverge; rules drift (already the case: update skips the name length and category checks).
Recommendation: PB07. Single `row_to_*` helpers and one shared validator.

### [MEDIUM] AP16 Missing or unsafe input validation
File: controllers.py:26-50, controllers.py:66-90, controllers.py:118-121, controllers.py:169-171, controllers.py:239-240, controllers.py:195-201, controllers.py:153-158
Description: Types are not checked (`preco < 0` on a string raises `TypeError` -> 500); `float(preco_min)` has no try; `login` and `atualizar_status_pedido` call `.get` on a possibly `None` JSON body; PUT validation is weaker than POST; no email format check; order items are not validated.
Impact: Bad input becomes 500s or reaches the database.
Recommendation: PB14. Validate body presence and types in one place; return 400 with clear messages.

### [MEDIUM] AP17 No centralized error handling / inconsistent responses
File: controllers.py:5-292, app.py:59-78
Description: The same `try/except Exception: return jsonify({"erro": str(e)}), 500` is repeated in every handler; there is no `@app.errorhandler`. Response shapes vary (`sucesso` present in some errors only; some success bodies lack `dados`).
Impact: Inconsistent API contract, leaked internals, duplicated handling.
Recommendation: PB11. Domain exceptions + `errorhandler` returning a uniform JSON body; remove per-handler try/except.

### [MEDIUM] AP18 Unrestricted resource consumption
File: models.py:7, models.py:75, models.py:206, models.py:174, controllers.py:167-186, app.py:6-9
Description: List endpoints return whole tables with `SELECT *` and no pagination; `/login` has no rate limiting; no `MAX_CONTENT_LENGTH`.
Impact: Response size and memory grow without bound; login can be brute-forced.
Recommendation: PB10. Add `limit`/`offset` with a sane maximum and set `MAX_CONTENT_LENGTH`.

### [MEDIUM] AP25 Missing security headers
File: app.py:6-9
Description: No `after_request` hook sets `X-Content-Type-Options` or `X-Frame-Options`.
Impact: Weaker browser-side protections (MIME sniffing, clickjacking).
Recommendation: PB01. Add a small `after_request` hook setting the headers.

### [LOW] AP19 Magic numbers and strings
File: models.py:257-262, controllers.py:52, controllers.py:242, controllers.py:47-50, app.py:85-88, controllers.py:285
Description: Discount thresholds/rates (`10000`, `0.1`, `5000`, `0.05`, `1000`, `0.02`), category list, status list, name length limits, port and version are inline literals.
Impact: Rules are hard to find and change; lists can drift.
Recommendation: PB15. Named constants in `config.py`/a constants module.

### [LOW] AP20 Print logging
File: controllers.py:8, controllers.py:11, controllers.py:57, controllers.py:61, controllers.py:106, controllers.py:161, controllers.py:179, controllers.py:182, controllers.py:208-210, controllers.py:219, controllers.py:248, controllers.py:250, app.py:56, app.py:83-86
Description: `print(...)` is used for events and errors, including fake "ENVIANDO EMAIL/SMS/PUSH" notifications and user emails concatenated into log lines.
Impact: No levels, no structure; log injection and misleading output.
Recommendation: PB16. Use the `logging` module; drop the fake notifications.

### [LOW] AP21 Poor naming and builtin shadowing
File: controllers.py:14, controllers.py:56, controllers.py:64, controllers.py:98, controllers.py:136, controllers.py:160, models.py:24, models.py:43, models.py:54, models.py:65, models.py:89, models.py:187-191
Description: Parameters and locals named `id` shadow the builtin; `cursor2`/`cursor3` are cryptic.
Impact: Readability and accidental shadowing.
Recommendation: PB15. Rename to `produto_id`/`usuario_id`; reuse a single cursor.

### [LOW] AP22 Dead code and unused imports
File: models.py:2, database.py:2
Description: `import sqlite3` in `models.py` and `import os` in `database.py` are never used.
Impact: Noise.
Recommendation: PB15. Remove the unused imports.

### [LOW] AP23 Deprecated APIs
File: app.py:88, app.py:11-30
Description: `app.run(debug=True)` for configuration -> `FLASK_DEBUG` env var; routes registered on the app object in one big file -> `Blueprint` per resource.
Impact: Harder to configure per environment and to maintain.
Recommendation: PB12.

================================
Total: 23 findings
================================
