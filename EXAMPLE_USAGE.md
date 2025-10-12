# 🚀 Using Orchestrator Toolkit in Your Project

This guide shows how to integrate orchestrator-toolkit into your existing project.

## Quick Integration (5 minutes)

### 1. Install the Package

```bash
# From PyPI Test
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            orchestrator-toolkit

# Or add to requirements.txt:
--index-url https://test.pypi.org/simple/
--extra-index-url https://pypi.org/simple/
orchestrator-toolkit>=1.0.0
```

### 2. Initialize in Your Project

```bash
cd your-project/

# Set the artifact directory (defaults to ai_docs)
export OTK_ARTIFACT_ROOT=ai_docs

# Create your first task
task-new "Implement user authentication" --owner Backend

# View the created task
cat ai_docs/tasks/T-0001.md
```

### 3. Add to .gitignore

```bash
echo "ai_docs/" >> .gitignore
```

## Real-World Example: Web Application

Let's say you're building a web application and want to track development tasks:

```bash
# Create tasks for your sprint
task-new "Design database schema" --owner Backend
task-new "Create REST API endpoints" --owner Backend
task-new "Build React components" --owner Frontend
task-new "Write unit tests" --owner QA

# Generate implementation plans
orchestrator-once

# View generated plans
ls ai_docs/plans/
```

## Integration with Claude Code

When working with Claude Code, you can ask it to:

1. **Create tasks directly**:
   ```
   You: "Create a task for implementing OAuth2 authentication"
   Claude: *runs* task-new "Implement OAuth2 authentication" --owner Backend
   ```

2. **Generate plans**:
   ```
   You: "Create a detailed plan for the authentication task"
   Claude: *runs* plan-new "OAuth2 implementation plan" --task T-0001
   ```

3. **Track progress**:
   ```
   You: "Update task T-0001 to in-progress"
   Claude: *edits* ai_docs/tasks/T-0001.md
   ```

## Project Structure Example

After integration, your project might look like:

```
your-project/
├── ai_docs/               # Task management (gitignored)
│   ├── tasks/
│   │   ├── T-0001.md      # Database schema task
│   │   ├── T-0002.md      # API endpoints task
│   │   └── T-0003.md      # React components task
│   └── plans/
│       ├── P-0001.md      # Database implementation plan
│       └── P-0002.md      # API design plan
├── src/                    # Your source code
│   ├── backend/
│   ├── frontend/
│   └── tests/
├── .gitignore             # Includes ai_docs/
├── requirements.txt       # Includes orchestrator-toolkit
└── README.md
```

## Advanced Usage: Python Integration

You can also use the toolkit programmatically:

```python
# my_project/task_manager.py
from orchestrator_toolkit.scripts.task_new import create_task
from orchestrator_toolkit.settings import OrchSettings
import os

def create_feature_task(feature_name: str):
    """Create a task for a new feature."""
    # Ensure we're using the right directory
    os.environ['OTK_ARTIFACT_ROOT'] = 'ai_docs'

    # Create the task
    task_path = create_task(
        title=f"Implement {feature_name}",
        owner="Development Team"
    )

    print(f"Created task: {task_path}")
    return task_path

def list_all_tasks():
    """List all tasks in the project."""
    settings = OrchSettings.load()
    tasks_dir = settings.tasks_dir

    if tasks_dir.exists():
        tasks = sorted(tasks_dir.glob("T-*.md"))
        for task in tasks:
            print(f"- {task.name}")
    else:
        print("No tasks found")

# Usage
if __name__ == "__main__":
    create_feature_task("user profiles")
    list_all_tasks()
```

## CI/CD Integration

You can integrate task tracking into your CI/CD pipeline:

```yaml
# .github/workflows/task-check.yml
name: Task Status Check

on: [pull_request]

jobs:
  check-tasks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install orchestrator-toolkit
        run: |
          pip install --index-url https://test.pypi.org/simple/ \
                      --extra-index-url https://pypi.org/simple/ \
                      orchestrator-toolkit

      - name: Check for incomplete tasks
        run: |
          # Custom script to check task statuses
          python check_tasks.py
```

## Tips & Best Practices

1. **Keep tasks atomic**: One deliverable per task
2. **Use meaningful owners**: Team names or roles, not individual names
3. **Regular status updates**: Update task status as work progresses
4. **Link related items**: Reference task IDs in commit messages
5. **Archive completed sprints**: Move old tasks to an archive directory

## Troubleshooting

### Issue: Commands not found
```bash
# Ensure package is installed
pip list | grep orchestrator-toolkit

# Reinstall if needed
pip install --upgrade --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            orchestrator-toolkit
```

### Issue: Tasks not appearing in ai_docs
```bash
# Check environment variable
echo $OTK_ARTIFACT_ROOT

# Set it explicitly
export OTK_ARTIFACT_ROOT=ai_docs
```

### Issue: Permission denied
```bash
# Ensure directory is writable
chmod -R u+w ai_docs/
```

## Support

- **Documentation**: https://github.com/arkaigrowth/orchestrator_toolkit_1.0
- **Issues**: https://github.com/arkaigrowth/orchestrator_toolkit_1.0/issues
- **PyPI Test**: https://test.pypi.org/project/orchestrator-toolkit/

---

Happy orchestrating! 🎯