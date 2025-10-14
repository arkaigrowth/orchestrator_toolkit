# 🎯 Orchestrator Toolkit

[![PyPI](https://img.shields.io/badge/PyPI-v2.0.2-blue)](https://pypi.org/project/orchestrator-toolkit/)
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

## Quick Start (30 Seconds)

### Natural Language (Recommended)

```bash
pip install orchestrator-toolkit

# Just say what you want
otk-new "plan 'Add user authentication' and mark it ready"

# Auto-generate detailed spec
otk-new "generate spec for ready plans"

# Get implementation checklist
otk-new "scout the spec"
```

**Why this works**: No flags, no IDs to remember. Just say what you want.

### CLI Equivalents (for scripts & automation)

```bash
otk plan "Add user authentication" --ready
otk orchestrate
otk scout SPEC-20251014-xxxxx
```

**When to use**: Automation, CI/CD, when you need precise control.

---

**That's it.** You now have:
- ✅ High-level plan in `ai_docs/plans/`
- ✅ Detailed technical spec in `ai_docs/specs/`
- ✅ Implementation checklist in `ai_docs/scout_reports/`
- ✅ All visible in your IDE, tracked in markdown

## How Orchestration Works (Important!)

**The Rules** (prevents "where's my SPEC?" issues):

`otk orchestrate` ONLY processes PLANs where:
- ✅ `status: ready` **AND**
- ✅ `spec_id: ""` (empty)

**What Happens**:

```
BEFORE orchestrate:
├── PLAN: status=ready, spec_id=""
└── (no SPEC exists yet)

AFTER orchestrate:
├── PLAN: status=in-spec, spec_id="SPEC-20251014-01K7JE"
└── SPEC: plan_id="PLAN-20251014-01K7A2", status=draft
```

**Idempotency**: Safe to re-run `otk orchestrate`—won't create duplicates!

**Status Flow**:
```
PLAN:  draft → ready → in-spec → executing → done
SPEC:  draft → designed → built → done
```

## Real Example: Adding Authentication

### Step 1: Create a PLAN (Your Idea)

```bash
$ otk-new "plan 'Add JWT authentication with OAuth 2.0 support' and mark ready"

✅ Created: ai_docs/plans/PLAN-20251014-01K7A2-jwt-authentication.md
   Status: ready
```

**What you get** (`ai_docs/plans/PLAN-20251014-01K7A2-jwt-authentication.md`):
```markdown
---
id: PLAN-20251014-01K7A2-jwt-authentication
title: Add JWT authentication with OAuth 2.0 support
owner: YourName
created: 2025-10-14T01:23:45Z
status: ready          # draft|ready|in-spec|executing|done
spec_id: ""            # filled after orchestrate creates SPEC
---

## Objective
Add JWT authentication with OAuth 2.0 support

## Milestones
- [ ] Design authentication flow
- [ ] Implement JWT middleware
- [ ] Add OAuth providers
- [ ] Security audit
```

**Why this matters**: Your vague idea is now a trackable thing with a unique ID.

### Step 2: Generate a SPEC (Technical Details)

```bash
$ otk orchestrate

Created: ai_docs/specs/SPEC-20251014-01K7JE-implementation-for-jwt.md
✅ Created 1 SPEC(s)

# PLAN updated automatically:
#   spec_id: "SPEC-20251014-01K7JE"
#   status: "in-spec"
```

**What you get** (`ai_docs/specs/SPEC-20251014-01K7JE-implementation-for-jwt.md`):
```markdown
---
id: SPEC-20251014-01K7JE-implementation-for-jwt
plan_id: PLAN-20251014-01K7A2-jwt-authentication
title: JWT Token Middleware Implementation
owner: YourName
created: 2025-10-14T02:15:30Z
status: draft          # draft|designed|built|done
---

## Objective
Implement technical solution for: Add JWT authentication with OAuth 2.0 support

## Approach
### Technical Design
- Use `pyjwt` library with RS256 signing
- Token expiry: 1 hour (access), 7 days (refresh)
- Store refresh tokens in database

### Implementation Steps
- [ ] Install and configure pyjwt
- [ ] Create token generation service
- [ ] Implement validation middleware
- [ ] Add refresh token endpoint
- [ ] Write unit tests for all flows

## Acceptance Criteria
- [ ] All tests passing with ≥90% coverage
- [ ] Security review completed
- [ ] Documentation updated
- [ ] OAuth 2.0 flow working for GitHub + Google
```

**Why this matters**: Template filled by you or Claude with specific technical details.

### Step 3: Get Implementation Checklist

```bash
$ otk scout SPEC-20251014-01K7JE

🔍 Scouting: SPEC-20251014-01K7JE-implementation-for-jwt.md
   Found 8 implementation tasks
✅ Scout report saved: ai_docs/scout_reports/SPEC-...-scout.md

📋 Summary:
   - Development: 1 tasks
   - Implementation: 4 tasks
   - Testing: 1 tasks
   - Validation: 2 tasks
```

**What you get** (`ai_docs/scout_reports/SPEC-...-scout.md`):
```markdown
## Implementation Checklist for SPEC-20251014-01K7JE

### 🔨 Development
- [ ] Install and configure pyjwt

### ⚙️ Implementation
- [ ] Create token generation service
- [ ] Implement validation middleware
- [ ] Add refresh token endpoint
- [ ] Write unit tests for all flows

### 🧪 Testing
- [ ] Ensure all tests passing with ≥90% coverage

### ✅ Validation
- [ ] Security review completed
- [ ] OAuth 2.0 flow working for GitHub + Google
```

**What scout does**: Reads the SPEC's objectives and acceptance criteria, then generates an actionable checklist in `ai_docs/scout_reports/`.

**Why this matters**: Clear checklist of what to do next. No guessing.

### Step 4: Track Your Work

```bash
$ otk exec SPEC-20251014-01K7JE

✅ Execution log created: ai_docs/exec_logs/SPEC-...-exec-20251014-031237.md
```

**What you get**: Timestamped log to track implementation, decisions made, blockers hit.

---

## 🤖 The Killer Feature: Works With Claude Code

**Here's where it gets magical.** Claude becomes your deterministic project manager.

### Who Creates Plans?

**You can:**
```bash
otk-new "plan 'Add search functionality' and mark ready"
```

**Or ask Claude:**
```
You: "Create a plan for adding search to the app"
Claude: *runs* otk plan "Add search functionality" --ready
```

**Best practice**: For large repos, use a "Planner" subagent that reads the repo structure first, then creates the PLAN with context.

### Example: Complete Workflow with Claude

```
You: "Let's add user profiles with avatars"

Claude (runs these exact commands):

1. otk plan "User profiles with avatars" --ready
   ✅ Created PLAN-20251014-01K7A2

2. otk orchestrate
   ✅ Created SPEC-20251014-01K7JE
   ✅ Updated PLAN: spec_id filled, status→in-spec
   (Idempotent—safe to re-run if interrupted)

3. otk scout SPEC-20251014-01K7JE
   ✅ Generated checklist: 8 tasks across 5 categories

Claude: "Ready to implement? I'll track our progress."

You: "Yes, let's do it"

4. otk exec SPEC-20251014-01K7JE
   ✅ Execution log: SPEC-...-exec-20251014-031237.md

Claude: *implements while updating the exec log*
```

**Why this is powerful**:
- ✅ Automatic planning and scoping
- ✅ Idempotent (safe to resume after interruption)
- ✅ Full visibility in `ai_docs/` folder
- ✅ Continuity across sessions (come back tomorrow, Claude knows where you are)

## Command Map

| I want to... | Natural Language | CLI Equivalent | When to use |
|-------------|------------------|----------------|-------------|
| Create plan and mark ready | `otk-new "plan 'Add auth' and mark ready"` | `otk plan "Add auth" --ready` | **NL**: Quick start<br>**CLI**: Scripts |
| Generate specs from ready plans | `otk-new "generate specs"` | `otk orchestrate` | **NL**: Don't know PLAN IDs<br>**CLI**: Automation |
| Create spec for specific plan | `otk-new "spec for PLAN-xxx 'DB schema'"` | `otk spec "DB schema" --plan PLAN-xxx` | **NL**: Conversational<br>**CLI**: Precise control |
| Get implementation checklist | `otk-new "scout SPEC-xxx"` | `otk scout SPEC-xxx` | Either works |
| Track execution | `otk-new "execute SPEC-xxx"` | `otk exec SPEC-xxx` | Either works |
| Mark plan ready later | `otk-new "ready PLAN-xxx"` | Edit PLAN file: `status: ready` | **NL**: Quick<br>**Edit**: Batch changes |
| See owner resolution | — | `otk owner who` | Debugging |
| Set persistent owner | — | `otk owner set "Team Name"` | Multi-developer |

💡 **Pro Tip**: Use natural language for interactive work, CLI for automation.

## Common Workflows

### 1. Solo Developer: "I have a vague idea"

```bash
# Start with your idea
otk-new "plan 'Improve app performance' and mark ready"

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
You: "Claude, I want to add dark mode with system preference detection"

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

**With Claude Code**: Just say "What were we working on?" Claude reads the logs and catches you up instantly.

### 4. Managing Multiple Features

```bash
# Create multiple PLANs
otk-new "plan 'Add search' and mark ready"
otk-new "plan 'Improve performance'"
otk-new "plan 'Refactor auth module'"

# Generate specs for ready ones
otk orchestrate   # Only processes PLANs with status=ready

# Work on them independently
otk scout SPEC-search-xxx
otk exec SPEC-search-xxx

# Later... mark another ready
otk-new "ready PLAN-performance-xxx"
otk orchestrate  # Creates new SPEC
```

## Installation

```bash
# Standard installation
pip install orchestrator-toolkit

# CLI-only (isolated, no project pollution)
pipx install orchestrator-toolkit

# From TestPyPI (latest)
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            orchestrator-toolkit
```

**No configuration needed.** Sensible defaults:
- ✅ Files go in `ai_docs/` (visible in your IDE)
- ✅ Owner from git username (or system user)
- ✅ Works immediately after install

## How It Works

### Three Concepts

**PLAN** (Your Goal)
- High-level: "Add authentication"
- Status tracking: `draft → ready → in-spec → executing → done`
- Links to SPECs via `spec_id` field

**SPEC** (How To Build It)
- Technical details: "JWT tokens with RS256, 1-hour expiry..."
- Acceptance criteria: "Tests passing, security review done..."
- Implementation steps: Specific tasks to complete
- Links back to PLAN via `plan_id` field

**EXECUTE** (What You're Doing)
- Timestamped logs of actual work
- Track decisions, blockers, progress
- Multiple exec logs per SPEC (resume work across sessions)

### The Workflow (Deterministic)

```
PLAN (your idea)
  ↓  (status=ready AND spec_id="" required)
  otk orchestrate (idempotent)
  ↓
SPEC (technical details)
  ↓
  otk scout
  ↓
Checklist (what to do)
  ↓
  otk exec
  ↓
Execution log (what you did)
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

## Advanced Usage

### Owner Management

**Owner resolution cascade**:
`OTK_OWNER` env → `.otk/.owner` file → `git config user.name` → system username

```bash
# See the resolution chain
otk owner who

# Override for session
export OTK_OWNER="Backend Team"

# Set persistent owner
otk owner set "Backend Team"  # Creates .otk/.owner
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
status: ready
spec_id: ""
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

## Troubleshooting

### No SPECs created when running orchestrate?

**Decision tree**:
```
orchestrate ran → No SPEC appeared
    ↓
Check: cat ai_docs/plans/PLAN-xxx.md | grep "status:"
    ↓
├─ status: draft → Fix: otk-new "ready PLAN-xxx"
├─ status: ready, spec_id: "SPEC-..." → Already has SPEC! Check ai_docs/specs/
└─ status: ready, spec_id: "" → Should work. Try: rm -rf .otk/cache && otk orchestrate
```

**Quick fixes**:
```bash
# See PLAN status
cat ai_docs/plans/PLAN-xxx.md | head -10

# Mark ready
otk-new "ready PLAN-xxx"

# Or recreate with --ready flag
otk plan "Title" --ready

# Safe to re-run (idempotent)
otk orchestrate
```

**Remember**: `otk orchestrate` is idempotent—safe to run multiple times.

### SPEC "disappeared"?

**Check files exist**:
```bash
ls ai_docs/specs/              # SPECs are always files
cat ai_docs/plans/PLAN-xxx.md | grep spec_id
```

**If spec_id is empty**: The SPEC wasn't created. Run `otk orchestrate` again (safe, idempotent).

**If spec_id shows a SPEC**: The SPEC file exists in `ai_docs/specs/`, you just need to find it:
```bash
ls ai_docs/specs/SPEC-20251014-*
```

### Wrong owner on files?

**Check resolution chain**:
```bash
otk owner who

# Override with environment
export OTK_OWNER="YourName"

# Or set persistent
otk owner set "YourName"
```

**Owner cascade** (first match wins):
1. `OTK_OWNER` environment variable
2. `.otk/.owner` file in current directory
3. `git config user.name`
4. System username

## Migration from v1.x

### What Changed

**v1.x**: Task-based (`otk-task-new`, numeric IDs `T-001`)
**v2.0**: PLAN/SPEC/EXECUTE workflow (ULID IDs `PLAN-20251014-xxx`)

### Backward Compatibility

All v1.x commands still work:
```bash
otk-task-new "Feature"       # Still works
otk-plan-new "Implementation" # Still works (creates numbered plan)
orchestrator-once            # Still works
```

### Gradual Migration

```bash
# Old way
otk-task-new "Add feature"

# New way (recommended)
otk-new "plan 'Add feature' and mark ready"
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

**Q: Why did my SPEC not appear?**
A: Check that your PLAN has `status: ready` AND `spec_id: ""`. Then run `otk orchestrate` (safe to re-run).

## Links

- **📦 PyPI**: https://pypi.org/project/orchestrator-toolkit/
- **🧪 TestPyPI**: https://test.pypi.org/project/orchestrator-toolkit/2.0.2/
- **💻 GitHub**: https://github.com/arkaigrowth/orchestrator_toolkit
- **📖 Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **🤝 Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE)

---

**Version 2.0.2** • Built for [Claude Code](https://claude.ai) • Powered by [Pydantic v2](https://pydantic.dev)

**Stop losing track. Start shipping.** 🚀
