# Audit report template

Used in Phase 2. The report is printed to the terminal and saved to `./reports/audit-report.md` (create `reports/` if missing). Same content in both places. English.

## Rules

1. One finding per anti-pattern id (`AP01`...`AP24`, or `AP-X` for problems outside the catalog). List every confirmed location of that anti-pattern in the `File:` line(s).
2. Locations are exact: `path/relative/to/project.ext:line` or `:start-end`. Verified by reading the file, never estimated.
3. Order: CRITICAL, then HIGH, MEDIUM, LOW. Within a severity, the higher-impact finding first.
4. Summary counts must equal the number of findings per severity; `Total` must equal their sum.
5. Description quotes or names the concrete code (e.g. the literal secret, the vulnerable query). Impact says what can go wrong. Recommendation points to the playbook pattern (`PBxx`) and states the concrete change.
6. Deprecated APIs (AP23): each usage shows `deprecated -> replacement`.
7. Every CRITICAL/HIGH finding will be fixed in Phase 3; MEDIUM/LOW may remain and will be listed as remaining.
8. No findings without evidence. If fewer than 5 findings are confirmed, say so; do not invent.

## Format

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <directory name>
Stack:   <Language> + <Framework version>
Files:   <N> analyzed | ~<lines> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] AP02 SQL Injection
File: models.py:28, models.py:47-50, models.py:110
Description: Queries are built by string concatenation, e.g. `"SELECT * FROM users WHERE email = '" + email + "'"`.
Impact: Login bypass and full data read/write by any client.
Recommendation: PB02. Use `?` placeholders with a params tuple in every query.

### [HIGH] AP08 Business logic in route handlers
File: controllers.py:43-54, controllers.py:242-250
Description: ...
Impact: ...
Recommendation: ...

### [LOW] AP23 Deprecated APIs
File: models/task.py:15, routes/task_routes.py:42
Description: `datetime.utcnow()` -> `datetime.now(timezone.utc)`; `Task.query.get(id)` -> `db.session.get(Task, id)`.
Impact: Breaks on future library/runtime versions; warnings today.
Recommendation: PB12.

================================
Total: <n> findings
================================
```

After the report, print exactly:

```text
Report saved to ./reports/audit-report.md
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Then stop and wait for the user's answer. Do not modify any project file before an explicit `y`.
