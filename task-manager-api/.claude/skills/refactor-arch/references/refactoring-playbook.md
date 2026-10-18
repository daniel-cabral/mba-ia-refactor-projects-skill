# Refactoring playbook

Used in Phase 3. Each pattern maps catalog ids (`anti-patterns.md`) to a concrete transformation with before/after code. Apply the variant that matches the project's stack; adapt names to the project, never copy example names blindly.

## Rules for every transformation

- Keep the endpoint contract (paths, methods, success status and response shape), except for removing sensitive fields and standardizing error bodies.
- Prefer stdlib / framework built-ins. Add a dependency only when unavoidable and record why in the final output.
- After each pattern that touches boot-critical code (config, app creation, DB), boot the app before continuing.

## Index

| Id | Pattern | Fixes |
| --- | --- | --- |
| PB01 | Extract configuration to environment | AP01, AP05, AP13, AP25 |
| PB02 | Parameterize queries and never execute input | AP02, AP24 |
| PB03 | Hash passwords with a slow salted algorithm | AP03 |
| PB04 | Strip sensitive fields and hide internals | AP04 |
| PB05 | Guard dangerous routes and whitelist writable fields | AP06 |
| PB06 | Split a God class/module into MVC layers | AP07 |
| PB07 | Move logic out of handlers into controllers/models | AP08, AP15 |
| PB08 | Replace global state with injected dependencies | AP09 |
| PB09 | Wrap multi-step writes in a transaction | AP10 |
| PB10 | Fix N+1 and bound queries | AP14, AP18 |
| PB11 | Centralized error handling | AP17 |
| PB12 | Replace deprecated APIs | AP23 |
| PB13 | Callbacks to async/await with error propagation | AP11 |
| PB14 | Validate input and enforce invariants at the boundary | AP12, AP16 |
| PB15 | Named constants, clear names, remove dead code | AP19, AP21, AP22 |
| PB16 | Structured logging instead of print | AP20 |

---

## PB01 Extract configuration to environment

Fixes AP01 (hardcoded secrets), AP05 (debug), AP13 (CORS). Secrets come from env vars. If a secret is missing, generate a random dev value and warn (never reuse the old literal). Write `.env.example` listing every variable.

Python, before:

```python
app = Flask(__name__)
app.config["SECRET_KEY"] = "my-super-secret"
CORS(app)
app.run(host="0.0.0.0", port=5000, debug=True)
```

Python, after (`config/settings.py` + entry point):

```python
# config/settings.py
import os, secrets, logging

class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    DATABASE_URL = os.environ.get("DATABASE_URL", "app.db")
    ADMIN_ENABLED = os.environ.get("ADMIN_ENABLED", "0") == "1"

if "SECRET_KEY" not in os.environ:
    logging.warning("SECRET_KEY not set; using a random development key")
```

```python
# app.py
app.config.from_object(Settings)
CORS(app, origins=Settings.CORS_ORIGINS)
if __name__ == "__main__":
    app.run(host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG)
```

JS, before:

```js
module.exports = { dbPass: "prod_pass_123", paymentKey: "pk_live_abc", port: 3000 };
```

JS, after:

```js
// src/config/index.js
const crypto = require("crypto");
module.exports = {
  port: Number(process.env.PORT || 3000),
  dbPath: process.env.DB_PATH || ":memory:",
  paymentKey: process.env.PAYMENT_GATEWAY_KEY || "",
  sessionSecret: process.env.SESSION_SECRET || crypto.randomBytes(32).toString("hex"),
  adminEnabled: process.env.ADMIN_ENABLED === "1",
};
```

## PB02 Parameterize queries and never execute input

Fixes AP02, AP24. Every value goes through placeholders. Endpoints that execute request-supplied code or SQL are guarded by PB05.

Python, before:

```python
cursor.execute("SELECT * FROM users WHERE email = '" + email + "' AND password = '" + pwd + "'")
cursor.execute(f"SELECT * FROM products WHERE name LIKE '%{term}%'")
```

Python, after:

```python
cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
cursor.execute("SELECT * FROM products WHERE name LIKE ?", (f"%{term}%",))
```

JS, before:

```js
db.all(`SELECT * FROM courses WHERE id = ${req.params.id}`, cb);
```

JS, after:

```js
db.all("SELECT * FROM courses WHERE id = ?", [req.params.id], cb);
```

Dynamic filters: build the WHERE clause from a fixed list of column names and keep values in a params list. Never interpolate column names from input.

## PB03 Hash passwords with a slow salted algorithm

Fixes AP03. Use framework built-ins. Seed users must be stored hashed so login with the seed credentials keeps working. Remove default passwords.

