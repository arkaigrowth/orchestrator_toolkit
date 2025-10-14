# Changelog

All notable changes to the Orchestrator Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-14

### 🎉 Major Release: PLAN/SPEC/EXECUTE Workflow

This release introduces a complete workflow overhaul, moving from simple task management to a sophisticated PLAN → SPEC → EXECUTE state machine with orchestration.

### Added

#### Core Features
- **PLAN/SPEC/EXECUTE Workflow**: Complete state machine implementation
  - PLANs define high-level objectives
  - SPECs provide detailed technical specifications
  - EXECUTE tracks implementation progress
- **Orchestrator Function**: Automated PLAN → SPEC workflow progression
  - `orchestrator_plans()` creates SPECs from ready PLANs
  - Idempotent operation prevents duplicate SPECs
  - State transitions tracked automatically
- **Natural Language Interface**: Intuitive command routing
  - `otk-new "implement auth system"` → Creates PLAN
  - `otk-new "spec for plan-123"` → Creates SPEC
  - `otk-new "execute spec-456"` → Creates execution log
  - `otk-new "ready plan-789"` → Marks PLAN as ready

#### New Commands
- **Clean CLI Subcommands**:
  - `otk plan [title] [--ready]` - Create PLANs
  - `otk spec [title] [--plan ID]` - Create SPECs
  - `otk exec [spec-id]` - Execute SPECs
  - `otk scout [spec-id]` - Generate implementation checklist
  - `otk orchestrate` - Run PLAN → SPEC automation
- **Owner Management**:
  - `otk owner who` - Show owner resolution chain
  - `otk owner set <name>` - Set persistent owner
- **ULID-Based IDs**: Sortable, unique identifiers
  - Format: `TYPE-YYYYMMDD-ULID6-slug`
  - Example: `PLAN-20251014-01K7FM-auth-system`

#### Infrastructure
- **Generic Hook System**: Simplified state transition hooks
  - `fire_hook()` replaces per-event methods
  - 3-second timeout with 2 retries
  - Non-blocking with jittered backoff
- **Enhanced Owner Resolution**: Clear hierarchy
  1. Environment: `OTK_OWNER`
  2. File: `.otk/.owner`
  3. Git: `user.name`
  4. System: Current user
- **Comprehensive Testing**:
  - 195 tests passing
  - Golden tests for phrase router
  - Integration tests for orchestrator
  - State machine validation

### Changed

#### Workflow Changes
- **Tasks → PLANs**: Tasks now create PLANs (backward compatible)
- **ID Format**: Moved from numeric (T-001) to ULID-based
- **Template System**: Templates now support variable status
- **Directory Structure**:
  ```
  ai_docs/
  ├── plans/     # PLAN documents
  ├── specs/     # SPEC documents
  ├── exec_logs/ # Execution tracking
  └── scout_reports/ # Implementation checklists
  ```

#### API Changes
- `OrchSettings` now includes `specs_dir` and `exec_logs_dir`
- `phrase_router` handles READY command for state transitions
- Hook system simplified to generic `fire_hook()` function

### Fixed
- Template status field now properly uses `${STATUS}` variable
- Owner resolution order corrected (file overrides git)
- Idempotency guaranteed through `spec_id` field in PLANs

### Migration Guide

#### From v1.x to v2.0

1. **Existing Tasks Continue Working**
   - Legacy T-XXX format still supported
   - `task-new` command remains available
   - `orchestrator-once` creates PLANs from tasks

2. **Adopt New Workflow Gradually**
   ```bash
   # Old way (still works)
   otk task-new "Implement feature"

   # New way (recommended)
   otk plan "Implement feature"
   otk orchestrate  # Auto-creates SPEC when ready
   otk exec SPEC-xxx  # Track execution
   ```

3. **Update Scripts**
   - Replace `otk-task-new` with `otk plan`
   - Use `otk-new` for natural language interface
   - Add `otk scout` for implementation guidance

### Technical Details

#### State Transitions
```
PLAN: draft → ready → in-spec → executing → done
SPEC: draft → designed → built → done
```

#### Idempotency Guarantees
- PLANs with `spec_id` set won't get duplicate SPECs
- Orchestrator is safe to run multiple times
- Atomic writes ensure consistency

#### Performance
- Parallel tool execution support
- Efficient batch operations
- Smart routing with priority hierarchy

---

## [1.0.1] - 2025-10-12

### Fixed
- Documentation updates and clarifications
- Minor bug fixes in task generation

### Added
- Improved error messages for better debugging
- Enhanced test coverage

## [1.0.0] - 2025-10-12

### Added
- Initial release of Orchestrator Toolkit
- Basic task management system
- Task to plan orchestration
- Integration with Archon and Mem0 services
- Command-line interface with multiple entry points
- Settings management with environment variable support

### Features
- Task creation and tracking
- Automatic plan generation from tasks
- Owner resolution system
- Atomic file operations for data integrity
- Extensible adapter system for external services

---

For detailed documentation, see the [README](README.md) and the [docs](docs/) directory.