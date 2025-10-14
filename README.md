# 🎯 Orchestrator Toolkit

[![PyPI](https://img.shields.io/badge/PyPI-v2.0.1-blue)](https://pypi.org/project/orchestrator-toolkit/)
[![Python](https://img.shields.io/badge/python-≥3.10-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Stop losing track of what you're building.** Turn vague ideas into shipped features with a simple workflow that works with Claude Code.

## The Problem

You know this story:
- Start with a vague idea: "add authentication"
- Claude writes some code
- Come back tomorrow... wait, where were we?
- Repeat 10x, features ship randomly, nothing's tracked

## The Solution

**PLAN** what you're building → Get a detailed **SPEC** → **EXECUTE** and track progress.

Three simple concepts. Zero configuration. Works with Claude Code automatically.

## Quick Start (Seriously, 30 Seconds)

```bash
pip install orchestrator-toolkit

# You: "I want to add authentication"
otk plan "Add user authentication" --ready

# Auto-generate detailed spec
otk orchestrate

# Get your implementation checklist
otk scout SPEC-20251014-xxxxx
```

**That's it.** You now have:
- ✅ High-level plan in `ai_docs/plans/`
- ✅ Detailed technical spec in `ai_docs/specs/`
- ✅ Implementation checklist in `ai_docs/scout_reports/`
- ✅ All visible in your IDE, tracked in markdown

## Real Example: Adding Authentication

### Step 1: Create a PLAN (Your Idea)

```bash
$ otk plan "Add JWT authentication with OAuth 2.0 support" --ready

✅ Created: ai_docs/plans/PLAN-20251014-01K7A2-jwt-authentication.md
   Status: ready
```

**What you get** (`ai_docs/plans/PLAN-20251014-01K7A2-jwt-authentication.md`):
```markdown
---
id: PLAN-20251014-01K7A2-jwt-authentication
title: Add JWT authentication with OAuth 2.0 support
status: ready
---

## Objective
Add JWT authentication with OAuth 2.0 support

## Milestones
- [ ] Define objectives and success criteria
- [ ] Identify major components and phases
- [ ] Track overall progress
```

**Why this matters**: Your vague idea is now a trackable thing.

### Step 2: Generate a SPEC (Technical Details)

```bash
$ otk orchestrate

Created: ai_docs/specs/SPEC-20251014-01K7JE-implementation-for-jwt.md
✅ Created 1 SPEC(s)
```

**What you get** (`ai_docs/specs/SPEC-20251014-01K7JE-implementation-for-jwt.md`):
```markdown
---
id: SPEC-20251014-01K7JE-implementation-for-jwt
plan_id: PLAN-20251014-01K7A2-jwt-authentication
status: draft
---

## Objective
Implement technical solution for: Add JWT authentication

## Approach
### Technical Design
[Space for you/Claude to design the solution]

### Implementation Steps
- [ ] Analyze requirements from PLAN
- [ ] Design technical approach
- [ ] Implement solution
- [ ] Test and validate

## Acceptance Criteria
- [ ] All PLAN objectives met
- [ ] Tests passing
- [ ] Documentation updated
```

**Why this matters**: Template ready for you or Claude to fill in with technical details.

### Step 3: Get Implementation Checklist

```bash
$ otk scout SPEC-20251014-01K7JE

✅ Scout report saved: ai_docs/scout_reports/SPEC-...-scout.md

📋 Summary:
   - Development: 1 tasks
   - Implementation: 2 tasks
   - Testing: 1 tasks
   - Validation: 3 tasks
   - Documentation: 1 task
```

**What you get** (`ai_docs/scout_reports/SPEC-...-scout.md`):
```markdown
## Implementation Checklist

### 🔨 Development
- [ ] Implement solution

### ⚙️ Implementation
- [ ] Analyze requirements from PLAN
- [ ] Design technical approach

### 🧪 Testing
- [ ] Test and validate

### ✅ Validation
- [ ] Ensure: All PLAN objectives met
- [ ] Ensure: Tests passing
- [ ] Ensure: Documentation updated

### 📚 Documentation
- [ ] Update documentation with new features
```

**Why this matters**: Clear checklist of what to do next. No guessing.

### Step 4: Track Your Work

```bash
$ otk exec SPEC-20251014-01K7JE

✅ Execution log created: ai_docs/exec_logs/SPEC-...-exec-20251014-031237.md
```

**What you get**: Timestamped log to track what you're doing, decisions made, blockers hit.

---

## 🤖 The Killer Feature: Works With Claude Code

**Here's where it gets magical.**

When you use Claude Code with OTK, Claude becomes your project manager:

```
You: "Let's add search functionality to the app"

Claude: *runs* otk plan "Add search functionality" --ready
Claude: *runs* otk orchestrate
Claude: *runs* otk scout SPEC-20251014-xxxxx

Claude: "I've created a plan and implementation checklist.
         Ready to start? I'll track our progress in the exec log."

You: "Yes, let's do it"

Claude: *runs* otk exec SPEC-20251014-xxxxx
Claude: *starts implementing while updating the exec log*
```

**You get:**
- 📋 Automatic planning and scoping
- ✅ Implementation checklists
- 📝 Progress tracking in real-time
- 🔍 Full visibility in `ai_docs/` folder
- 🔄 Continuity across sessions (come back tomorrow, Claude knows where you are)

## Common Workflows

### 1. Solo Developer: "I have a vague idea"

```bash
# Start with your idea
otk plan "Improve app performance" --ready

# Get specific
otk orchestrate   # Creates detailed spec

# Figure out what to do
otk scout SPEC-xxx   # Gives you checklist

# Do the work
# (implement features, write code)

# Track progress
otk exec SPEC-xxx    # Log what you did
```

### 2. With Claude Code: "Claude, help me build X"

```
You: "Claude, I want to add user profiles with avatars"

Claude: [Creates PLAN automatically]
Claude: [Generates SPEC with technical details]
Claude: [Shows implementation checklist]
Claude: [Tracks execution while implementing]

Result: Feature shipped, everything documented automatically.
```

### 3. Coming Back to a Project

```bash
# Check what you're working on
ls ai_docs/plans/        # See all your PLANs
ls ai_docs/exec_logs/    # See recent work

# Pick up where you left off
cat ai_docs/exec_logs/SPEC-xxx-exec-latest.md
```

**With Claude Code**: Just say "What were we working on?" Claude reads the logs and catches you up.

### 4. Managing Multiple Features

```bash
# Create multiple PLANs
otk plan "Add search" --ready
otk plan "Improve performance"
otk plan "Refactor auth module"

# Generate specs for ready ones
otk orchestrate   # Only processes ready PLANs

# Work on them independently
otk scout SPEC-search-xxx
otk exec SPEC-search-xxx

# Later...
otk plan "Improve performance" --ready  # Mark ready when you're ready
otk orchestrate  # Creates spec
```

## Natural Language Interface

**Forget command syntax**. Just say what you want:

```bash
# Create plans
otk-new "plan 'Add OAuth login'"
otk-new "implement dark mode"
otk-new "feature for exporting data"

# Create specs
otk-new "spec for PLAN-xxx 'Database schema'"
otk-new "design API for PLAN-yyy"

# Execute
otk-new "execute SPEC-zzz"
otk-new "implement SPEC-www"

# Mark ready
otk-new "ready PLAN-xxx"
```

**The CLI figures out what you mean.** No memorizing commands.

## Installation

```bash
pip install orchestrator-toolkit
```

**No configuration needed.** Sensible defaults:
- ✅ Files go in `ai_docs/` (visible in your IDE)
- ✅ Owner from git username (or system user)
- ✅ Works immediately after install

## How It Works

### Three Concepts

**PLAN** (Your Goal)
- High-level: "Add authentication"
- Status tracking: draft → ready → in-spec → executing → done
- Links to SPECs when generated

**SPEC** (How To Build It)
- Technical details: "JWT tokens with RS256, 1-hour expiry..."
- Acceptance criteria: "Tests passing, security review done..."
- Implementation steps: Specific tasks to complete

**EXECUTE** (What You're Doing)
- Timestamped logs of actual work
- Track decisions, blockers, progress
- Multiple exec logs per SPEC (resume work across sessions)

### The Workflow

```
PLAN (your idea)
  ↓
  otk orchestrate
  ↓
SPEC (technical details)
  ↓
  otk scout
  ↓
Checklist (what to do)
  ↓
  otk exec
  ↓
EXECUTE (track progress)
```

### File Organization

```
your-project/
├── ai_docs/                        # Everything here
│   ├── plans/                      # PLANs (ideas)
│   │   └── PLAN-20251014-01K7A2-auth.md
│   ├── specs/                      # SPECs (how to build)
│   │   └── SPEC-20251014-01K7JE-jwt-impl.md
│   ├── exec_logs/                  # Execution tracking
│   │   └── SPEC-xxx-exec-20251014-031237.md
│   └── scout_reports/              # Implementation checklists
│       └── SPEC-xxx-scout.md
└── src/                            # Your actual code
```

**Everything in `ai_docs/`** means it's:
- ✅ Visible in your IDE
- ✅ Searchable (Cmd+P to find any PLAN/SPEC)
- ✅ Git-ignored by default (no noise in commits)
- ✅ Backed up with your code

## Command Reference

### Core Commands

| Command | What It Does | Example |
|---------|-------------|---------|
| `otk plan "title" [--ready]` | Create PLAN (your idea) | `otk plan "Add search" --ready` |
| `otk orchestrate` | Generate SPECs from ready PLANs | `otk orchestrate` |
| `otk scout SPEC-ID` | Get implementation checklist | `otk scout SPEC-20251014-xxxxx` |
| `otk exec SPEC-ID` | Track execution progress | `otk exec SPEC-20251014-xxxxx` |

### Helper Commands

| Command | What It Does | Example |
|---------|-------------|---------|
| `otk spec "title" [--plan ID]` | Create SPEC manually | `otk spec "API design" --plan PLAN-xxx` |
| `otk owner who` | See who owns files | `otk owner who` |
| `otk owner set NAME` | Set default owner | `otk owner set "DevTeam"` |
| `otk-new "anything"` | Natural language interface | `otk-new "plan 'Add OAuth'"` |

### Typical Flow

```bash
# 1. Start with idea
otk plan "Add real-time notifications" --ready

# 2. Generate detailed spec
otk orchestrate

# 3. Get implementation checklist
otk scout SPEC-20251014-xxxxx

# 4. Start working and track progress
otk exec SPEC-20251014-xxxxx

# (edit the exec log as you work)
```

## Advanced Usage

### Owner Management

By default, owner comes from:
1. `OTK_OWNER` environment variable
2. `.otk/.owner` file
3. Git `user.name`
4. System username

```bash
# See the resolution chain
otk owner who

# Set persistent owner
otk owner set "Backend Team"
```

### Working with Claude Code

**Tell Claude to use the workflow:**

```
You: "Claude, use the orchestrator workflow for this feature"

Claude: [Creates PLAN, orchestrates SPEC, scouts checklist, tracks execution]
```

**Or let Claude decide automatically:**

```
You: "Let's add GraphQL support"

Claude: "I'll create a plan for this...
        [Uses otk automatically if installed]"
```

### Multiple Developers

Each PLAN/SPEC has an owner:

```bash
export OTK_OWNER="Backend Team"
otk plan "Refactor database layer"

export OTK_OWNER="Frontend Team"
otk plan "Redesign dashboard UI"
```

Owners are tracked in frontmatter:

```yaml
---
id: PLAN-20251014-xxxxx
owner: Backend Team
---
```

### Custom Templates

Edit `.claude/templates/`:
- `plan.md` - Customize PLAN format
- `spec.md` - Customize SPEC format
- `task.md` - Legacy task format

Variables available: `${ID}`, `${TITLE}`, `${OWNER}`, `${DATE}`, `${STATUS}`

## Why ULID-Based IDs?

**Format**: `PLAN-20251014-01K7A2-human-readable-slug`

**Benefits**:
- ✅ **Sortable**: Latest PLANs at top (`ls -l` shows chronologically)
- ✅ **Unique**: Never collides, even across machines
- ✅ **Readable**: Date + slug tells you what it is
- ✅ **Searchable**: Cmd+P "PLAN-auth" finds all auth plans

**Old way** (v1.x): `PLAN-001`, `PLAN-002` (requires counter, hard to merge)
**New way** (v2.0): `PLAN-20251014-01K7A2-auth-system` (globally unique)

## Integration Examples

### With CI/CD

```yaml
# .github/workflows/check-plans.yml
- name: Check open PLANs
  run: |
    if ls ai_docs/plans/PLAN-*-ready.md 1> /dev/null 2>&1; then
      echo "⚠️ Ready PLANs waiting for orchestration"
      ls ai_docs/plans/*-ready.md
    fi
```

### With Pre-commit Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash
# Remind about tracking work
if git diff --cached --name-only | grep -q "^src/"; then
  if ! ls ai_docs/exec_logs/*$(date +%Y%m%d)*.md 1> /dev/null 2>&1; then
    echo "💡 Tip: Track your work with 'otk exec SPEC-xxx'"
  fi
fi
```

### With Documentation

```bash
# Generate project status
echo "# Project Status" > STATUS.md
echo "" >> STATUS.md
echo "## Active Plans" >> STATUS.md
ls ai_docs/plans/*.md | xargs -I {} basename {} >> STATUS.md
echo "" >> STATUS.md
echo "## In Progress" >> STATUS.md
ls ai_docs/exec_logs/*$(date +%Y%m%d)*.md 2>/dev/null | xargs -I {} basename {} >> STATUS.md
```

## Troubleshooting

### "No SPECs created when I run orchestrate"

**Check**: Does your PLAN have `status: ready`?

```bash
# See PLAN status
cat ai_docs/plans/PLAN-xxx.md | grep status

# Mark as ready
otk-new "ready PLAN-xxx"

# Or recreate with --ready flag
otk plan "Title" --ready
```

### "Where did my files go?"

**Check**: Default location is `ai_docs/`

```bash
ls ai_docs/plans/     # Your PLANs
ls ai_docs/specs/     # Your SPECs
ls ai_docs/exec_logs/ # Your execution logs
```

### "Wrong owner on files"

**Check**: Owner resolution chain

```bash
otk owner who

# Override with environment
export OTK_OWNER="YourName"

# Or set persistent
otk owner set "YourName"
```

## Migration from v1.x

### What Changed

**v1.x**: Task-based (`otk-task-new`, numeric IDs `T-001`)
**v2.0**: PLAN/SPEC/EXECUTE workflow (ULID IDs `PLAN-20251014-xxx`)

### Backward Compatibility

All v1.x commands still work:
```bash
otk-task-new "Feature"       # Still works
otk-plan-new "Implementation" # Still works
orchestrator-once            # Still works
```

### Gradual Migration

```bash
# Old way
otk-task-new "Add feature"

# New way (recommended)
otk plan "Add feature" --ready
otk orchestrate
```

See [CHANGELOG.md](CHANGELOG.md) for complete migration guide.

## FAQ

**Q: Do I need to use all three (PLAN/SPEC/EXECUTE)?**
A: No! Use what helps:
- Just PLANs for tracking ideas
- PLAN → SPEC for detailed planning
- Full workflow for complex features

**Q: Can I edit the generated files?**
A: Yes! They're markdown. Edit freely in your IDE.

**Q: Does Claude Code need this installed?**
A: No, but it helps! Claude can use your manual workflow or install OTK automatically.

**Q: What if I don't use Claude Code?**
A: Works great solo! Manual workflow, visible files, simple commands.

**Q: Can I change where files go?**
A: Yes: `export OTK_ARTIFACT_ROOT=my_folder`

**Q: Is there a UI?**
A: No. Files in `ai_docs/` are the UI. Use your IDE.

**Q: How do I delete a PLAN/SPEC?**
A: Just delete the markdown file. That's it.

**Q: Can multiple people use this on the same project?**
A: Yes! Set different owners (`otk owner set "Team Name"`)

## Links

- **📦 PyPI**: https://pypi.org/project/orchestrator-toolkit/
- **🧪 TestPyPI**: https://test.pypi.org/project/orchestrator-toolkit/2.0.1/
- **💻 GitHub**: https://github.com/arkaigrowth/orchestrator_toolkit
- **📖 Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **🤝 Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE)

---

**Version 2.0.1** • Built for [Claude Code](https://claude.ai) • Powered by [Pydantic v2](https://pydantic.dev)

**Stop losing track. Start shipping.** 🚀