Python, before:

```python
user.password = hashlib.md5(pwd.encode()).hexdigest()
cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, pwd))
```

Python, after:

```python
from werkzeug.security import generate_password_hash, check_password_hash

user.password = generate_password_hash(pwd)
ok = check_password_hash(user.password, candidate)
```

JS, before:

```js
function badHash(p) { let h = ""; for (let i = 0; i < 10000; i++) h += Buffer.from(p).toString("base64").slice(0, 2); return h.slice(0, 10); }
const hash = badHash(pwd || "123456");
```

JS, after:

```js
const crypto = require("crypto");
function hashPassword(pwd) {
  const salt = crypto.randomBytes(16).toString("hex");
  const hash = crypto.scryptSync(pwd, salt, 64).toString("hex");
  return `${salt}:${hash}`;
}
function verifyPassword(pwd, stored) {
  const [salt, hash] = stored.split(":");
  const candidate = crypto.scryptSync(pwd, salt, 64);
  return crypto.timingSafeEqual(candidate, Buffer.from(hash, "hex"));
}
```

## PB04 Strip sensitive fields and hide internals

Fixes AP04. Serializers never include password/hash/token fields. Health endpoints report status only. Errors return a generic message; details go to the server log. Logs never contain card numbers, passwords or keys.

Before:

```python
def to_dict(self):
    return {"id": self.id, "email": self.email, "password": self.password}

return jsonify({"status": "ok", "secret_key": app.config["SECRET_KEY"], "db_path": DB})
```

After:

```python
def to_dict(self):
    return {"id": self.id, "email": self.email}

return jsonify({"status": "ok"})
```

JS, before:

```js
console.log(`Charging card ${card} with key ${config.paymentKey}`);
```

JS, after:

```js
logger.info("Charging card ending in %s", card.slice(-4));
```

## PB05 Guard dangerous routes and whitelist writable fields

Fixes AP06. Only these route classes get the guard: admin routes (`/admin/*`, admin reports), raw SQL or code execution, DB reset / bulk wipe, account (user) deletion. They keep their path but return 403 unless explicitly enabled by config.

Normal resource CRUD (create/update/delete of products, tasks, categories, orders...) is **not** guarded and keeps working.

A missing authentication system (no login/token verification anywhere) is reported as CRITICAL but is out of scope for Phase 3: list it under Remaining Findings with the reason "requires an authentication design (out of scope); dangerous routes guarded meanwhile". Writable fields are whitelisted; privileged fields are never taken from public requests.

Python, after:

```python
# middlewares/guards.py
from functools import wraps
from flask import current_app, jsonify

def admin_only(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_app.config.get("ADMIN_ENABLED"):
            return jsonify({"error": "Forbidden"}), 403
        return fn(*args, **kwargs)
    return wrapper

@bp.post("/admin/reset-db")
@admin_only
def reset_db(): ...
```

JS, after:

```js
// src/middlewares/adminOnly.js
const config = require("../config");
module.exports = (req, res, next) =>
  config.adminEnabled ? next() : res.status(403).json({ error: "Forbidden" });

router.delete("/api/users/:id", adminOnly, userController.remove);
```

Mass assignment, before:

```python
user.role = data.get("role", "user")
```

After:

```python
ALLOWED_FIELDS = {"name", "email", "password"}
payload = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}
user.role = "user"  # privileged fields are set only by admin flows
```

## PB06 Split a God class/module into MVC layers

Fixes AP07. One file/class per responsibility per domain. Target trees are in `mvc-guidelines.md`.

Before (one module):

```python
# models.py: DB connection, SQL, validation, discounts, formatting for products, users and orders
def create_order(user_id, items): ...
def sales_report(): ...
def login(email, pwd): ...
```

After:

```text
models/order_model.py        # SQL for orders only
models/user_model.py         # SQL for users only
controllers/order_controller.py   # order flow: validate, call model, apply rules
controllers/report_controller.py
views/order_routes.py        # HTTP: parse request, call controller, return JSON
```

JS, before:

```js
class AppManager { initDb() {} setupRoutes(app) { app.post("/api/checkout", (req, res) => { /* SQL + payment + response */ }); } }
```

JS, after:

```text
src/config/index.js
src/db/connection.js
src/models/userModel.js, courseModel.js, enrollmentModel.js, paymentModel.js
src/controllers/checkoutController.js, reportController.js, userController.js
src/routes/index.js
src/middlewares/errorHandler.js
src/app.js   # composition root
```

## PB07 Move logic out of handlers into controllers/models

