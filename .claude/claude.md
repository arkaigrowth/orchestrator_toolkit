# Claude Handoff — Orchestrator Toolkit 2.0

**You are the repo assistant. Follow the PLAN→SPEC→EXECUTE workflow.**

## Quick Start Commands

### Natural Language Interface (Recommended)
- `otk-new "plan 'Implement authentication'"` → Creates a PLAN with ULID-based ID
- `otk-new "spec for P-01JCAKE... 'Database design'"` → Creates a SPEC linked to a PLAN
- `otk-new "execute S-01JCBMN..."` → Creates execution log for a SPEC

### Makefile Shortcuts
- `make plan TITLE="Your plan title"` → Create a new PLAN
- `make spec PLAN=P-01JC... TITLE="Your spec"` → Create a SPEC for a PLAN
- `make exec SPEC=S-01JC...` → Execute a SPEC
- `make new TEXT="any otk command"` → Run any otk-new command

### Direct Commands
- `otk-plan-new "Plan title"` → Create PLAN directly
- `otk-spec-new P-01JC... "Spec title"` → Create SPEC with plan reference
- `otk-exec S-01JC...` → Execute a SPEC directly

### Legacy Commands (Backward Compatible)
- `task-new "TITLE" --owner NAME` → creates `tasks/T-*.md` (deprecated)
- `plan-new "TITLE" --owner NAME` → creates numbered plan (use otk-new instead)
- `orchestrator-once` → process assigned tasks
- `plan-summarize P-XXXX` → creates summary checklist

## Workflow: PLAN → SPEC → EXECUTE

1. **PLAN Phase**: High-level project planning
   - Creates `ai_docs/plans/P-[ULID].md`
   - Defines overall objectives and milestones
   - Example: "Implement user authentication system"

2. **SPEC Phase**: Detailed technical specifications
   - Creates `ai_docs/specs/S-[ULID].md`
   - Links to parent PLAN
   - Defines acceptance criteria and approach
   - Example: "JWT token implementation for auth"

3. **EXECUTE Phase**: Implementation tracking
   - Creates `ai_docs/exec_logs/S-[ULID]-exec-[timestamp].md`
   - Tracks progress against SPEC
   - Documents actual implementation steps

## File Structure
```
ai_docs/
├── plans/         # PLAN documents (P-[ULID].md)
├── specs/         # SPEC documents (S-[ULID].md)
└── exec_logs/     # Execution logs (S-[ULID]-exec-*.md)
```

## Guardrails
- Keep **all generated files small and readable**
- Use ULID-based IDs for uniqueness and sortability
- Link SPECs to PLANs, EXECs to SPECs
- If Archon/Mem0 env is missing, **do not fail**: proceed and log a warning

## Best Practices
- Use natural language with `otk-new` for flexibility
- Create PLANs for major features or initiatives
- Break PLANs into multiple SPECs for manageable chunks
- Track execution progress in real-time with exec logs
- Use Makefile shortcuts for quick access during development

Stay within these commands unless instructed to extend the toolkit.

## Slash commands (intake)
- /INTAKE <text> — Send <text> to the intake-scribe agent to create the right artifact.
  Examples:
  - /INTAKE add oauth login → creates PLAN
  - /INTAKE spec for PLAN-20251013-01K7EP “react components” → creates SPEC
  - /INTAKE execute SPEC-20251013-02NZ6Q → triggers EXECUTE

Allowed actions for intake-scribe:
- Run Bash only to call: `otk-new`, `otk plan`, `otk spec`, `otk exec`, `otk orchestrate`
- Read & list files under ai_docs/