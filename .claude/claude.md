# Claude Handoff — Orchestrator Toolkit 1.0 (MVP)

**You are the repo assistant. Follow only these commands unless asked otherwise.**

## Primary verbs (run in this repo)
- `task-new "TITLE" --owner NAME` → creates `tasks/T-*.md` from template
- `orchestrator-once` → for each task with `status: assigned`, scaffold `plans/P-*.md` and write "Next step" via `hooks/post_to_statusline.sh`
- `plan-new "TITLE" --owner NAME` → optional manual plan (rare)
- `plan-summarize P-XXXX` → creates `plans/P-XXXX.summary.md` checklist for a human (e.g., CPA)

## Guardrails
- Keep **all generated files small and readable**.
- Do **not** commit large imports. If humans need docs, link paths only.
- If Archon/Mem0 env is missing, **do not fail**: proceed and log a warning.

## When asked to import/attach docs
1) Create a `docs/` folder *at project root* (not in this MVP by default).
2) Add a bullet list of paths into the relevant plan file under “References”.
3) Avoid copying binaries into git; prefer paths.

Stay within these commands unless instructed to extend the toolkit.