Fixes AP08, AP15. Route handler = parse input, call controller, map result to HTTP. Controller = flow and business rules. Model = data access and entity rules. Duplicated blocks become one function in the right layer.

Before:

```python
@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    total = 0
    for item in data["items"]:
        row = db.execute("SELECT price, stock FROM products WHERE id = ?", (item["id"],)).fetchone()
        if row["stock"] < item["qty"]:
            return jsonify({"error": "no stock"}), 400
        total += row["price"] * item["qty"]
    db.execute("INSERT INTO orders (total) VALUES (?)", (total,))
    db.commit()
    return jsonify({"total": total}), 201
```

After:

```python
# views/order_routes.py
@bp.post("/orders")
def create_order():
    order = order_controller.create(request.get_json(silent=True) or {})
    return jsonify(order), 201

# controllers/order_controller.py
def create(payload):
    items = validate_items(payload.get("items"))
    return order_model.create_with_items(items)   # raises DomainError on stock issues
```

## PB08 Replace global state with injected dependencies

Fixes AP09. Create shared resources once in the composition root (or per request via the framework's context) and pass them in.

Python, before:

```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect("app.db", check_same_thread=False)
    return db_connection
```

Python, after:

```python
from flask import g, current_app

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_URL"])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# app factory: app.teardown_appcontext(close_db)
```

JS, before:

```js
let globalCache = {};
class AppManager { constructor() { this.db = new sqlite3.Database(":memory:"); } }
```

JS, after:

```js
// src/app.js (composition root)
const db = createConnection(config.dbPath);
const userModel = createUserModel(db);
const checkoutController = createCheckoutController({ userModel, enrollmentModel, paymentModel });
app.use(createRoutes({ checkoutController, reportController, userController }));
```

## PB09 Wrap multi-step writes in a transaction

Fixes AP10. All writes of one business operation commit together or roll back together. Replace check-then-act with an atomic conditional update.

Python, before:

```python
if product["stock"] >= qty:
    cursor.execute("INSERT INTO orders ...")
    cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, pid))
db.commit()
```

Python, after:

```python
with db:  # sqlite3 connection as context manager: commit or rollback
    cur = db.execute(
        "UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?", (qty, pid, qty)
    )
    if cur.rowcount == 0:
        raise DomainError("Insufficient stock")
    db.execute("INSERT INTO orders ...")
```

SQLAlchemy: use `db.session.begin()` or commit once at the end and `db.session.rollback()` in the error path.

JS, after:

```js
await run(db, "BEGIN");
try {
  const userId = await userModel.create(user);
  await enrollmentModel.create(userId, courseId);
  await paymentModel.create(userId, amount, "PAID");
  await run(db, "COMMIT");
} catch (err) {
  await run(db, "ROLLBACK");
  throw err;
}
```

## PB10 Fix N+1 and bound queries

Fixes AP14, AP18. Replace per-row queries with a JOIN, `IN (...)` or eager loading. Aggregate in SQL, not in loops.

Python (raw SQL), before:

```python
for order in orders:
    items = db.execute("SELECT * FROM order_items WHERE order_id = ?", (order["id"],)).fetchall()
    for it in items:
        product = db.execute("SELECT name FROM products WHERE id = ?", (it["product_id"],)).fetchone()
```

After:

```python
rows = db.execute("""
    SELECT oi.order_id, oi.quantity, oi.unit_price, p.name AS product_name
    FROM order_items oi JOIN products p ON p.id = oi.product_id
    WHERE oi.order_id IN (SELECT id FROM orders)
""").fetchall()
# group rows by order_id in one pass
```

SQLAlchemy, before:

```python
for t in Task.query.all():
    user = User.query.get(t.user_id)
```

After:

```python
from sqlalchemy.orm import joinedload
tasks = db.session.execute(select(Task).options(joinedload(Task.user))).scalars().all()
```

Counts per group: `SELECT category_id, COUNT(*) FROM tasks GROUP BY category_id` instead of one `count()` per category.

## PB11 Centralized error handling

Fixes AP17. Domain errors are raised in controllers/models; one handler maps them to HTTP. Error envelope: `{"error": "<message>"}`. Unexpected errors are logged and return a generic 500.

Python, after:

```python
# middlewares/error_handler.py
class DomainError(Exception):
    status = 400

class NotFoundError(DomainError):
    status = 404

def register_error_handlers(app):
    @app.errorhandler(DomainError)
    def handle_domain(err):
        return jsonify({"error": str(err)}), err.status

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        app.logger.exception("Unhandled error")
        return jsonify({"error": "Internal server error"}), 500
```

Handlers lose their `try/except Exception: return {"erro": str(e)}, 500` blocks.

JS, after:

```js
// src/middlewares/errorHandler.js
module.exports = (err, req, res, next) => {
  const status = err.status || 500;
  if (status >= 500) console.error(err);
  res.status(status).json({ error: status >= 500 ? "Internal server error" : err.message });
};

// src/app.js, after all routes
app.use(errorHandler);
```

Express 4 does not catch rejected promises: wrap async handlers.

```js
const asyncHandler = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
```

## PB12 Replace deprecated APIs

Fixes AP23. Use the replacement column of the AP23 table. Common cases:

```python
# before
created_at = db.Column(db.DateTime, default=datetime.utcnow)
user = User.query.get(user_id)
# after
created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
user = db.session.get(User, user_id)
```

```js
// before
const self = this;
db.get(sql, params, function (err, row) { self.handle(row); });
// after
const row = await get(db, sql, params);
this.handle(row);
```

## PB13 Callbacks to async/await with error propagation

Fixes AP11. Promisify the driver once; every error either propagates to the error handler or is handled explicitly. Never send success after ignoring `err`.

JS, before:

```js
db.get("SELECT * FROM courses WHERE id = ?", [cid], (err, course) => {
  db.get("SELECT * FROM users WHERE email = ?", [email], (err, user) => {
    db.run("INSERT INTO enrollments ...", [], (err) => {
      res.status(200).json({ msg: "ok" }); // err ignored
    });
  });
});
```

JS, after:

```js
// src/db/connection.js
const get = (db, sql, p = []) => new Promise((ok, ko) => db.get(sql, p, (e, r) => (e ? ko(e) : ok(r))));
const all = (db, sql, p = []) => new Promise((ok, ko) => db.all(sql, p, (e, r) => (e ? ko(e) : ok(r))));
const run = (db, sql, p = []) => new Promise((ok, ko) => db.run(sql, p, function (e) { e ? ko(e) : ok(this); }));

// controller
async function checkout(input) {
  const course = await courseModel.findById(input.courseId);
  if (!course) throw new NotFoundError("Course not found");
  ...
}
```

Python: replace `except: pass` with specific exceptions, or let the error reach PB11.

## PB14 Validate input and enforce invariants at the boundary

Fixes AP12, AP16. Validate type, presence and range before any logic. Return 400 with a clear message. Enforce business rules (positive quantities, credential checks on existing accounts, allowed status transitions) in the controller.

Python, before:

```python
data = request.get_json()
if data["price"] < 0: ...
qty = item["quantity"]
```

Python, after:

```python
def require_number(data, field, minimum=None):
    value = data.get(field)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise DomainError(f"'{field}' must be a number")
    if minimum is not None and value < minimum:
        raise DomainError(f"'{field}' must be >= {minimum}")
    return value

data = request.get_json(silent=True)
if not isinstance(data, dict):
    raise DomainError("JSON body required")
price = require_number(data, "price", minimum=0)
```

JS, after:

```js
function validateCheckout(body) {
  const { name, email, courseId, card } = body || {};
  if (typeof name !== "string" || !name.trim()) throw new ValidationError("name is required");
  if (typeof email !== "string" || !/^\S+@\S+\.\S+$/.test(email)) throw new ValidationError("invalid email");
  if (!Number.isInteger(Number(courseId))) throw new ValidationError("invalid courseId");
  if (typeof card !== "string" || !/^\d{12,19}$/.test(card)) throw new ValidationError("invalid card");
  return { name, email, courseId: Number(courseId), card };
}
```

Existing account in a public flow: verify the password before acting on that account.

## PB15 Named constants, clear names, remove dead code

Fixes AP19, AP21, AP22.

Before:

```python
if total > 10000: discount = total * 0.1
def get(id): ...
import os, sys, json
```

After:

```python
DISCOUNT_TIERS = [(10_000, 0.10), (5_000, 0.05), (1_000, 0.02)]
ORDER_STATUSES = ("pending", "approved", "shipped", "delivered", "cancelled")

def get_product(product_id): ...
# unused imports removed
```

JS: `let u = req.body.usr` becomes `const { name } = req.body`. Remove exports and dependencies that nothing uses.

## PB16 Structured logging instead of print

Fixes AP20.

```python
# before
print("Order created: " + str(order_id))
# after
import logging
logger = logging.getLogger(__name__)
logger.info("Order created: %s", order_id)
```

```js
// before
console.log("Processing payment for " + email);
// after: one small logger module, no sensitive data
logger.info("Processing payment", { userId });
```
