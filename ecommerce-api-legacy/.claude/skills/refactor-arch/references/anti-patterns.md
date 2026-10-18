# Anti-pattern catalog

Used in Phase 2. Each entry has an id, a severity, concrete detection signals and a pointer to the fix in `refactoring-playbook.md`.

## How to use

1. For each entry, search the source with the signals (grep-style), then **read the surrounding code to confirm**. A signal is a lead, not a finding.
2. Record exact `file:line` (or `file:start-end`) for every confirmed location. Never estimate line numbers.
3. One finding per anti-pattern id, listing all its locations. Do not create one finding per occurrence.
4. If an entry has no confirmed location, omit it. Do not report speculative findings.
5. Also report problems that match no entry but clearly fit a severity definition (e.g. a business rule bug). Use id `AP-X` and justify the severity.

## Severity scale

| Severity | Meaning |
| --- | --- |
| CRITICAL | Security or architecture failure: exposes data or credentials, allows unauthorized actions, or completely breaks separation of concerns. |
| HIGH | Strong MVC/SOLID violation or reliability bug: heavy logic in the wrong layer, tight coupling, global mutable state, data corruption risk. |
| MEDIUM | Duplication, performance (N+1, unbounded queries), missing validation, inadequate error handling or middleware. |
| LOW | Readability: naming, magic numbers, logging style, dead code, deprecated APIs with a drop-in replacement. |

## Summary

| Id | Anti-pattern | Severity | Fix |
| --- | --- | --- | --- |
| AP01 | Hardcoded secrets and credentials | CRITICAL | PB01 |
| AP02 | SQL injection | CRITICAL | PB02 |
| AP03 | Plaintext or weak password storage, weak crypto | CRITICAL | PB03 |
| AP04 | Sensitive data exposure | CRITICAL | PB04 |
| AP05 | Debug mode / insecure server and transport config | CRITICAL | PB01 |
| AP06 | Unprotected dangerous endpoints and broken access control | CRITICAL | PB05 |
| AP07 | God class / God module | CRITICAL | PB06 |
| AP08 | Business logic in routes or controllers (fat handlers) | HIGH | PB07 |
| AP09 | Global mutable state and hidden coupling (no DI) | HIGH | PB08 |
| AP10 | Non-atomic multi-step writes | HIGH | PB09 |
| AP11 | Swallowed errors and callback hell | HIGH | PB13 |
| AP12 | Broken business invariants | HIGH | PB14 |
| AP13 | Permissive CORS on sensitive API | HIGH | PB01 |
| AP14 | N+1 queries | MEDIUM | PB10 |
| AP15 | Duplicated logic | MEDIUM | PB07 |
| AP16 | Missing or unsafe input validation | MEDIUM | PB14 |
| AP17 | No centralized error handling / inconsistent responses | MEDIUM | PB11 |
| AP18 | Unrestricted resource consumption | MEDIUM | PB10 |
| AP19 | Magic numbers and strings | LOW | PB15 |
| AP20 | Print/console logging | LOW | PB16 |
| AP21 | Poor naming and builtin shadowing | LOW | PB15 |
| AP22 | Dead code, unused or outdated dependencies | LOW | PB15 |
| AP23 | Deprecated APIs | LOW | PB12 |
| AP24 | Code/command injection, unsafe deserialization, path traversal | CRITICAL | PB02 |
| AP25 | Missing security headers | MEDIUM | PB01 |

---

## CRITICAL

### AP01 Hardcoded secrets and credentials

- Signals (any language): string literals assigned to names matching `secret|key|password|passwd|pass|token|api_key|smtp|dbPass|credential`; `SECRET_KEY = "..."`; `app.config['SECRET_KEY'] = '...'`; config objects with literal passwords; live-looking keys (`pk_live_`, `sk_`).
- Also check: secrets echoed in responses (health/status endpoints) or seed files with real-looking passwords.
- Not a finding: values read from `os.environ`, `os.getenv`, `process.env`.
- Why: anyone with repo access gets the credentials; session signing can be forged.

### AP02 SQL injection

