# Plan: refactor-arch skill

Status: APPROVED
Spec: [spec.md](spec.md)

## Environment (C5, verified 2026-10-18)

- Python 3.14.7, Node 24.19, npm 11.17.
- Deps install unmodified: P1 (Flask 3.1.1), P3 (Flask 3.0.0), P2 (`npm ci`). Python projects use a local `.venv/` (gitignored).
- All 3 apps boot unmodified and answer 200 (P1 `/produtos`, P3 `/health`, `/tasks`, P2 `/api/admin/financial-report`).
- Gotcha: Flask `debug=True` spawns a reloader child; killing the parent leaves the port bound. P1 and P3 both use port 5000. Validation must free the port before boot and kill the whole process tree after (POSIX and Windows commands both documented).
- Booting creates gitignored DB files (`loja.db`, `instance/tasks.db`) with seed data; they survive `git restore` and must be deleted for a fresh state.

## Skill layout

Authored once in `code-smells-project/.claude/skills/refactor-arch/`, then copied unchanged to the other two projects (FR6).

```
refactor-arch/
├── SKILL.md                       # orchestration: 3 phases, gates, output blocks
└── references/
    ├── project-analysis.md        # area 1: stack/DB/architecture detection heuristics
    ├── anti-patterns.md           # area 2: catalog (>= 8, all severities, deprecated APIs)
    ├── report-template.md         # area 3: Phase 2 report format
    ├── mvc-guidelines.md          # area 4: target layers, responsibilities, per-stack layout
    ├── refactoring-playbook.md    # area 5: >= 8 before/after transformations
    └── validation.md              # baseline, expected deltas, process handling (D10-D13, D16)
```

## SKILL.md design

- Frontmatter: `name: refactor-arch`, description with trigger phrases.
- Body is a prompt, short: phases, when to read which reference, hard gates. Domain knowledge lives in references (progressive disclosure).
- Phase 1: read `project-analysis.md`; apply D18 ignores; print the Phase 1 block (README format) incl. endpoint list.
- Phase 2: read `anti-patterns.md` + `report-template.md`; one finding per anti-pattern (D17); sort by severity; print + save `./reports/audit-report.md` (D3, D19); STOP and ask `[y/n]` (FR3).
- Phase 3: read `mvc-guidelines.md`, `refactoring-playbook.md`, `validation.md`; capture baseline before any edit; refactor incrementally (D13); fix CRITICAL/HIGH + checklist items (D1, D2); validate (D10-D12, D16); print Phase 3 block with structure, validation results and "remaining" MEDIUM/LOW (C2).

## Reference content plan

| File | Must contain |
| --- | --- |
| project-analysis.md | Start command (`python app.py`, `npm start`), seed/setup scripts, manifest signals (requirements.txt, package.json, pyproject), framework + version, DB detection (sqlite3, SQLAlchemy, sqlite3 npm), entry point, route discovery per framework, domain inference from tables/routes, architecture classification (monolith / partial layers / MVC) |
| anti-patterns.md | ~14 entries, each: id, severity, detection signals (grep-able, Python + JS), example, fix pointer to playbook. Covers: hardcoded secrets, SQL injection, weak/plaintext passwords, sensitive data exposure, debug in prod, unauthenticated destructive routes / mass assignment, God class, business logic in routes, global mutable state, missing transactions, N+1, duplication, missing validation / error handling, magic numbers, print logging, naming/shadowing, unused imports/dead code, deprecated APIs (table: `datetime.utcnow`, `Query.get`, callback sqlite3, `app.run(debug)` etc.) |
| report-template.md | Exact block from README (header, Summary counts, Findings with File/Description/Impact/Recommendation, total), rules: exact file:line, ordering, one finding per anti-pattern |
| mvc-guidelines.md | Layer rules (Model: data + domain rules; Controller: flow, no HTTP/SQL; View/Routes: HTTP only; config; middlewares; composition root), dependency direction, per-stack target trees (Flask, Express), in-place evolution for layered projects (D4) |
| refactoring-playbook.md | >= 10 patterns, before/after in the matching stack: extract config/env (D8), parameterize SQL, hash passwords (D7), strip sensitive fields, guard dangerous routes (D2), split God class into model/controller/routes, move logic route->controller, replace global state with injected deps, wrap in transaction, fix N+1 with JOIN/eager load, centralized error handler (D5), replace deprecated APIs, callbacks->async/await |
| validation.md | Fresh DB state (delete DB file), run seed/setup scripts, free port, boot with the original start command, wait-for-ready, endpoint list + payloads, destructive last (D12), expected deltas list (D11), compare, kill process tree, retry policy (D16), log format `./reports/validation-log.md` |

## Execution order (becomes tasks.md)

0. Discovery check: stub SKILL.md in P1, open a fresh session in `code-smells-project/`, confirm `/refactor-arch` is found.
1. Write references (anti-patterns + playbook first: largest, drive the rest).
2. Write SKILL.md.
3. Commit skill; run on P1 in a fresh session; iterate (reset per D15). On pass: commit refactored project, copy report to repo-root `reports/audit-project-1.md`.
4. Copy skill to P2, P3; run; iterate; commit + copy report after each pass. Any fix to the skill is made in P1 copy and re-copied.
5. README sections A-D; copy reports to repo-root `reports/`.

## Catalog severity target

At least: CRITICAL 4, HIGH 4, MEDIUM 4, LOW 3 (all present in the ground truth).

## Risks

- Skill too long for context: keep SKILL.md < ~200 lines; references loaded per phase.
- Over-fitting to the 3 projects: detection signals are generic patterns, never project file names.
- Start command must still work after refactor, or manifest + project README updated.
- Phase 3 on P3 moving too much: D4 in-place evolution.
