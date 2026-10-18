================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0
Files:   15 analyzed | ~1150 lines of code

## Summary
CRITICAL: 5 | HIGH: 4 | MEDIUM: 6 | LOW: 5

## Findings

### [CRITICAL] AP06 Unprotected dangerous endpoints and broken access control
File: routes/user_routes.py:52, routes/user_routes.py:71-78, routes/user_routes.py:119-125, routes/user_routes.py:134-151, routes/user_routes.py:210, routes/task_routes.py:225-238, routes/report_routes.py:211-223
Description: No endpoint has an authentication or authorization check. `POST /users` and `PUT /users/<id>` take `role` and `active` straight from the request body (`role = data.get('role', 'user')`, `user.role = data['role']`, `user.active = data['active']`), so any caller can create an admin or promote themselves. `DELETE /users/<id>` also deletes all of that user's tasks, and `DELETE /tasks/<id>` and `DELETE /categories/<id>` are open. `POST /login` returns the guessable token `'fake-jwt-token-' + str(user.id)`, which nothing verifies.
Impact: Any anonymous client can escalate to admin, delete users, tasks and categories, and forge a token for any user id.
Recommendation: PB05. Reject `role`/`active` in the public create and update paths (or require an admin). Guard the destructive routes (DELETE users/tasks/categories) with an admin check (403 without it). Replace the fake token with a signed, expiring token, or list the missing authentication system as remaining.

### [CRITICAL] AP04 Sensitive data exposure
File: models/user.py:21, routes/user_routes.py:33, routes/user_routes.py:85, routes/user_routes.py:129, routes/user_routes.py:209
Description: `User.to_dict()` includes `'password': self.password`. It is returned by `GET /users/<id>`, `POST /users`, `PUT /users/<id>` and `POST /login`.
Impact: The password hash of any user is readable by anyone, and the hash is MD5, which is trivially cracked.
Recommendation: PB04. Remove `password` from `to_dict()` and every response.

### [CRITICAL] AP03 Weak password storage and weak crypto
File: models/user.py:29, models/user.py:32, seed.py:19, seed.py:26, seed.py:33
Description: `set_password` and `check_password` use unsalted `hashlib.md5(pwd.encode()).hexdigest()`. The seed users get the same MD5 hashes with trivial passwords ('1234', 'abcd', 'pass').
Impact: A leaked database reveals every password almost instantly (rainbow tables and brute force on MD5).
Recommendation: PB03. Use `werkzeug.security.generate_password_hash` / `check_password_hash` (salted PBKDF2/scrypt, already a Flask dependency). Re-seed so the stored hashes use the new scheme.

### [CRITICAL] AP01 Hardcoded secrets and credentials
File: app.py:13, services/notification_service.py:9-10
Description: `app.config['SECRET_KEY'] = 'super-secret-key-123'`; the SMTP account `'taskmanager@gmail.com'` / `'senha123'` is hardcoded in `NotificationService.__init__`. The database URI is a literal at app.py:11.
Impact: Anyone with repo access can forge signed sessions and use the mail account.
Recommendation: PB01. Add a `config.py` that reads `SECRET_KEY`, `DATABASE_URL`, `SMTP_*` from the environment with safe dev fallbacks, and write `.env.example`.

### [CRITICAL] AP05 Debug mode and insecure server configuration
File: app.py:34
Description: `app.run(debug=True, host='0.0.0.0', port=5000)` starts the Werkzeug debugger and listens on all interfaces.
Impact: The interactive debugger on a public interface gives remote code execution.
Recommendation: PB01. Drive debug from `FLASK_DEBUG` (default off) and the bind host from config (default `127.0.0.1`).

### [HIGH] AP08 Business logic in route handlers
File: routes/task_routes.py:11-63, routes/task_routes.py:85-154, routes/task_routes.py:156-223, routes/task_routes.py:273-299, routes/user_routes.py:42-90, routes/user_routes.py:92-132, routes/user_routes.py:153-183, routes/report_routes.py:12-101, routes/report_routes.py:103-155, routes/report_routes.py:167-188
Description: Handlers validate input, query the ORM, compute overdue flags and statistics, build response dicts, and call `db.session.add/commit/delete` directly. `services/` exists but only holds an unused `NotificationService`, and the routes never use `Task.is_overdue`, `Task.validate_status` or the helpers. `report_routes.py` also mixes reports with the category CRUD.
Impact: The logic cannot be reused or tested without HTTP, and the layers are bypassed.
Recommendation: PB07. Move the rules into controllers/services (task, user, category, report), keep models as data and persistence, and make the routes thin: parse the request, call a controller, return JSON. Split the category routes into their own blueprint with the same paths.

