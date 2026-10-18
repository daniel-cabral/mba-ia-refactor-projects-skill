# Tasks: refactor-arch skill

Spec: [spec.md](spec.md) | Plan: [plan.md](plan.md)

Skill path: `code-smells-project/.claude/skills/refactor-arch/` (master copy).

## Phase A: references

- [x] T1 `references/anti-patterns.md`: >= 14 entries (CRITICAL >= 4, HIGH >= 4, MEDIUM >= 4, LOW >= 3), each with id, severity, Python + JS detection signals, playbook pointer; deprecated API table. Done when: counts met, no project-specific file names.
- [x] T2 `references/refactoring-playbook.md`: >= 10 patterns with before/after code (Python and/or JS), each linked to catalog ids. Done when: every CRITICAL/HIGH catalog id has a pattern.
- [x] T3 `references/mvc-guidelines.md`: layer rules, dependency direction, Flask + Express target trees, in-place evolution rule (D4), endpoint contract (D5).
- [x] T4 `references/project-analysis.md`: stack/DB/entry point/start command/seed detection, route discovery per framework, domain inference, architecture classification, ignore list (D18), Phase 1 output block.
- [x] T5 `references/report-template.md`: README report format, ordering, one finding per anti-pattern (D17), exact file:line rule.
- [x] T6 `references/validation.md`: fresh DB, seed, free port, boot, baseline, expected deltas (D11), destructive last (D12), compare, kill tree (POSIX + Windows), retry (D16), log format.

## Phase B: orchestration

- [x] T7 `SKILL.md`: frontmatter, cwd-only rule, 3 phases with reference loading, Phase 2 save + print + `[y/n]` gate, Phase 3 incremental steps, final block with "remaining" list (C2). Under ~200 lines.
- [x] T8 Commit skill.

## Phase C: execution (one project at a time, fresh session in project folder)

- [x] T9 P1 run. Check: stack, >= 5 ground-truth matches, >= 1 CRITICAL/HIGH, boot + endpoints OK. Iterate (reset per D15, fix skill in master, recommit). On pass: commit refactored P1, copy report to `reports/audit-project-1.md`.
- [x] T10 Copy skill to P2; run; same checks; commit; `reports/audit-project-2.md`.
- [ ] T11 Copy skill to P3; run (seed first); same checks; commit; `reports/audit-project-3.md`.
- [ ] T12 If the skill changed during T10/T11, re-copy final version to all 3 projects (identical copies).

## Phase D: docs

- [ ] T13 README: A) Análise Manual (PT-BR, from spec ground truth + why), B) Construção da Skill, C) Resultados (counts, before/after trees, filled checklists, validation logs), D) Como Executar.
- [ ] T14 Final review against README acceptance criteria; commit.
