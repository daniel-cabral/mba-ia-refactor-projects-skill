---
name: refactor-arch
description: Analyze a backend codebase (any language/framework), audit it against an anti-pattern catalog with severities and exact file:line, then, after explicit user confirmation, refactor it to MVC and validate that the app boots and its endpoints still respond. Use when the user runs /refactor-arch or asks to audit, review the architecture of, or refactor a project to MVC.
---

# refactor-arch

Three sequential phases: **Analysis -> Audit -> (confirmation) -> Refactoring**. Domain knowledge lives in `references/`; read each file when its phase starts, not before.

| Phase | Read |
| --- | --- |
| 1 Analysis | `references/project-analysis.md` |
| 2 Audit | `references/anti-patterns.md`, `references/report-template.md` |
| 3 Refactoring | `references/mvc-guidelines.md`, `references/refactoring-playbook.md`, `references/validation.md` |

## Hard rules

1. **Scope is the current working directory.** Never read, search or list files outside it (no parent directories, no sibling projects). Apply the ignore list from `project-analysis.md`.
2. **No project file is modified before the user answers `y`** at the end of Phase 2. Phase 1 and 2 are read-only, except writing `./reports/audit-report.md`.
3. **Evidence over claims.** Every finding has an exact, verified `file:line`. Every validation result comes from a command actually run. Never print a check as passed without running it.
4. **Never commit, push or touch git history.** The user handles version control.
5. Output (terminal blocks, report, logs) in English. Keep the project's domain vocabulary in code.
6. The skill must work on any stack: rely on the heuristics in the references, not on assumptions about a specific project.

---

## Phase 1: Project analysis

1. Read `references/project-analysis.md`.
2. Inventory source files (respect the ignore list). Read the manifest(s), the entry point and every source file.
3. Detect language, framework + version, dependencies, database + tables, entry point, start command, port, seed/setup scripts, domain and architecture classification.
4. Discover every endpoint (`METHOD path`), including blueprint/router prefixes.
5. Print the Phase 1 block exactly as defined in `project-analysis.md` section 8.

Continue directly to Phase 2.

## Phase 2: Architecture audit

1. Read `references/anti-patterns.md` and `references/report-template.md`.
2. For each catalog entry: search with its signals, then read the code to confirm. Record exact locations.
3. Look for problems outside the catalog that fit a severity (logic bugs, broken business rules); report them as `AP-X` with justification.
4. Build the report following `report-template.md`: one finding per anti-pattern, ordered CRITICAL -> HIGH -> MEDIUM -> LOW, summary counts consistent with the findings.
5. Print the full report and save the same content to `./reports/audit-report.md`.
6. Print:

   ```text
   Report saved to ./reports/audit-report.md
   Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
   ```

7. **STOP. End your turn and wait for the user.** Only an explicit `y` (or yes) starts Phase 3. Any other answer: stop without modifying files.

## Phase 3: Refactoring

Scope: restructure to MVC, fix **every CRITICAL and HIGH finding** (single exception: a missing authentication system is out of scope; guard dangerous routes per PB05 and list it as remaining), and satisfy the MVC checklist (config module, centralized error handling, clear entry point). Fix MEDIUM/LOW when it comes naturally with the restructuring (e.g. duplication removed by moving code); list the rest as remaining.

### 3.1 Baseline (before any edit)

1. Read `references/validation.md`.
2. Prepare the environment, apply the fresh state, boot with the original start command, run the request plan built from the Phase 1 endpoint list, record the baseline, tear down.
3. If the original app does not boot, report it and ask the user how to proceed before refactoring.

### 3.2 Plan the target

1. Read `references/mvc-guidelines.md` and `references/refactoring-playbook.md`.
2. Choose the target tree: split a monolith into the stack's target tree, or evolve a partially layered project in place (keep existing layer folders, add the missing ones).
3. Map each CRITICAL/HIGH finding to its playbook pattern (`PBxx`).
4. Write down the expected deltas (guarded routes -> 403, removed sensitive fields, standardized error bodies, intentional bug fixes).

### 3.3 Refactor incrementally

Apply in this order, booting the app after each step (quick boot check: start, hit one GET, tear down) and fixing before moving on:

1. **Config**: create the config module, move secrets/flags to env vars with safe dev fallbacks, write `.env.example` (PB01).
2. **Models / data access**: move SQL/ORM access into models; parameterize queries (PB02); per-request or injected DB connection instead of globals (PB08); transactions for multi-step writes (PB09); N+1 fixes (PB10); password hashing incl. seed data (PB03).
3. **Controllers**: move business rules and flow out of handlers (PB07); input validation and invariants (PB14); async/await and error propagation where callbacks are used (PB13).
4. **Views / routes**: thin handlers grouped per resource (Blueprints / Routers), same paths and methods; guards on dangerous routes (PB05); no sensitive fields in responses (PB04).
5. **Middlewares + composition root**: centralized error handler (PB11); entry point wires config, DB, controllers and routes; original start command still works.
6. **Cleanup**: deprecated APIs (PB12), constants/naming/dead code touched by the refactor (PB15), logging (PB16). Remove files left empty by the moves.

### 3.4 Validate

Run the full validation from `references/validation.md` (fresh state, boot, same request plan, compare against baseline and expected deltas, teardown). Save `./reports/validation-log.md`. Follow the failure policy: at most 3 fix-and-revalidate cycles, then stop and report what fails.

### 3.5 Final output

Print:

```text
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<tree of source files, ignore-list excluded, one-line role per file>

## Fixed Findings
<severity> <APxx> <title>: <what changed>   (one line per CRITICAL/HIGH finding)

## Remaining Findings
<severity> <APxx> <title>: <why not fixed>   (or "none")

## Validation
  <✓|✗> Application boots without errors
  <✓|✗> All original endpoints respond correctly (<passed>/<total>, see reports/validation-log.md)
  <✓|✗> Expected deltas only: <short list>
  <✓|✗> No CRITICAL/HIGH findings remaining (except out-of-scope authentication system, if listed)
================================
```

Use `✗` with the reason for any check that did not pass. Print "Zero anti-patterns remaining" only if the Remaining Findings section is "none".
