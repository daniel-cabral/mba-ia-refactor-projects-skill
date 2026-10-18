# Spec: refactor-arch skill

Status: APPROVED (after grilling)

## Goal

A Claude Code skill, `/refactor-arch`, that analyzes any backend codebase, audits it against an anti-pattern catalog, and (after human confirmation) refactors it to MVC, validating the app still boots and its endpoints respond.

## Functional requirements

- FR1 Phase 1 (Analysis): detect language, framework + version, dependencies, DB, domain, current architecture, source file count; print the Phase 1 summary block.
- FR2 Phase 2 (Audit): match code against the catalog; every finding has severity, exact `file:line`, description, impact, recommendation; ordered CRITICAL > HIGH > MEDIUM > LOW; includes deprecated API detection.
- FR3 Phase 2 MUST stop and ask for confirmation before touching any file.
- FR4 Phase 3 (Refactor): restructure to MVC (config, models, views/routes, controllers, centralized error handling, clear entry point); adapt to existing structure (monolith vs partially layered).
- FR5 Phase 3 validation: app boots without errors; every original endpoint still responds.
- FR6 Tech-agnostic: same skill folder, copied unchanged, works on Python/Flask and Node/Express.

## Reference knowledge (5 mandatory areas)

| Area | Content |
| --- | --- |
| Project analysis | Heuristics: language, framework, DB, architecture mapping |
| Anti-pattern catalog | >= 8 anti-patterns, detection signals, severity, deprecated APIs |
| Report template | Phase 2 report format |
| MVC guidelines | Layer rules and responsibilities |
| Refactoring playbook | >= 8 before/after transformations |

## Acceptance criteria (per project, 3/3)

- Phase 1 detects stack correctly.
- Phase 2 finds >= 5 findings, >= 1 CRITICAL or HIGH, and >= 5 of the ground-truth items below.
- Phase 3: app boots and original endpoints respond.
- Report saved to `reports/audit-project-{1,2,3}.md`.

## Ground truth (manual analysis)

Drafted by subagents in two passes, line numbers spot-checked. To be reviewed.

### Project 1: code-smells-project (Python, Flask 3.1.1, sqlite3, e-commerce)

Endpoints: 19 (produtos, usuarios, login, pedidos, relatorios, health, admin).

| # | Sev | Anti-pattern | Location |
| --- | --- | --- | --- |
| 1 | CRITICAL | SQL injection (string concat) | models.py:28, 47-50, 58-60, 68, 92, 110, 127-128, 140, 174, 280, 291-297 |
| 2 | CRITICAL | Arbitrary SQL endpoint, unauthenticated | app.py:59-78 |
| 3 | CRITICAL | Hardcoded SECRET_KEY, leaked in /health | app.py:7, controllers.py:289 |
| 4 | CRITICAL | Plaintext passwords stored and returned | models.py:83, 99; database.py:76-78 |
| 5 | CRITICAL | Debug on + 0.0.0.0 | app.py:8, 88 |
| 6 | CRITICAL | Unauthenticated destructive admin route (/admin/reset-db) | app.py:47-57 |
| 7 | CRITICAL | God module: models.py mixes SQL, business rules, reporting | models.py:1-314 |
| 8 | CRITICAL | No auth on any route; login issues no token | app.py:11-30; controllers.py:176-180 |
| 9 | HIGH | Global mutable DB connection, no DI | database.py:4-10 |
| 10 | HIGH | Business logic in controllers | controllers.py:43-54, 242-250 |
| 11 | HIGH | CORS wide open on API with destructive routes | app.py:9 |
| 12 | HIGH | Non-atomic order: stock race, negative quantity accepted | models.py:139-166; controllers.py:198-203 |
| 13 | HIGH | Controller and entry point query DB directly (layer bypass) | controllers.py:266-274; app.py:47-78 |
| 14 | MEDIUM | N+1 queries in order listing | models.py:171-233 |
| 15 | MEDIUM | Duplicated row mapping / validation | models.py:12-21, 31-40; controllers.py:24-93 |
| 16 | MEDIUM | Missing validation, no error middleware | controllers.py:26, 119, 169-170 |
| 17 | MEDIUM | Internal exception text returned to client (`str(e)`) | controllers.py:12, 22, 62 (and others) |
| 18 | MEDIUM | Cancel does not restore stock; no 404 on status update | controllers.py:242-250; models.py:275-283 |
| 19 | MEDIUM | Sales report counts cancelled orders as revenue | models.py:242-245 |
| 20 | LOW | Magic numbers (discount tiers) | models.py:257-262 |
| 21 | LOW | print() as logging | controllers.py:8, 11, 57 |
| 22 | LOW | Builtin shadowing (`id`), unused import | controllers.py:14; models.py:2 |