- Python signals: `execute(` whose argument is built with `+`, `%`, `.format(` or an f-string containing a variable; `"... WHERE x = '" + var + "'"`.
- JS signals: `db.run|get|all|query(` with template literals `` `${var}` `` or `+` concatenation inside SQL.
- Not a finding: placeholders (`?`, `%s`, `:name`) with a separate params argument; ORM query builders.
- Why: login bypass, data theft and destruction.

### AP03 Plaintext or weak password storage

- Signals: password columns stored as received (`INSERT ... senha|password ... VALUES (?)` with the raw value); `hashlib.md5|sha1(` on passwords; custom "hash" functions (loops over base64, `substring`); comparison of plaintext (`WHERE password = ?` with raw input); default passwords (`|| "123456"`).
- Weak crypto signals: `hashlib.md5|sha1` or `createHash('md5'|'sha1')` for anything security-related; `createCipher(`. Predictable tokens (`random`, `Math.random()`, `'token-' + id`) belong to AP06.
- Why: a DB leak reveals every password; MD5/SHA1 unsalted is cracked instantly; predictable tokens can be guessed.

### AP04 Sensitive data exposure

- Signals: serializers (`to_dict`, row-to-dict mapping, `res.json(user)`) that include `password|senha|pass|hash|token`; health/debug endpoints returning secrets, DB paths or debug flags; `str(e)` / `err.message` / stack traces returned to the client; logs printing card numbers, passwords, keys or emails.
- Why: leaks credentials and internals; card data in logs breaks PCI-DSS.

### AP05 Debug mode / insecure server config

- Python signals: `debug=True` in `app.run(`; `app.config['DEBUG'] = True`; `host='0.0.0.0'` together with debug.
- JS signals: stack traces enabled in responses; `NODE_ENV` never checked.
- Transport signals: `verify=False` (requests), `ssl._create_unverified_context`, `rejectUnauthorized: false`, `NODE_TLS_REJECT_UNAUTHORIZED`.
- Why: the Werkzeug debugger allows remote code execution.

### AP06 Unprotected dangerous endpoints and broken access control

- Signals: routes that execute raw SQL from the request body; routes that drop, reset or bulk-delete data; `admin`/`report`/`delete` routes with no auth check; user creation or update that accepts `role`/`is_admin` from the request (mass assignment); fake or guessable tokens (`'token-' + str(id)`, `random`/`Math.random()` for tokens).
- Mass assignment signals: `Model(**request.json)`, `setattr` loop over the payload, `obj.update(request.json)`; `new Model(req.body)`, `Object.assign(obj, req.body)`, `Model.create(req.body)`; any privileged field (`role`, `is_admin`, `active`) set from the request.
- Object-level access (BOLA/IDOR) signals: handlers loading a record by URL id (`get(id)`, `findById(req.params.id)`) and modifying or returning it with no owner check against the authenticated user. Confirm by reading.
- Auth config signals: `jwt.decode(..., verify=False)`, `algorithms=['none']`, tokens without expiry, session cookies with `secure`/`httpOnly` false.
- Why: any caller can destroy data, read everything or escalate to admin.

### AP07 God class / God module

- Signals: one class or file that mixes at least three of: DB connection/schema, SQL queries, business rules, HTTP routing, payment/notification side effects, reporting; files much larger than the rest of the project that cover multiple domains (users + products + orders in one place).
- Why: impossible to test in isolation; any change risks everything.

### AP24 Code/command injection, unsafe deserialization, path traversal

- Python signals: `eval(`, `exec(`, `pickle.loads(`, `yaml.load(` without `SafeLoader`, `os.system(`, `os.popen(`, `subprocess.*(..., shell=True)` with interpolated input; `open(`/`send_file(` with a path from `request.*`.
- JS signals: `eval(`, `new Function(`, `vm.runIn*`, `child_process.exec(` / `execSync(` with template literals; `res.sendFile(` / `fs.*(` with `req.params|query|body` and no fixed root.
- Why: remote code execution or arbitrary file read.

## HIGH

### AP08 Business logic in routes or controllers (fat handlers)

