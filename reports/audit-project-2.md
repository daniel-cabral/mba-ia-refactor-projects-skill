================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express ^4.18.2
Files:   3 analyzed | ~183 lines of code

## Summary
CRITICAL: 5 | HIGH: 5 | MEDIUM: 5 | LOW: 5

## Findings

### [CRITICAL] AP01 Hardcoded secrets and credentials
File: src/utils.js:2-5
Description: The `config` object holds literal credentials: `dbUser: "admin_master"`, `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"` and `smtpUser: "no-reply@fullcycle.com.br"`. Nothing is read from `process.env`.
Impact: Anyone with repo access gets the production DB password and a live payment gateway key.
Recommendation: PB01. Create a config module that reads these values from env vars with safe dev fallbacks, and add `.env.example`.

### [CRITICAL] AP03 Plaintext or weak password storage
File: src/utils.js:17-23, src/AppManager.js:18, src/AppManager.js:68
Description: `badCrypto` "hashes" by looping 10000 times over `Buffer.from(pwd).toString('base64').substring(0, 2)` and truncating to 10 chars. The result depends only on the first 2 base64 chars (about 3 password bytes) and is unsalted. A missing password defaults to `"123456"` (`badCrypto(p || "123456")`). The seeded user is stored in plaintext: `INSERT INTO users ... VALUES ('Leonan', ..., '123')`.
Impact: Passwords are effectively stored in the clear. Many different passwords collide on the same hash, and anyone can guess one. Users created without a password get a known default.
Recommendation: PB03. Use `crypto.scryptSync` with a per-user salt (no new dependencies), hash the seed password too, and reject a missing password.

