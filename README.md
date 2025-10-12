# 🎯 Orchestrator Toolkit

[![PyPI Test](https://img.shields.io/badge/PyPI%20Test-v1.0.0-orange)](https://test.pypi.org/project/orchestrator-toolkit/)
[![Python Version](https://img.shields.io/badge/python-≥3.10-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A lightweight task orchestration system for managing project workflows with Claude Code. Built with modern Python patterns and Pydantic v2.

## 🚀 Quick Start (PyPI Test)

```bash
# Install from PyPI Test
pip install --index-url https://test.pypi.org/simple/ orchestrator-toolkit

# Set up environment
export OTK_ARTIFACT_ROOT=.ai_docs

# Create your first task
otk-task-new "Build awesome feature" --owner You

# Create a plan
otk-plan-new "Implementation roadmap"

# Run orchestrator
orchestrator-once
```

That's it! Your tasks and plans are now in `.ai_docs/`.

## ✨ Features

- **📁 Centralized Artifacts**: All tasks/plans in `.ai_docs/` directory
- **🆔 Smart ID Generation**: Directory-based IDs prevent merge conflicts
- **🎨 Auto Templates**: Creates templates on first use
- **💻 Cross-Platform**: Windows, macOS, and Linux support
- **🚀 Zero Config**: Works out of the box with sensible defaults
- **🔌 Optional Integrations**: Archon and Mem0 adapters available

## 📦 Installation Options

### From PyPI Test (Recommended)

```bash
# Install latest version
pip install --index-url https://test.pypi.org/simple/ orchestrator-toolkit

# Or install with extra index for dependencies
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            orchestrator-toolkit
```

### From Source

```bash
# Clone repository
git clone https://github.com/arkaigrowth/orchestrator_toolkit_1.0.git
cd orchestrator_toolkit_1.0

# Install in development mode
pip install -e .
```

### Using Setup Script

```bash
# Unix/macOS
chmod +x setup.sh
./setup.sh

# Windows
setup.bat
```

## 📖 Usage

### Core Commands

| Command | Description |
|---------|-------------|
| `otk-task-new "title" --owner name` | Create a new task |
| `otk-plan-new "title" --task T-0001` | Create a new plan |
| `orchestrator-once` | Generate plans for assigned tasks |

### Task Management Workflow

1. **Create Task**
   ```bash
   otk-task-new "Implement user authentication" --owner Backend
   # Creates: .ai_docs/tasks/T-0001.md
   ```

2. **Create Plan** (optional)
   ```bash
   otk-plan-new "Auth implementation details" --task T-0001
   # Creates: .ai_docs/plans/P-0001.md
   ```

3. **Auto-generate Plans**
   ```bash
   # For tasks with status: assigned
   orchestrator-once
   ```

### Task Format

Tasks are markdown files with YAML frontmatter:

```markdown
---
id: T-0001
title: Implement user authentication
owner: Backend
status: assigned   # (new|assigned|in-progress|blocked|done)
created: 2024-10-12T07:08:09Z
---

## Goal
Implement user authentication

## Notes
- Requirements and constraints here
```

### Environment Configuration

```bash
# Set artifact directory (default: .ai_docs)
export OTK_ARTIFACT_ROOT=.ai_docs

# Optional: Enable Archon integration
export OTK_ARCHON_ENABLED=1
export OTK_ARCHON_BASE_URL=http://localhost:8787
export OTK_ARCHON_API_KEY=your-key

# Optional: Enable Mem0 integration
export OTK_MEM0_ENABLED=1
export OTK_MEM0_API_URL=https://api.mem0.ai/v1
export OTK_MEM0_API_KEY=your-key
```

## 🏗️ Architecture

```
your-project/
├── .ai_docs/               # All artifacts (gitignored)
│   ├── tasks/             # Task files (T-XXXX.md)
│   └── plans/             # Plan files (P-XXXX.md)
├── .claude/               # Claude-specific config
│   └── templates/         # Task/plan templates
└── src/                   # Your project code
```

### Key Design Principles

1. **Directory-Based IDs**: Scans directory for next ID (no counter files)
2. **Single Source of Truth**: All settings via `OrchSettings.load()`
3. **Template Auto-Creation**: Missing templates created automatically
4. **Cross-Platform**: Pure Python implementation

## 🔧 Advanced Usage

### Custom Templates

Edit templates in `.claude/templates/`:
- `task.md` - Task format
- `plan.md` - Plan format

Variables: `${ID}`, `${TITLE}`, `${OWNER}`, `${DATE}`, `${TASK_ID}`

### Programmatic Usage

```python
from orchestrator_toolkit.scripts.task_new import create_task
from orchestrator_toolkit.settings import OrchSettings

# Create task programmatically
task_path = create_task("My Task", owner="Me")
print(f"Created: {task_path}")

# Access settings
settings = OrchSettings.load()
print(f"Tasks in: {settings.tasks_dir}")
```

### Integration with Claude Code

When using with Claude Code:
1. Claude can run commands directly
2. Ask: "Create a task for implementing OAuth"
3. Claude executes: `otk-task-new "Implement OAuth" --owner Dev`

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install orchestrator-toolkit` |
| Tasks not in `.ai_docs/` | Set `export OTK_ARTIFACT_ROOT=.ai_docs` |
| `pydantic_settings not found` | Run `pip install pydantic-settings>=2.3` |
| Permission denied | Unix/macOS: `chmod +x setup.sh` |

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Built for [Claude Code](https://claude.ai)
- Powered by [Pydantic v2](https://pydantic.dev)
- Inspired by simple, effective tools

---

**Version**: 1.0.0
**PyPI Test**: https://test.pypi.org/project/orchestrator-toolkit/
**Repository**: https://github.com/arkaigrowth/orchestrator_toolkit_1.0