- Signals: route handlers that contain validation rules, price/discount calculations, status transitions, persistence calls (`session.add`, `commit`, `execute`, `db.run`) and serialization in the same function; handlers longer than ~30 lines; a `services/` layer that exists but is not used by the routes.
- Leaky abstraction signals (both directions): controllers/routes importing the DB driver or session (`sqlite3`, `cursor`, `db.session`) directly; models or services importing HTTP objects (`flask.request`, `req`, `res`, `jsonify`).
- Long method / long parameter list (> ~50 lines, > 5 params) in handlers counts here.
- Why: logic cannot be reused or tested without HTTP; violates SRP and MVC.

### AP09 Global mutable state and hidden coupling (no DI)

- Signals: `global` keyword; module-level mutable objects (`cache = {}`, `items = []`, `let total = 0`) mutated by functions; a single shared DB connection created at module level (`check_same_thread=False`); classes instantiating their own dependencies (`new Database(...)` in a constructor, SMTP config in `__init__`).
- Why: not thread-safe, grows without bound, cannot be mocked or reconfigured.

### AP10 Non-atomic multi-step writes

- Signals: several `INSERT`/`UPDATE` (or `db.run` chains) for one business operation without an explicit transaction; check-then-act on stock or uniqueness (read, compare, then write) without an atomic `UPDATE ... WHERE stock >= ?` or a unique constraint (TOCTOU race); `commit()` only on the success path with no `rollback()`.
- Why: partial writes on failure (orphan rows, oversell, users created for failed payments).

### AP11 Swallowed errors and callback hell

- Signals: callbacks that receive `err` and ignore it; responses sent with success regardless of `err`; 4+ levels of nested callbacks; `except: pass` or `except Exception` that hides the cause; results used without checking the error (`rows.length` when `rows` may be undefined).
- Why: failures are reported as success or crash the process.

### AP12 Broken business invariants

- Signals: quantities, prices or amounts accepted without range checks (negative, zero, non-numeric); operations on existing accounts that skip credential checks; status changes without allowed-transition check; reports that aggregate records that should be excluded (cancelled, unpaid).
- Why: corrupts data or allows abuse through valid-looking requests.

### AP13 Permissive CORS on sensitive API

- Signals: `CORS(app)` with no `origins`; `app.use(cors())` with no options; `Access-Control-Allow-Origin: *` on an API that has destructive or unauthenticated routes.
- Why: any website can call the API from a victim's browser.

## MEDIUM

### AP14 N+1 queries

- Signals: a query inside a `for` loop over the result of another query; lazy relationship access in a loop (`len(user.tasks)`, `Model.query.get(row.fk)` per row); nested callbacks issuing one query per row.
- Why: query count grows with data size.

### AP15 Duplicated logic

- Signals: the same row-to-dict mapping, validation block or calculation copied in several functions; helpers that exist but are not used while their logic is re-implemented inline; model methods duplicated as inline logic in routes.
- Why: fixes diverge; rules drift.

### AP16 Missing or unsafe input validation

- Signals: `request.get_json()` / `req.body` used without a None/type check; `int(...)`/`float(...)` on query params without try; comparisons on unvalidated types (`preco < 0` where `preco` may be a string); no email/format checks; PUT validation weaker than POST; redirects to request-supplied URLs (`redirect(request.args[...])`, `res.redirect(req.query...)`).
- Why: bad input becomes a 500 or reaches the DB.

### AP17 No centralized error handling / inconsistent responses

- Signals: the same `try/except Exception: return {"erro": str(e)}, 500` in every handler; no `@app.errorhandler` / Express error middleware; bare `except:`; mixed plain-text and JSON responses; wrong status codes (404 for DB errors, 200 for creation).
- Why: inconsistent API contract; hides errors; duplicated handling.

### AP18 Unrestricted resource consumption

- Signals: `SELECT *` or `.all()` on whole tables returned directly by list endpoints; no `limit`/pagination parameters; login or expensive routes without rate limiting (no `express-rate-limit`, `flask-limiter` or equivalent); `express.json()` without `limit`, Flask without `MAX_CONTENT_LENGTH`; CPU-heavy synchronous work on the request path.
- Why: response size, memory and CPU grow without bound; brute force on login is unthrottled.