### Project 2: ecommerce-api-legacy (Node.js, Express 4.18, sqlite3 in-memory, LMS checkout)

Endpoints: POST /api/checkout, GET /api/admin/financial-report, DELETE /api/users/:id.

| # | Sev | Anti-pattern | Location |
| --- | --- | --- | --- |
| 1 | CRITICAL | Hardcoded credentials (DB, payment key) | src/utils.js:2-5 |
| 2 | CRITICAL | Fake/reversible password hashing | src/utils.js:17-23 |
| 3 | CRITICAL | Card number + key logged | src/AppManager.js:45 |
| 4 | CRITICAL | God class (DB, schema, routes, payment, report) | src/AppManager.js:4-139 |
| 5 | CRITICAL | Unauthenticated admin report and user delete | src/AppManager.js:80, 131-132 |
| 6 | HIGH | Business logic in route handlers | src/AppManager.js:28-78 |
| 7 | HIGH | Callback hell swallowing errors | src/AppManager.js:37-77, 83-128 |
| 8 | HIGH | Global mutable state (cache, revenue) | src/utils.js:9-10, 14 |
| 9 | HIGH | Existing email checkout skips password check (account takeover) | src/AppManager.js:40, 73-74 |
| 10 | HIGH | Non-atomic checkout: user created even when card is denied | src/AppManager.js:46-48, 66-72 |
| 11 | HIGH | Report crashes process on DB error (`enrollments.length` on undefined) | src/AppManager.js:92-93 |
| 12 | HIGH | Non-string `card` crashes process (`cc.startsWith`) | src/AppManager.js:35, 46 |
| 13 | MEDIUM | N+1 in financial report | src/AppManager.js:83-126 |
| 14 | MEDIUM | Weak validation, no error middleware | src/AppManager.js:29-35; src/app.js |
| 15 | MEDIUM | DELETE ignores error, no 404, orphans data | src/AppManager.js:132-136 |
| 16 | MEDIUM | Inconsistent response formats (text vs JSON) | src/AppManager.js:35, 48, 60, 135 |
| 17 | LOW | Cryptic names (u, e, cid, cc) | src/AppManager.js:29-33 |
| 18 | LOW | Magic numbers/strings (10000, "4", "123456") | src/utils.js:19-22; src/AppManager.js:46, 68 |
| 19 | LOW | Legacy style: `self = this`, callback sqlite3 API | src/AppManager.js:26 |
| 20 | LOW | Wrong status codes (200 on create, text on delete) | src/AppManager.js:48, 60, 135 |

### Project 3: task-manager-api (Python, Flask 3.0, Flask-SQLAlchemy 3.1, SQLite, Task Manager)

Endpoints: 22 (tasks, users, login, reports, categories, health).

| # | Sev | Anti-pattern | Location |
| --- | --- | --- | --- |
| 1 | CRITICAL | Hardcoded SECRET_KEY | app.py:13 |
| 2 | CRITICAL | Hardcoded SMTP credentials | services/notification_service.py:9-10 |
| 3 | CRITICAL | Unsalted MD5 password hashing | models/user.py:29, 32 |
| 4 | CRITICAL | Password hash in API responses | models/user.py:21 |
| 5 | CRITICAL | Debug on + 0.0.0.0 | app.py:34 |
| 6 | CRITICAL | Fake token, no authorization (anyone deletes users / sets admin) | routes/user_routes.py:210, 93, 135 |
| 7 | CRITICAL | Mass assignment: public signup accepts `role=admin` | routes/user_routes.py:52, 71-78 |
| 8 | HIGH | Business logic + persistence in routes (no controller layer) | routes/task_routes.py:85-223; routes/report_routes.py:12-101 |
| 9 | HIGH | CORS wide open on unauthenticated API | app.py:15 |
| 10 | MEDIUM | Duplicated validation, helper unused | utils/helpers.py:57-108 vs routes/task_routes.py:92-144 |
| 11 | MEDIUM | N+1 queries | routes/task_routes.py:42, 51; routes/report_routes.py:56 |
| 12 | MEDIUM | Bare `except:` | routes/task_routes.py:62, 137, 204 |
| 13 | MEDIUM | Overdue logic duplicated 6x (model method unused) | routes/task_routes.py:30-39, 71-80 |
| 14 | MEDIUM | Category CRUD lives in report blueprint (misplaced resource) | routes/report_routes.py:157-223 |
| 15 | MEDIUM | Unbounded list endpoints, no pagination | routes/task_routes.py:14; routes/user_routes.py:12 |
| 16 | MEDIUM | Duplicate-email race: IntegrityError becomes 500 | routes/user_routes.py:67-69, 87-90 |
| 17 | MEDIUM | Missing body guard: `None` body crashes PUT /categories | routes/report_routes.py:196-197 |
| 18 | LOW | Deprecated `datetime.utcnow()` | models/task.py:15-16 (and others) |
| 19 | LOW | Deprecated `Query.get()` (SQLAlchemy 2.0) | routes/task_routes.py:42 (and others) |
| 20 | LOW | Magic strings, unused constants | routes/task_routes.py:96-100, 110, 177; routes/user_routes.py:71; utils/helpers.py:110-116 |
| 21 | LOW | Unused imports, print() logging | app.py:7; routes/task_routes.py:149 |
| 22 | LOW | Dead notification service (never imported), mail header injection | services/notification_service.py:4-48 |

