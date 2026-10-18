# Validation log

Start command: `npm start` (node src/app.js) | Port: 3000 | Fresh state: in-memory SQLite (nothing to delete), seeded at boot. After run started with `ADMIN_TOKEN=test-admin`.

## Expected deltas
- GET /api/admin/financial-report: 200 -> 403 without `x-admin-token` (guarded, PB05)
- DELETE /api/users/:id: 200 -> 403 without `x-admin-token` (guarded, PB05); with the token the user's enrollments and payments are deleted too (AP12 fix), response text changed
- Error bodies standardized to `{"error": ...}` (PB11): denied payment 400, invalid body 400
- Checkout validation stricter (PB14): `pwd` required, email/card format checked; existing accounts need the right password (401), duplicate enrollment returns 409
- Seed user password is hashed and random unless `SEED_USER_PASSWORD` is set (PB03)
- Report is ordered by course id and paginated (`limit`, `offset`)

## Results
| # | Request | Baseline | After | Shape | Result |
| --- | --- | --- | --- | --- | --- |
| 1 | GET /api/admin/financial-report (no token) | 200 | 403 | `{error}` | PASS (expected delta) |
| 2 | POST /api/checkout (valid, c_id 2) | 200 | 200 | same (`msg`, `enrollment_id`) | PASS |
| 3 | POST /api/checkout (card 5111...) | 400 text | 400 | `{error}` | PASS (expected delta) |
| 4 | POST /api/checkout ({}) | 400 text | 400 | `{error}` | PASS (expected delta) |
| 5 | GET /api/admin/financial-report (with token) | 200 | 200 | same (`course`, `revenue`, `students[student, paid]`) | PASS |
| 6 | DELETE /api/users/1 (no token) | 200 | 403 | `{error}` | PASS (expected delta) |
| 7 | DELETE /api/users/1 (with token) | 200 | 200 | text | PASS (expected delta: message) |

Extra checks after refactor (200/409/401/400/404 paths): duplicate enrollment 409, wrong password 401, malformed JSON 400, bad `limit` 400, unknown route 404 JSON, deleted user leaves no orphan rows in the report.

Boot: PASS (no errors in reports/boot-after.log)
Summary: 7/7 PASS
