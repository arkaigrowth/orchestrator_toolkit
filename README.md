# 🎯 Orchestrator Toolkit v1.0

[![Python Version](https://img.shields.io/badge/python-≥3.10-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A lightweight, production-ready task orchestration system for managing project workflows with Claude Code. Built with modern Python patterns and zero external dependencies beyond Pydantic.

## ✨ Features

- **📁 Centralized Artifact Management**: All tasks and plans stored in `.ai_docs/` directory
- **🔄 Automatic Legacy Migration**: Seamlessly migrates existing `tasks/` and `plans/` directories
- **🆔 Conflict-Free ID Generation**: Directory-based ID allocation prevents merge conflicts
- **🛡️ Collision-Safe Migration**: Smart handling of duplicate files during migration
- **🎨 Template Auto-Creation**: Automatically generates templates on first use
- **🔌 Optional Integrations**: Archon and Mem0 adapters for extended functionality
- **💻 Cross-Platform**: Works on Windows, macOS, and Linux
- **🚀 Zero Configuration**: Sensible defaults with environment variable overrides

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/arkaigrowth/orchestrator_toolkit_1.0.git
cd orchestrator_toolkit_1.0

# Install in development mode (creates .ai_docs/ automatically)
pip install -e .

# Create your first task
task-new "Implement user authentication" --owner Alex

# Create a plan
plan-new "Authentication implementation plan" --task T-0001

# Run orchestrator to scaffold plans for assigned tasks
orchestrator-once
```

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- git (for cloning)

### Method 1: Using Virtual Environment (Recommended)

```bash
# Create and activate virtual environment
python -m venv .otk-venv

# On macOS/Linux:
source .otk-venv/bin/activate

# On Windows:
.otk-venv\Scripts\activate

# Install the package
pip install -e .
```

### Method 2: Using the Setup Script

#### Unix/macOS:
```bash
chmod +x setup.sh
./setup.sh
```

#### Windows:
```cmd
setup.bat
```

### Method 3: Direct Installation

```bash
# Install dependencies
pip install pydantic-settings>=2.3,<3

# Install package
pip install -e .
```

## 📖 Usage Guide

### Creating Tasks

Tasks are the fundamental unit of work tracking:

```bash
# Basic task creation
task-new "Implement login feature" --owner Dev

# Task with specific owner
task-new "Write API documentation" --owner "Sarah Chen"

# Using the otk- prefix (alternative)
otk-task-new "Deploy to production" --owner DevOps
```

Tasks are created in `.ai_docs/tasks/T-XXXX.md` with this structure:

```markdown
---
id: T-0001
title: Implement login feature
owner: Dev
status: assigned   # (new|assigned|in-progress|blocked|done)
created: 2024-10-12T07:08:09Z
---

## Goal
Implement login feature

## Notes
- Add constraints/notes here.
```

### Creating Plans

Plans provide structured implementation details for tasks:

```bash
# Create standalone plan
plan-new "Technical architecture design"

# Create plan linked to a task
plan-new "Login implementation plan" --task T-0001

# With specific owner
plan-new "Database migration strategy" --owner DBA --task T-0002
```

Plans are created in `.ai_docs/plans/P-XXXX.md`.

### Running the Orchestrator

The orchestrator automatically creates plans for tasks with `status: assigned`:

```bash
# Run once (process all assigned tasks)
orchestrator-once

# Output: created_plans=2
```

### Environment Configuration

Configure behavior using environment variables:

```bash
# Set artifact root directory (default: .ai_docs)
export OTK_ARTIFACT_ROOT=.ai_docs

# Optional: Enable Archon integration
export OTK_ARCHON_ENABLED=1
export OTK_ARCHON_BASE_URL=http://localhost:8787
export OTK_ARCHON_API_KEY=sk-local-archon-xyz

# Optional: Enable Mem0 integration
export OTK_MEM0_ENABLED=1
export OTK_MEM0_API_URL=https://api.mem0.ai/v1
export OTK_MEM0_API_KEY=sk-mem0-xyz
```

For persistent configuration, use `direnv`:

```bash
# Create .envrc file
cat > .envrc << EOF
source .otk-venv/bin/activate
export OTK_ARTIFACT_ROOT=.ai_docs
EOF

# Allow direnv to load it
direnv allow
```

## 🏗️ Architecture

### Directory Structure

```
orchestrator_toolkit_1.0/
├── .ai_docs/                    # All artifacts (gitignored)
│   ├── tasks/                   # Task files (T-XXXX.md)
│   └── plans/                   # Plan files (P-XXXX.md)
├── .claude/                     # Claude-specific configuration
│   ├── templates/               # Task/plan templates
│   │   ├── task.md
│   │   └── plan.md
│   ├── commands/                # Legacy shell scripts
│   └── CLAUDE.md               # Claude handoff instructions
├── src/orchestrator_toolkit/    # Python package
│   ├── settings.py             # Pydantic v2 settings
│   ├── utils.py                # Helper functions
│   ├── id_alloc.py            # Directory-based ID generation
│   ├── orchestrator.py        # Core orchestration logic
│   ├── archon_adapter.py     # Optional Archon integration
│   ├── mem0_wrapper.py       # Optional Mem0 integration
│   ├── cli.py                # CLI entry points
│   └── scripts/               # Python-based commands
│       ├── task_new.py
│       └── plan_new.py
├── examples/                   # Example files
├── pyproject.toml             # Package configuration
├── requirements.txt           # Pip dependencies
└── README.md                  # This file
```

### Key Design Decisions

1. **Pydantic v2 Settings**: Uses `SettingsConfigDict` for robust environment handling
2. **Directory-Based IDs**: Scans existing files to determine next ID (no counter files)
3. **Collision-Safe Migration**: Appends `-migrated-N` suffix to prevent overwrites
4. **Single Load Pattern**: All settings use `OrchSettings.load()` for consistency
5. **Python-First**: Shell scripts replaced with Python for cross-platform compatibility

## 🔧 Advanced Configuration

### Custom Templates

Templates are auto-created on first use, but you can customize them:

1. Edit `.claude/templates/task.md` for task format
2. Edit `.claude/templates/plan.md` for plan format

Use `${VARIABLE}` placeholders:
- `${ID}` - Task/Plan ID
- `${TITLE}` - Title
- `${OWNER}` - Owner name
- `${DATE}` - ISO timestamp
- `${TASK_ID}` - Associated task (plans only)

### Migration Behavior

When you first run any command, the toolkit:
1. Checks for legacy `tasks/` and `plans/` directories
2. Migrates all `.md` files to `.ai_docs/`
3. Handles naming conflicts with `-migrated-N` suffix
4. Removes empty legacy directories

This is automatic and safe - no data is ever lost.

### ID Generation Strategy

IDs are generated by scanning the directory:
- Tasks: `T-0001`, `T-0002`, etc.
- Plans: `P-0001`, `P-0002`, etc.

The system finds the highest existing ID and increments by 1. This approach:
- ✅ Prevents merge conflicts
- ✅ Works across branches
- ✅ No shared state files
- ✅ Thread-safe for reasonable use

## 🐛 Troubleshooting

### Common Issues

**Issue: "No module named 'orchestrator_toolkit'"**
```bash
# Solution: Install package in development mode
pip install -e .
```

**Issue: "Permission denied" on Unix/macOS**
```bash
# Solution: Make scripts executable
chmod +x setup.sh
```

**Issue: Tasks not created in .ai_docs/**
```bash
# Solution: Set environment variable
export OTK_ARTIFACT_ROOT=.ai_docs
```

**Issue: "pydantic_settings not found"**
```bash
# Solution: Install dependencies
pip install pydantic-settings>=2.3,<3
```

### Verifying Installation

Run these commands to verify everything works:

```bash
# Check Python version
python --version  # Should be 3.10+

# Test task creation
task-new "Test task" --owner test
ls .ai_docs/tasks/  # Should show T-0001.md

# Test plan creation
plan-new "Test plan"
ls .ai_docs/plans/  # Should show P-0001.md

# Test orchestrator
orchestrator-once  # Should show created_plans=0 or higher
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/arkaigrowth/orchestrator_toolkit_1.0.git
cd orchestrator_toolkit_1.0

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in development mode
pip install -e .

# Run tests (when available)
python -m pytest tests/
```

### Reporting Issues

Please report issues on [GitHub Issues](https://github.com/arkaigrowth/orchestrator_toolkit_1.0/issues) with:
- Python version
- Operating system
- Error messages
- Steps to reproduce

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for use with [Claude Code](https://claude.ai)
- Inspired by modern Python patterns and Pydantic v2
- Designed for real-world project management needs

## 📚 Additional Resources

- [API Documentation](docs/api.md) (coming soon)
- [Architecture Deep Dive](docs/architecture.md) (coming soon)
- [Integration Guide](docs/integrations.md) (coming soon)

---

**Version**: 1.0.0
**Maintained by**: Arkai Growth
**Last Updated**: October 2024