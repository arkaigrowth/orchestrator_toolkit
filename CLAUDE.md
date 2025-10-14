# CLAUDE.md — Orchestrator Toolkit 1.3

## 🧭 Purpose

This file defines the permissions, structure, and conventions used when operating within this repository.
Claude (and its subagents) act as implementers of the PLAN → SPEC → EXECUTE workflow.

---

## ⚙️ Environment Rules

**Artifact root:** `ai_docs/`

- Plans → `ai_docs/plans/`
- Specs → `ai_docs/specs/`
- Exec logs → `ai_docs/exec_logs/`

**Integrations (optional):**

- Archon API → gated by `OTK_ARCHON_ENABLED`
- Mem0 API → gated by `OTK_MEM0_ENABLED`

**Hook policy:** Non-blocking. Log failures to `run_log.md`.

---

## 🧩 Allowed Actions

Claude may:

- Run repo-local CLI commands:
  - `otk-new "<text>"`
  - `otk-plan-new`, `otk-spec-new`, `otk-exec`
  - `task-new`, `plan-new`, `orchestrator-once`
  - `pytest`, `make plan`, `make spec`, `make exec`
- Create, edit, and summarize files inside `ai_docs/` and `.claude/`.
- Update `.claude/templates/*.md` as needed.
- Write Python source files under `src/orchestrator_toolkit/`.
- Modify `pyproject.toml`, `Makefile`, and documentation (`README.md`, `INSTALLATION.md`).
- Trigger hooks (Archon, Mem0) asynchronously if enabled.

Claude may **not**:

- Access external APIs other than Archon/Mem0 via configured URLs.
- Delete system or hidden files.
- Modify outside the repo boundary.

---

## 🧠 Agent Structure

**Main Agent (Implementer):**

- Responsible for coordinating all work described in active PLAN files.

**Subagents:**Claude may spawn subagents **per SPEC or phase**, but only within this repository.Each subagent must:

1. Create a new SPEC file in `ai_docs/specs/` using ULID+date+slug ID format.
2. Work strictly inside its assigned SPEC scope.
3. Update its parent PLAN with completion status.

Allowed subagent scopes:

- `PHASE: phrase_router`
- `PHASE: ids`
- `PHASE: cli`
- `PHASE: hooks`
- `PHASE: tests`
- `PHASE: docs`

Each subagent terminates automatically after executing its assigned SPEC.

---

## 💬 Slash Commands

| Command                   | Description                                           |
| ------------------------- | ----------------------------------------------------- |
| `/PLAN "title"`         | Create a new PLAN                                     |
| `/SPEC PLAN-ID "title"` | Create a new SPEC under an existing PLAN              |
| `/EXEC SPEC-ID`         | Execute an existing SPEC                              |
| `/OTK "free text"`      | Use phrase router to infer intent (PLAN/SPEC/EXECUTE) |

These map to local commands:

- `/PLAN` → `otk-new "plan ..."`
- `/SPEC` → `otk-new "spec for PLAN-..." ...`
- `/EXEC` → `otk-new "execute SPEC-..."`
- `/OTK` → `otk-new "<free text>"`

---

## 🧪 Workflow Summary

1. **User prompt →** `otk-new "<text>"` → routed via `phrase_router.py`.
2. **PLAN** created if context missing (default entry point).
3. **SPEC** created or linked to PLAN on request.
4. **EXECUTE** runs all phases (scout → design → build) with hook updates.
5. **Hooks** call Archon & Mem0 asynchronously for milestone tracking.
6. **Subagents** may handle individual SPECs but must remain repo-bound.

---

## 🛡️ Safety Defaults

- All external calls wrapped in try/except with 5s timeout.
- No persistent environment modification.
- Always prefer idempotent operations (ULIDs prevent collisions).
- Claude must confirm any destructive file change before proceeding.

---

✅ *Last updated: 2025-10-12 (PLAN/SPEC/EXEC MVP initialized)*
Maintainers: **alexkamysz / Coach Chad**