### [HIGH] AP11 Swallowed errors
File: routes/task_routes.py:62, routes/task_routes.py:137, routes/task_routes.py:204, routes/task_routes.py:236, routes/user_routes.py:130, routes/user_routes.py:149, routes/report_routes.py:186, routes/report_routes.py:207, routes/report_routes.py:221
Description: Bare `except:` blocks convert any failure (including programming errors) into a generic 400/500 and drop the cause. `get_tasks` wraps the whole body in `except:` and returns 'Erro interno'. `update_task` catches `Exception as e` and never uses it.
Impact: Real failures are invisible, hard to debug, and reported with misleading statuses.
Recommendation: PB13. Catch specific exceptions (`ValueError`, `SQLAlchemyError`), log the cause, and let unexpected errors reach the central handler (PB11).

### [HIGH] AP13 Permissive CORS
File: app.py:15
Description: `CORS(app)` with no origins allows every website to call the API, including the destructive routes.
Impact: Any page in a victim's browser can call the API cross-origin.
Recommendation: PB01. Read the allowed origins from config (`CORS_ORIGINS`) and pass `origins=` to `CORS`.

### [HIGH] AP09 Hidden coupling and hardcoded dependencies in a service
File: services/notification_service.py:5-10
Description: `NotificationService.__init__` builds its own SMTP settings (host, port, user, password) and keeps notifications in an in-memory list on the instance. Nothing is injected, and the service is never used.
Impact: It cannot be configured or mocked, and the in-memory list is lost on restart.
Recommendation: PB08. Receive the SMTP settings from `config` (injected), and remove the in-memory store or inject a store.

### [MEDIUM] AP14 N+1 queries
File: routes/task_routes.py:41-57, routes/user_routes.py:22, routes/report_routes.py:55-56, routes/report_routes.py:163
Description: `get_tasks` calls `User.query.get` and `Category.query.get` for every task. `get_users` evaluates `len(u.tasks)` for every user. `summary_report` runs `Task.query.filter_by(user_id=u.id).all()` per user, and `get_categories` runs a count per category.
Impact: The number of queries grows with the data size.
Recommendation: PB10. Use joined/eager loading (`joinedload`) or grouped aggregate queries.

### [MEDIUM] AP15 Duplicated logic
File: routes/task_routes.py:30-39, routes/task_routes.py:71-80, routes/task_routes.py:283-287, routes/user_routes.py:171-180, routes/report_routes.py:34-43, routes/report_routes.py:132-135, routes/task_routes.py:17-28, routes/user_routes.py:162-169, routes/task_routes.py:110, routes/task_routes.py:177
Description: The overdue rule is copied seven times even though `Task.is_overdue()` (models/task.py:50-60) exists. The task row-to-dict mapping is duplicated against `Task.to_dict()`. The valid-status list is repeated inline (models/task.py:39, task_routes.py:110 and 177, utils/helpers.py:75 and 110), and the email regex is repeated in user_routes.py:61, user_routes.py:106 and utils/helpers.py:21. The task counters are duplicated between `/tasks/stats` and `/reports/summary`.
Impact: Fixes diverge and the rules drift.
Recommendation: PB07. Use `Task.is_overdue()` and `to_dict()` everywhere, centralize the constants and validators in one module, and compute statistics in one place.

### [MEDIUM] AP16 Missing or unsafe input validation
File: routes/report_routes.py:196-202, routes/task_routes.py:96, routes/task_routes.py:113, routes/task_routes.py:182, routes/task_routes.py:261, routes/task_routes.py:264, routes/user_routes.py:106, routes/user_routes.py:115, routes/user_routes.py:125, routes/report_routes.py:173-180
Description: `update_category` never checks that `data` is not None (a request with no JSON body fails with a TypeError and a 500). `len(title)` and `priority < 1` run on unvalidated types, so a number title or a string priority raises. `int(priority)` and `int(user_id)` from the query string in `/tasks/search` are unguarded, so a bad value gives a 500. `active` is assigned unvalidated, and category `name`/`color` are not validated. PUT validation is also weaker than POST.
Impact: Bad input becomes a 500 or reaches the database.
Recommendation: PB14. Validate types, ranges and formats in a single validation layer, and return 400 with a consistent body.

### [MEDIUM] AP17 No centralized error handling
File: app.py:9-34, routes/task_routes.py:12-63, routes/user_routes.py:80-90
Description: The app registers no `@app.errorhandler`. Every handler repeats its own try/except with its own message format, and unhandled exceptions return Flask's default HTML 500.
Impact: The API contract is inconsistent, and errors are hidden or duplicated.
Recommendation: PB11. Register JSON error handlers for HTTPException and Exception in a middleware module and let controllers raise typed errors.