## Out of scope

- Adding automated test suites to the target projects.
- Authentication/authorization features (flagged in audit, not implemented).

## Decisions

- D1 Phase 3 scope: MVC restructuring + fix all CRITICAL and HIGH findings + whatever the validation checklist requires (config module, centralized error handling, clear entry point). Remaining MEDIUM/LOW are listed as "remaining" in the Phase 3 output, never claimed as fixed. Constraint: original endpoints keep paths, methods and response shape (minus leaked sensitive fields).
- D2 Inherently dangerous endpoints (e.g. arbitrary SQL, DB reset) and every unauthenticated admin or destructive route are kept but guarded by config: they return 403 unless an env flag enables them. The route still responds; the risk is closed and noted in the report.
- D20 Guard scope (refines D2): only admin routes, raw SQL/code execution, DB reset/bulk wipe and account deletion are guarded. Normal resource CRUD keeps working. A missing authentication system is reported CRITICAL but listed as remaining (out of scope).
- D4 MVC layers are fixed (config, models, views/routes, controllers, middlewares); folder names follow the stack idiom. Partially layered projects evolve in place (add missing layers) instead of being moved under `src/`.
- D5 Endpoint contract: success responses keep path, method, status and shape (minus sensitive fields); error responses may adopt a standard envelope (`{"error": ...}`).
- D6 HIGH logic bugs are fixed even when behavior changes; the validation baseline only compares happy-path requests.
- D7 No new dependencies unless unavoidable; prefer stdlib/framework built-ins (e.g. `werkzeug.security`, Node `crypto.scrypt`). Any new dependency is justified in the report.
- D8 Missing secret env vars: boot with a random dev secret plus a warning; the skill writes `.env.example`. Old hardcoded values are never reused.
- D9 Audit report and skill output in English; README "Análise Manual" in PT-BR.
- D10 Validation: at the start of Phase 3 (before any edit) the skill boots the app in background, calls every endpoint with curl (payloads from code or `api.http`), records a baseline, and after refactoring repeats and compares. Log saved to `./reports/validation-log.md`.
- D11 Expected deltas (D2 guards returning 403, removed sensitive fields) are listed explicitly before comparing; any other difference is a failure.
- D12 Destructive requests (DELETE, reset) run last in both baseline and validation.
- D13 Phase 3 runs incrementally (config, models, controllers, routes, error handler), checking boot after each step.
- D14 Dependency versions may be bumped only when needed to boot or to remove a deprecated API; recorded in the report.
- D15 The skill never commits. The skill is committed before every run. Between iterations the project is reset to the original: `git restore` + `git clean` of the project folder excluding `.claude/`, plus deleting gitignored `*.db` / `instance/`. Each run happens in a fresh Claude Code session started inside the project folder.
- D16 Validation failure: fix and re-validate up to 3 times; then stop and report the failure, never claim success.
- D17 One finding per anti-pattern, listing all its locations (no per-occurrence inflation).
- D18 Phases 1-2 analyze only the current working directory (never parent folders) and ignore `.claude/`, `node_modules/`, `reports/`, virtualenvs, lock files and `.db` files.
- D19 Phase 2 prints the full report to the terminal, saves it (D3), then asks `[y/n]`.
- D3 The skill saves the Phase 2 report to `./reports/audit-report.md` inside the target project (stays tech and repo agnostic); we copy it to the repo-root `reports/audit-project-N.md`.

## Constraints

- C1 Severity follows the README scale: God Class = CRITICAL, duplication = MEDIUM.
- C2 Phase 3 output never prints "Zero anti-patterns remaining" while MEDIUM/LOW remain; it prints the remaining list.
- C3 Validation baseline: before any change, record each original endpoint's status and response shape; compare after refactoring.
- C4 Password hashing fix must re-hash seed users so `/login` still accepts the seed credentials.
- C5 Plan phase starts by confirming Python/Node are installed and the 3 apps boot unmodified.
