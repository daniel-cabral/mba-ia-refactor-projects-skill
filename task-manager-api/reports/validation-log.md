# Validation log

Start command: python app.py | Port: 5000 | Fresh state: tasks.db / instance/ deleted, `python seed.py` run before each boot (baseline and after)

## Expected deltas
- DELETE /users/<id>: 200 -> 403 (account deletion guarded, enabled with ADMIN_ENABLED=1, PB05)
- `password` removed from GET /users/<id>, POST /users, PUT /users/<id> and the `user` object in POST /login (PB04)
- POST /users with `role: admin` no longer creates an admin: privileged fields are ignored unless ADMIN_ENABLED=1 (PB05); same for `role`/`active` on PUT /users/<id>
- Error bodies are always `{"error": ...}` (request 25: empty body used to return Flask's HTML 400); unexpected errors return a generic 500
- Password hashes are salted scrypt instead of MD5 (PB03); login with seed credentials still works (request 20)
- POST /login `token` is a signed token instead of `fake-jwt-token-<id>` (same shape)

## Results
| # | Request | Baseline | After | Shape | Result |
| --- | --- | --- | --- | --- | --- |
| 1 | GET / | 200 | 200 | same | PASS |
| 2 | GET /health | 200 | 200 | same | PASS |
| 3 | GET /tasks | 200 | 200 | same | PASS |
| 4 | GET /tasks/1 | 200 | 200 | same | PASS |
| 5 | GET /tasks/search?q=bug&status=pending | 200 | 200 | same | PASS |
| 6 | GET /tasks/stats | 200 | 200 | same | PASS |
| 7 | GET /users | 200 | 200 | same | PASS |
| 8 | GET /users/1 | 200 | 200 | expected diff | PASS (expected delta: password removed (PB04)) |
| 9 | GET /users/1/tasks | 200 | 200 | same | PASS |
| 10 | GET /reports/summary | 200 | 200 | same | PASS |
| 11 | GET /reports/user/1 | 200 | 200 | same | PASS |
| 12 | GET /categories | 200 | 200 | same | PASS |
| 13 | POST /tasks | 201 | 201 | same | PASS |
| 14 | GET /tasks/11 | 200 | 200 | same | PASS |
| 15 | POST /users | 201 | 201 | expected diff | PASS (expected delta: password removed (PB04)) |
| 16 | POST /categories | 201 | 201 | same | PASS |
| 17 | PUT /tasks/1 | 200 | 200 | same | PASS |
| 18 | PUT /users/2 | 200 | 200 | expected diff | PASS (expected delta: password removed (PB04)) |
| 19 | PUT /categories/1 | 200 | 200 | same | PASS |
| 20 | POST /login | 200 | 200 | expected diff | PASS (expected delta: user.password removed (PB04)) |
| 21 | POST /login | 401 | 401 | same | PASS |
| 22 | POST /tasks | 400 | 400 | same | PASS |
| 23 | GET /tasks/999 | 404 | 404 | same | PASS |
| 24 | GET /users/999 | 404 | 404 | same | PASS |
| 25 | PUT /categories/1 | 400 | 400 | expected diff | PASS (expected delta: error body standardized: HTML 400 -> {"error"}) |
| 26 | POST /users | 201 | 201 | expected diff | PASS (expected delta: password removed (PB04); role ignored (PB05)) |
| 27 | DELETE /tasks/2 | 200 | 200 | same | PASS |
| 28 | DELETE /categories/4 | 200 | 200 | same | PASS |
| 29 | DELETE /users/4 | 200 | 403 | n/a | PASS (expected delta: guarded 200 -> 403 (PB05)) |

Boot: PASS (no traceback/error in reports/boot-after.err.log; reports/boot-baseline.err.log for the original)
Summary: 29/29 PASS

## Supplementary checks (run against the refactored app)
- Fresh run with ADMIN_ENABLED=1 (reports/boot-admin.err.log): same plan, DELETE /users/4 -> 200, POST /users with role admin -> role `admin` stored. PASS
- Without ADMIN_ENABLED: `PUT /users/5` with role/active ignored (role stays `user`, active stays true); `DELETE /users/5` -> 403. PASS
- GET /tasks?limit=2&offset=1 -> 200 (2 items); ?limit=abc -> 400; /tasks/search?priority=abc -> 400 (was 500); POST /tasks with priority "2" -> 400 (was 500). PASS
- GET /nope -> JSON 404 `{"error": ...}`. PASS
- Response headers include X-Content-Type-Options: nosniff and X-Frame-Options: DENY. PASS
- Stored passwords start with `scrypt:` (checked in instance/tasks.db). PASS
- Teardown: process tree killed, port 5000 free, generated DB files deleted. PASS