### [MEDIUM] AP18 Unrestricted resource consumption
File: routes/task_routes.py:14, routes/task_routes.py:266, routes/user_routes.py:12, routes/report_routes.py:30, routes/report_routes.py:53, routes/report_routes.py:159, routes/user_routes.py:185-211, app.py:9-34
Description: List endpoints call `.all()` with no pagination or limit, `/reports/summary` loads every task and every user's tasks in Python, `POST /login` has no rate limiting, and the app sets no `MAX_CONTENT_LENGTH`.
Impact: Response size, memory and CPU grow without bound, and login can be brute-forced.
Recommendation: PB10. Add optional `limit`/`offset` with a sane maximum, aggregate in SQL, and set `MAX_CONTENT_LENGTH`.

### [MEDIUM] AP25 Missing security headers
File: app.py:9-34
Description: No `after_request` hook sets `X-Content-Type-Options` or `X-Frame-Options`.
Impact: The responses are exposed to MIME sniffing and framing.
Recommendation: PB01. Add a small `after_request` hook that sets the headers.

### [LOW] AP23 Deprecated APIs
File: models/category.py:11, models/task.py:15-16, models/task.py:52, models/user.py:14, routes/task_routes.py:31, routes/task_routes.py:72, routes/task_routes.py:215, routes/task_routes.py:285, routes/user_routes.py:172, routes/report_routes.py:35, routes/report_routes.py:42, routes/report_routes.py:45, routes/report_routes.py:71, routes/report_routes.py:133, services/notification_service.py:35, utils/helpers.py:38, routes/task_routes.py:42, routes/task_routes.py:51, routes/task_routes.py:67, routes/task_routes.py:117, routes/task_routes.py:122, routes/task_routes.py:158, routes/task_routes.py:188, routes/task_routes.py:195, routes/task_routes.py:227, routes/user_routes.py:29, routes/user_routes.py:94, routes/user_routes.py:136, routes/user_routes.py:155, routes/report_routes.py:105, routes/report_routes.py:192, routes/report_routes.py:213, app.py:34
Description: `datetime.utcnow()` -> `datetime.now(timezone.utc)`; `Model.query.get(id)` -> `db.session.get(Model, id)`; `app.run(debug=True)` -> `FLASK_DEBUG` env var / config.
Impact: Breaks on future library/runtime versions; warnings today.
Recommendation: PB12. Note that the stored datetimes are naive, so the replacement must keep comparisons consistent (naive UTC).

### [LOW] AP22 Dead code, unused imports and dependencies
File: app.py:7, routes/task_routes.py:7, routes/user_routes.py:6, routes/report_routes.py:7-8, models/task.py:3, utils/helpers.py:3-7, utils/helpers.py:9-108, services/notification_service.py:4-48, models/task.py:38-60, models/user.py:34-38, requirements.txt:4-6
Description: Unused imports (`os, sys, json`, `hashlib`, `format_date`, `calculate_percentage`, `math`, ...). Functions never called: every function in `utils/helpers.py`, the whole `NotificationService`, `Task.validate_status`, `Task.validate_priority`, `Task.is_overdue` and `User.is_admin`. `marshmallow`, `requests` and `python-dotenv` are in requirements.txt but never imported.
Impact: Noise, a misleading structure, and unneeded dependencies.
Recommendation: PB15. Remove the dead code, or wire it in (`is_overdue`, the validators, `python-dotenv` for config) as part of the restructure.

### [LOW] AP19 Magic numbers and strings
File: routes/task_routes.py:96-114, routes/task_routes.py:166-184, routes/report_routes.py:45, routes/report_routes.py:129, routes/user_routes.py:64, routes/user_routes.py:71, utils/helpers.py:110-116
Description: Title limits (3, 200), priority range (1-5), the 7-day window, the high-priority threshold (`<= 2`), the password minimum (4) and the status/role lists are repeated inline. Constants exist at utils/helpers.py:110-116 but nothing uses them.
Impact: Rules are hard to find and change consistently.
Recommendation: PB15. Define the constants once and use them.

### [LOW] AP20 Print logging
File: routes/task_routes.py:149, routes/task_routes.py:153, routes/task_routes.py:219, routes/task_routes.py:234, routes/user_routes.py:83, routes/user_routes.py:89, routes/user_routes.py:147, services/notification_service.py:21, services/notification_service.py:24, utils/helpers.py:39-41
Description: Application events and errors are written with `print(...)`, and failed logins are not logged at all.
Impact: There are no log levels or structure, so the output is hard to filter or ship.
Recommendation: PB16. Use the `logging` module.

### [LOW] AP21 Poor naming
File: routes/task_routes.py:16, routes/user_routes.py:14, routes/report_routes.py:24-28
Description: Cryptic names (`t`, `u`, `p1`..`p5`, `cat`, `d`) for domain data, and `type(tags) == list` instead of `isinstance`.
Impact: Readability.
Recommendation: PB15. Use descriptive names and `isinstance`.

================================
Total: 20 findings
================================
