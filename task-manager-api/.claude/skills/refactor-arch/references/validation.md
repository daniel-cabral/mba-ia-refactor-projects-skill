# Validation procedure

Used in Phase 3. Proves the app still boots and every original endpoint still responds. The baseline is captured **before any file is edited**; the same request plan runs again after refactoring.

## 1. Environment

- Python: use `.venv/` in the project. If missing, create it (`python -m venv .venv`) and install the manifest (`.venv/bin/pip install -r requirements.txt`, Windows: `.venv\Scripts\pip`). Run the app with the venv interpreter.
- Node: if `node_modules/` is missing, run `npm ci` (or `npm install` without a lock file).
- Do not install anything globally.

## 2. Fresh state (before every boot)

- Delete local database files created by previous runs: `*.db`, `*.sqlite`, `instance/` (only gitignored/generated files, never source).
- In-memory databases need nothing.
- If Phase 1 found a seed/setup script, run it after deleting the DB and before booting (after refactoring it must still run without errors; a failing seed is a regression) (or let the boot seed, if that is how the project works).
- Same fresh state for the baseline run and the post-refactor run, so ids and counts match.

## 3. Boot

1. Free the port from Phase 1 (a previous run or a debug reloader may still hold it):
   - POSIX: `lsof -ti tcp:<port> | xargs -r kill -9`
   - Windows (PowerShell): `Get-NetTCPConnection -LocalPort <port> -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }`
   - Windows (Git Bash): `netstat -ano | grep ":<port> .*LISTEN" | awk '{print $NF}' | sort -u | xargs -r -I{} taskkill //F //T //PID {}`
2. Confirm the port is free before starting.
3. Start with the original start command in the background, redirecting output to `./reports/boot-<baseline|after>.log`.
4. Wait until ready: poll a cheap GET endpoint every second, up to 30 s. If it never answers, boot failed: read the log.
5. Boot succeeds only if the process is running, the port answers, and the log has no traceback/unhandled error.

## 4. Request plan

Build once from the Phase 1 endpoint list, store it in the log, reuse it unchanged after refactoring.

- One request per endpoint, at minimum. Add a second request for important error paths only if useful (e.g. invalid body returns 400).
- Payloads: take them from `*.http` files, README examples, or the fields read by the handler. Use valid, realistic values (happy path).
- Path ids: use ids that exist after the fresh state (seed data or records created earlier in the plan).
- Order:
  1. Health/root and list GETs.
  2. Creates (POST), then reads of the created records.
  3. Updates (PUT/PATCH).
  4. Login/auth endpoints, using seed credentials.
  5. Guarded/dangerous routes (admin, raw SQL, reset).
  6. Destructive requests (DELETE, reset) last.
- Use `curl -s -o <body file> -w "%{http_code}"` with `-H "Content-Type: application/json"` for bodies. On Git Bash for Windows, prefix with `MSYS_NO_PATHCONV=1` if paths get rewritten.

## 5. Baseline

Run the plan against the original code. For each request record: method, path, status, and the response shape (top-level keys; for lists, keys of the first element; for nested objects, one more level).

## 6. Expected deltas

Before comparing, list every intentional difference introduced by the refactor:

- Guarded dangerous routes: original status -> 403 (D2, PB05).
- Removed sensitive fields (password, hash, secret, db path, debug flag) from response shapes (PB04).
- Error bodies standardized to `{"error": ...}` (only for non-2xx responses).
- Logic bugs fixed on purpose that change a response (state the request and why).

Anything not on this list is a regression.

## 7. Compare

After refactoring, apply the fresh state, boot, run the same plan, and compare per request:

| Check | Pass when |
| --- | --- |
| Boot | Process up, port answers, no traceback in the log |
| Status | Same as baseline, or an expected delta |
| Shape | Same keys as baseline, minus expected removed fields |
| Errors | No 500 where the baseline had a 2xx |

## 8. Teardown

Kill the whole process tree after each run (the debug reloader keeps a child alive):

- POSIX: `kill -- -<pgid>` or `pkill -P <pid>; kill <pid>`, then repeat the port check.
- Windows: `taskkill /F /T /PID <pid>` and the port-based kill from step 3.

Confirm the port is free. Delete the database files created during validation.

## 9. Failure policy

- If any check fails: read the boot log and the failing response, fix the code, and run the full plan again.
- Maximum 3 fix-and-revalidate cycles. If it still fails, stop and report exactly what fails. Never report success for a failing check.

## 10. Log format (`./reports/validation-log.md`)

```markdown
# Validation log

Start command: <command> | Port: <port> | Fresh state: <what was deleted / seeded>

## Expected deltas
- POST /admin/reset-db: 200 -> 403 (guarded, PB05)
- GET /users: field `password` removed (PB04)

## Results
| # | Request | Baseline | After | Shape | Result |
| --- | --- | --- | --- | --- | --- |
| 1 | GET /products | 200 | 200 | same | PASS |
| 2 | POST /admin/reset-db | 200 | 403 | n/a | PASS (expected delta) |

Boot: PASS (no errors in reports/boot-after.log)
Summary: <passed>/<total> PASS
```