### AP25 Missing security headers

- Signals: Express without `helmet` (or manual headers) and with `x-powered-by` enabled; Flask without `X-Content-Type-Options` / `X-Frame-Options` set in an `after_request` hook.
- Fix without new dependencies: `app.disable('x-powered-by')` and a small middleware/`after_request` setting the headers.

## LOW

### AP19 Magic numbers and strings

- Signals: numeric literals in business rules (discount tiers, thresholds, lengths); status/role/category lists repeated inline; constants defined but unused.

### AP20 Print/console logging

- Signals: `print(` or `console.log(` used for application events, errors or fake notifications; user input concatenated into log lines (log injection); no log entry for failed logins or denied access.

### AP21 Poor naming and builtin shadowing

- Signals: single-letter or cryptic names for domain data (`u`, `e`, `cc`, `cid`); parameters named `id`, `type`, `list`, `input` (Python builtins); mixed languages in identifiers; `const self = this`.

### AP22 Dead code, unused imports and dependencies

- Signals: imports never referenced; functions/services never called (grep for usages); dependencies in the manifest never imported; exported variables never read; abandoned packages (e.g. `request` on npm); unpinned versions (`*`, `latest`) or no lock file.

### AP23 Deprecated APIs

Report each deprecated usage with its modern replacement.

| Stack | Deprecated | Replacement |
| --- | --- | --- |
| Python 3.12+ | `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| SQLAlchemy 2.0 | `Model.query.get(id)` | `db.session.get(Model, id)` |
| SQLAlchemy 2.0 | `Model.query.filter(...)` (legacy Query API) | `db.session.execute(select(Model).where(...))` |
| Flask | `app.run(debug=True)` for configuration | `FLASK_DEBUG` env var / `flask run` |
| Flask | routes registered on the app object in a big file | `Blueprint` per resource |
| Node.js | `new Buffer(...)` | `Buffer.from(...)` / `Buffer.alloc(...)` |
| Node.js | `var` | `const` / `let` |
| Node.js | callback-style DB APIs (`sqlite3` callbacks) | Promises / `async`/`await` (wrapper or promise-based driver) |
| Express | `body-parser` package | `express.json()` / `express.urlencoded()` |
| Express | `res.send(status, body)` / `res.json(status, body)` | `res.status(code).json(body)` |
| JS | `const self = this` to capture context | arrow functions |
| Python 3.12+ | `datetime.utcfromtimestamp(ts)` | `datetime.fromtimestamp(ts, timezone.utc)` |
| SQLAlchemy 2.0 | `from sqlalchemy.ext.declarative import declarative_base` | `sqlalchemy.orm.DeclarativeBase` |
| SQLAlchemy 2.0 | `engine.execute(...)`, `conn.execute("raw sql string")` | `conn.execute(text(...))` inside `with engine.connect()` |
| Flask-SQLAlchemy 3 | `Model.query.get_or_404(id)` | `db.get_or_404(Model, id)` |
| Flask 2.3+ | `@app.before_first_request` (removed) | setup in the app factory or `with app.app_context()` |
| Flask 3.0 | `from flask import Markup, escape` (removed) | `from markupsafe import Markup, escape` |
| Werkzeug 2.1+ | `werkzeug.security.safe_str_cmp` (removed) | `hmac.compare_digest` |
| Node.js | `url.parse()` | `new URL()` |
| Node.js | `crypto.createCipher()` (removed in Node 22) | `crypto.createCipheriv()` |
| npm | `request` package (deprecated) | built-in `fetch` |
| Express 5 | `app.del()` | `app.delete()` |
| Express 5 | `req.param(name)` | `req.params` / `req.body` / `req.query` |
| Express 5 | `res.send(status)`, `res.json(obj, status)` | `res.sendStatus(status)`, `res.status(status).json(obj)` |
| Express 4 | async handlers without error forwarding (rejections are not caught) | wrap with `next(err)` or upgrade to Express 5 |