### [CRITICAL] AP04 Sensitive data exposure
File: src/AppManager.js:45
Description: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)` writes the full card number and the live gateway key to the logs.
Impact: Card data in logs breaks PCI-DSS and leaks the gateway key to anyone who can read the logs.
Recommendation: PB04/PB16. Never log the card number or the key. If a log line is needed, use at most the last 4 digits.

### [CRITICAL] AP06 Unprotected dangerous endpoints and broken access control
File: src/AppManager.js:131-137, src/AppManager.js:80-129
Description: `DELETE /api/users/:id` deletes any user with no authentication or authorization. `GET /api/admin/financial-report` returns every student, payment and revenue figure with no auth check.
Impact: Any anonymous caller can destroy user data and read all financial data.
Recommendation: PB05. Guard both routes with an admin guard middleware (an `x-admin-token` header compared against an env-configured token, 403 otherwise). A full authentication system is out of scope and will be listed as remaining.

### [CRITICAL] AP07 God class / God module
File: src/AppManager.js:4-139
Description: `AppManager` creates the DB connection (`new sqlite3.Database(':memory:')`), defines the schema and seeds data (`initDb`), registers HTTP routes (`setupRoutes`), implements checkout and payment rules, creates users, writes audit logs and builds the financial report.
Impact: Nothing can be tested in isolation, and any change touches every concern.
Recommendation: PB06. Split into config, database, models (user, course, enrollment, payment, audit), controllers, routes and middlewares.

### [HIGH] AP08 Business logic in routes or controllers (fat handlers)
File: src/AppManager.js:28-78, src/AppManager.js:80-129
Description: The checkout handler (about 50 lines) validates input, looks up the course and user, creates the user, decides the payment status (`cc.startsWith("4")`), and inserts the enrollment, payment and audit log, all in one function. The report handler runs the queries and aggregates revenue inline. Both call `this.db` directly.
Impact: The logic cannot be reused or tested without HTTP, and the code violates SRP and MVC.
Recommendation: PB07. Move the flow to a checkout controller/service and the aggregation to a report controller. Keep the route handlers thin.

### [HIGH] AP09 Global mutable state and hidden coupling (no DI)
File: src/utils.js:9-10, src/utils.js:12-15, src/utils.js:25, src/AppManager.js:7, src/app.js:8-10
Description: `globalCache = {}` is mutated by `logAndCache` and grows without bound. `totalRevenue` is a module-level `let`. `AppManager` builds its own DB in the constructor instead of receiving it.
Impact: The cache has no eviction. The in-memory state is shared across requests, and the DB cannot be mocked or reconfigured.
Recommendation: PB08. Remove the global cache/state (or make it a bounded injectable). Inject the DB handle from the composition root.

### [HIGH] AP10 Non-atomic multi-step writes
File: src/AppManager.js:50-57, src/AppManager.js:69
Description: Checkout does 3 or 4 separate writes (user, enrollment, payment, audit log) without a transaction. The user is inserted at line 69 before the payment is evaluated. A DENIED card (line 48) leaves a newly created user behind, and a failure at line 54 leaves an enrollment without a payment.
Impact: Orphan users, enrollments without payments and inconsistent data.
Recommendation: PB09. Wrap the checkout writes in `BEGIN`/`COMMIT` with `ROLLBACK` on error. Decide the payment status before any write.

### [HIGH] AP11 Swallowed errors and callback hell
File: src/AppManager.js:57, src/AppManager.js:92-94, src/AppManager.js:104, src/AppManager.js:106, src/AppManager.js:133-135, src/AppManager.js:37-63
Description: The audit-log callback ignores `err` and returns success (line 57). In the report, `enrollments.length` is read without checking `err` (line 94), and the user and payment lookups ignore `err` (lines 104, 106). The delete route ignores `err` and always answers that the user was deleted (line 133). The checkout nests 7 levels of callbacks.
Impact: Failures are reported as success or crash the process (`enrollments` undefined), and the report may never respond.
Recommendation: PB13. Use async/await over a promisified DB wrapper and propagate errors to the central error handler.

### [HIGH] AP12 Broken business invariants
File: src/AppManager.js:40-74, src/AppManager.js:131-137
Description: When the email already exists, checkout enrolls that account without checking any credential (`pwd` is ignored). An unauthenticated caller can enroll a victim's account. Deleting a user leaves its enrollments and payments behind, as the response itself admits (line 135). The same course can be enrolled twice by the same user.
Impact: Data corruption and account abuse through valid-looking requests.
Recommendation: PB14. Verify the password for existing users, forbid duplicate enrollments, and delete the user's dependent rows together with the user in one transaction.

### [MEDIUM] AP14 N+1 queries
File: src/AppManager.js:83-126
Description: The financial report runs one enrollments query per course, then one user query and one payment query per enrollment.
Impact: The query count grows with the data size (1 + C + 2E queries).
Recommendation: PB10. Replace with one JOIN query (courses, enrollments, users, payments) and aggregate in memory.

### [MEDIUM] AP16 Missing or unsafe input validation
File: src/AppManager.js:29-35
Description: Checkout only tests truthiness of `usr`, `eml`, `c_id` and `card`. There is no type check, no email format check, and no card format check. `pwd` is optional. The user id in `DELETE /api/users/:id` is not validated as an integer.
Impact: Malformed input reaches the DB, and strings or objects can be passed as ids.
Recommendation: PB14. Validate types and formats in the controller and return a 400 with a JSON error.

### [MEDIUM] AP17 No centralized error handling / inconsistent responses
File: src/AppManager.js:35, 38, 41, 48, 51, 55, 70, 87, 135, src/app.js:5-14
Description: Errors are plain-text strings (`res.status(500).send("Erro DB")`) while success is JSON. The delete route returns 200 text. The 404 for a DB error (line 38) mixes up its causes. No Express error middleware exists.
Impact: The API contract is inconsistent, and unexpected exceptions return Express's HTML error page.
Recommendation: PB11. Add a JSON error-handling middleware plus a 404 handler, and use one error shape such as `{ error: "..." }`.

### [MEDIUM] AP18 Unrestricted resource consumption
File: src/AppManager.js:83, src/AppManager.js:92, src/app.js:6, src/utils.js:19-21
Description: The report returns every course, enrollment and student without pagination (`SELECT * FROM courses`). `express.json()` has no body size limit. There is no rate limiting on checkout. `badCrypto` runs a 10000-iteration synchronous loop per new user on the request path.
Impact: Response size, memory and CPU are unbounded, and checkout can be brute-forced.
Recommendation: PB10. Set `express.json({ limit })`, and use pagination on the report and a simple rate limit on checkout.

### [MEDIUM] AP25 Missing security headers
File: src/app.js:5-6
Description: No security headers are set and `x-powered-by` is still enabled.
Impact: The server fingerprint is exposed and the API lacks basic browser hardening.
Recommendation: PB01. Call `app.disable('x-powered-by')` and add a small middleware setting `X-Content-Type-Options` and `X-Frame-Options`.

### [LOW] AP19 Magic numbers and strings
File: src/utils.js:6, src/utils.js:19, src/utils.js:22, src/AppManager.js:46, src/AppManager.js:68
Description: Literals `10000`, `10`, `3000`, `"123456"`, `startsWith("4")`, and the status strings `'PAID'`/`'DENIED'` are repeated inline (also lines 21, 108).
Impact: The rules are hard to read and change.
Recommendation: PB15. Name them as constants (e.g. `PAYMENT_STATUS`, `CARD_APPROVED_PREFIX`).

### [LOW] AP20 Print/console logging
File: src/app.js:13, src/AppManager.js:45, src/utils.js:13
Description: `console.log` is used for application events and for the payment step. User-controlled ids go into the log text, and no log entry exists for errors.
Impact: There are no log levels or structure, and a risk of log injection.
Recommendation: PB16. Use a small logger module with levels. Do not log sensitive values.

### [LOW] AP21 Poor naming and builtin shadowing
File: src/AppManager.js:29-33, src/AppManager.js:26, src/AppManager.js:52, src/app.js:13
Description: Cryptic names `u`, `e`, `p`, `cid`, `cc`, `enrId`, `self` (`const self = this`). Messages mix Portuguese and English, and the startup message calls the app "Frankenstein LMS".
Impact: The code is harder to read.
Recommendation: PB15. Rename to `name`, `email`, `password`, `courseId`, `cardNumber`, and use arrow functions instead of `self`.

### [LOW] AP22 Dead code, unused imports and dependencies
File: src/utils.js:3-5, src/utils.js:10, src/utils.js:25, src/AppManager.js:2
Description: `totalRevenue` is imported in `AppManager.js` and exported but never used. `dbUser`, `dbPass` and `smtpUser` are never read. `globalCache` is exported but only written, never read.
Impact: Noise, and secrets that serve no purpose.
Recommendation: PB15. Remove unused exports, imports and config entries.

### [LOW] AP23 Deprecated APIs
File: src/AppManager.js:37-137, src/AppManager.js:26
Description: Callback-style sqlite3 API -> Promises with async/await; `const self = this` -> arrow functions.
Impact: Hard-to-maintain callback code, and unhandled errors in Express 4.
Recommendation: PB12/PB13. Wrap `sqlite3` in a promise helper and use async handlers with error forwarding.

================================
Total: 20 findings
================================
