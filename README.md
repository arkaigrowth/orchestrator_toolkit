# 🎯 Orchestrator Toolkit

[![PyPI](https://img.shields.io/badge/PyPI-v2.0.0-blue)](https://pypi.org/project/orchestrator-toolkit/)
[![Python Version](https://img.shields.io/badge/python-≥3.10-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A lightweight PLAN → SPEC → EXECUTE workflow orchestration system for managing project development with Claude Code. Built with modern Python patterns and Pydantic v2.

## 🚀 Quick Start

```bash
# Install from PyPI
pip install orchestrator-toolkit

# Create a high-level PLAN
otk plan "Implement user authentication" --ready

# Auto-generate detailed SPEC from PLAN
otk orchestrate

# Generate implementation checklist
otk scout SPEC-20251014-xxxxx

# Track execution progress
otk exec SPEC-20251014-xxxxx
```

That's it! Your workflow is tracked in `ai_docs/` with ULID-based IDs.

## 🆕 What's New in v2.0.0

### 🔄 PLAN → SPEC → EXECUTE Workflow
- **PLANs**: High-level objectives and milestones
- **SPECs**: Detailed technical specifications with acceptance criteria
- **EXECUTE**: Implementation tracking with timestamped logs
- **Orchestration**: Automated PLAN → SPEC generation (`otk orchestrate`)

### 🎨 Modern CLI
```bash
otk plan "Feature title" [--ready]      # Create PLAN
otk spec "Spec title" [--plan ID]       # Create SPEC
otk exec SPEC-ID                        # Track execution
otk scout SPEC-ID                       # Generate checklist
otk orchestrate                         # Auto-create SPECs
otk owner who                           # Show owner resolution
```

### 🆔 ULID-Based Identifiers
- Format: `TYPE-YYYYMMDD-ULID6-slug`
- Example: `PLAN-20251014-01K7A2-user-authentication`
- Benefits: Sortable, unique, human-readable

### 🧪 Comprehensive Testing
- **195 tests passing** with comprehensive coverage
- Golden tests for routing patterns
- Integration tests for orchestration
- Owner resolution tests

## ✨ Core Features

### Workflow Management
- **📋 PLAN Phase**: Define high-level goals and milestones
- **📝 SPEC Phase**: Create detailed technical specifications
- **⚙️ EXECUTE Phase**: Track implementation progress with logs
- **🤖 Auto-Orchestration**: Generate SPECs from ready PLANs
- **🔍 Scout Reports**: Generate actionable implementation checklists

### Developer Experience
- **🗣️ Natural Language**: `otk-new "plan 'Feature X'"` understands intent
- **💻 Git-Style CLI**: Clean subcommands (`plan`, `spec`, `exec`, `scout`)
- **🎯 Smart Defaults**: Works out of the box, minimal configuration
- **👤 Owner Resolution**: Cascading owner detection (env → file → git → system)
- **🔗 Cross-Linking**: Automatic PLAN ↔ SPEC ↔ EXEC relationships

### Integration & Safety
- **🔌 Optional Integrations**: Archon and Mem0 adapters (gated by env vars)
- **🪝 Non-Blocking Hooks**: 3s timeout with retry and muting
- **🔒 Idempotent**: Safe to run orchestration multiple times
- **📁 Visible Artifacts**: All files in `ai_docs/` for IDE visibility

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install orchestrator-toolkit
```

### From Source

```bash
git clone https://github.com/arkaigrowth/orchestrator_toolkit_1.0.git
cd orchestrator_toolkit_1.0
pip install -e .
```

## 📖 Usage

### PLAN → SPEC → EXECUTE Workflow

**1. Create a PLAN (High-Level Objective)**
```bash
otk plan "Implement JWT authentication system" --ready

# Output:
# ✅ Created: ai_docs/plans/PLAN-20251014-01K7A2-jwt-authentication.md
# Status: ready (ready for orchestration)
```

**2. Generate SPEC Automatically**
```bash
otk orchestrate

# Output:
# Created: ai_docs/specs/SPEC-20251014-01K7JE-implementation-for-jwt.md
# ✅ Created 1 SPEC(s)
```

**3. Generate Implementation Checklist**
```bash
otk scout SPEC-20251014-01K7JE

# Output:
# ✅ Scout report saved: ai_docs/scout_reports/SPEC-...-scout.md
# 📋 Summary:
#    - Development: 3 tasks
#    - Testing: 2 tasks
#    - Documentation: 1 task
```

**4. Track Execution**
```bash
otk exec SPEC-20251014-01K7JE

# Output:
# ✅ Execution log created: ai_docs/exec_logs/SPEC-...-exec-20251014-031237.md
```

### Natural Language Interface

The `otk-new` command understands natural language:

```bash
# Create PLAN
otk-new "plan 'OAuth 2.0 implementation'"
otk-new "add feature for user profiles"

# Create SPEC
otk-new "spec for PLAN-20251014-xxxxx 'Database schema'"
otk-new "design API endpoints for PLAN-xyz"

# Mark ready
otk-new "ready PLAN-20251014-xxxxx"

# Execute
otk-new "execute SPEC-20251014-yyyyy"
```

### Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `otk plan "title" [--ready]` | Create PLAN | `otk plan "Auth system" --ready` |
| `otk spec "title" [--plan ID]` | Create SPEC | `otk spec "JWT middleware" --plan PLAN-xxx` |
| `otk exec SPEC-ID` | Track execution | `otk exec SPEC-20251014-xxxxx` |
| `otk scout SPEC-ID` | Generate checklist | `otk scout SPEC-20251014-xxxxx` |
| `otk orchestrate` | Auto-create SPECs | `otk orchestrate` |
| `otk owner who` | Show owner chain | `otk owner who` |
| `otk owner set NAME` | Set persistent owner | `otk owner set "DevTeam"` |

### Legacy Commands (Backward Compatible)

```bash
otk-task-new "title" --owner name    # Create task (deprecated)
otk-plan-new "title"                 # Create numbered plan (deprecated)
orchestrator-once                    # Process assigned tasks (deprecated)
```

## 🏗️ Project Structure

```
your-project/
├── ai_docs/                    # All artifacts (gitignored)
│   ├── plans/                  # PLAN documents (PLAN-*.md)
│   ├── specs/                  # SPEC documents (SPEC-*.md)
│   ├── exec_logs/              # Execution logs (SPEC-*-exec-*.md)
│   └── scout_reports/          # Implementation checklists
├── .claude/                    # Claude-specific config
│   ├── templates/              # PLAN/SPEC/TASK templates
│   └── commands/               # Shell script shortcuts
└── src/                        # Your project code
```

### PLAN File Format

```yaml
---
id: PLAN-20251014-01K7A2-user-authentication
title: Implement user authentication system
owner: DevTeam
created: 2025-10-14T01:23:45Z
status: ready                   # draft | ready | in-spec | executing | done
spec_id: ""                     # Linked SPEC (set by orchestrator)
---

## Objective
Build secure JWT-based authentication with OAuth 2.0 support.

## Milestones
- [ ] Design authentication flow
- [ ] Implement JWT middleware
- [ ] Add OAuth providers
- [ ] Security audit
```

### SPEC File Format

```yaml
---
id: SPEC-20251014-01K7JE-jwt-middleware-implementation
plan_id: PLAN-20251014-01K7A2-user-authentication
title: JWT Token Middleware Implementation
owner: BackendTeam
created: 2025-10-14T02:15:30Z
status: draft                   # draft | designed | built | done
---

## Objective
Implement JWT token generation, validation, and refresh logic.

## Approach
### Technical Design
- Use `pyjwt` library with RS256 signing
- Token expiry: 1 hour (access), 7 days (refresh)
...

### Implementation Steps
- [ ] Install and configure pyjwt
- [ ] Create token generation service
- [ ] Implement validation middleware
- [ ] Add refresh token endpoint
...

## Acceptance Criteria
- [ ] All tests passing with ≥90% coverage
- [ ] Security review completed
- [ ] Documentation updated
```

## 🔧 Configuration

### Environment Variables

```bash
# Artifact directory (default: ai_docs)
export OTK_ARTIFACT_ROOT=ai_docs

# Owner (overrides all other sources)
export OTK_OWNER=YourName

# Optional: Enable Archon integration
export OTK_ARCHON_ENABLED=1
export OTK_ARCHON_BASE_URL=http://localhost:8787
export OTK_ARCHON_API_KEY=your-key

# Optional: Enable Mem0 integration
export OTK_MEM0_ENABLED=1
export OTK_MEM0_API_URL=https://api.mem0.ai/v1
export OTK_MEM0_API_KEY=your-key
```

### Owner Resolution Chain

```
1. Environment: OTK_OWNER
2. File: .otk/.owner
3. Git: user.name
4. System: current user
```

Use `otk owner who` to see the resolution chain.

### Custom Templates

Edit templates in `.claude/templates/`:
- `plan.md` - PLAN format
- `spec.md` - SPEC format
- `task.md` - Task format (legacy)

Variables: `${ID}`, `${TITLE}`, `${OWNER}`, `${DATE}`, `${STATUS}`

## 🔌 Integration with Claude Code

When using with Claude Code:
```
User: "Create a plan for implementing search functionality"
Claude: *runs* otk plan "Implement search functionality" --ready
Claude: *runs* otk orchestrate
Claude: "Created PLAN-xxx and SPEC-yyy. Ready to implement!"
```

Claude can:
- Create and manage PLANs/SPECs
- Run orchestration automatically
- Generate scout reports for guidance
- Track execution progress

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install orchestrator-toolkit` |
| Files not in `ai_docs/` | Set `export OTK_ARTIFACT_ROOT=ai_docs` |
| Wrong owner assigned | Check `otk owner who` and set via `otk owner set NAME` |
| SPEC not created | Ensure PLAN has `status: ready` and `spec_id: ""` |
| Orchestrator no-op | Run `otk orchestrate` - only processes ready PLANs |

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Ensure all tests pass (`pytest`)
5. Submit pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 🔄 Migration from v1.x

### Key Changes
- **Tasks → PLANs**: Use `otk plan` instead of `otk-task-new`
- **Numeric IDs → ULIDs**: `PLAN-20251014-xxxxx` instead of `P-001`
- **New Commands**: `orchestrate`, `scout`, `owner`, `exec`
- **Automatic SPECs**: Run `otk orchestrate` to generate from ready PLANs

### Backward Compatibility
All v1.x commands still work:
```bash
otk-task-new "title"      # Still supported
otk-plan-new "title"      # Still supported
orchestrator-once         # Still supported
```

### Gradual Migration
```bash
# Old way (v1.x)
otk-task-new "Implement feature"

# New way (v2.0)
otk plan "Implement feature" --ready
otk orchestrate
```

See [CHANGELOG.md](CHANGELOG.md) for complete migration guide.

## 🙏 Acknowledgments

- Built for [Claude Code](https://claude.ai)
- Powered by [Pydantic v2](https://pydantic.dev)
- Inspired by clean, effective workflows

---

**Version**: 2.0.0
**PyPI**: https://pypi.org/project/orchestrator-toolkit/
**Repository**: https://github.com/arkaigrowth/orchestrator_toolkit_1.0
**Documentation**: See [docs/](docs/) for detailed guides
