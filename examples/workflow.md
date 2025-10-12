# 📋 Orchestrator Toolkit Workflow Examples

This guide demonstrates common workflows using the Orchestrator Toolkit.

## Basic Workflow: Task to Implementation

### 1. Create a Task

```bash
# Create a new task for implementing a feature
task-new "Add user profile page" --owner "Frontend Team"
# Output: ai_docs/tasks/T-0001.md
```

### 2. Review and Update Task Status

Edit `ai_docs/tasks/T-0001.md`:
- Change `status: new` to `status: assigned`
- Add specific notes and requirements

### 3. Generate Plan Automatically

```bash
# Run orchestrator to create plans for assigned tasks
orchestrator-once
# Output: created_plans=1
# Creates: ai_docs/plans/P-0001.md
```

### 4. Work on Implementation

- Open the plan file: `ai_docs/plans/P-0001.md`
- Follow the scaffolded steps
- Update plan with actual implementation details

### 5. Track Progress

Update task status as you work:
- `status: in-progress` - When starting work
- `status: blocked` - If encountering issues
- `status: done` - When complete

## Advanced Workflow: Project Management

### Scenario: Managing a Sprint

```bash
# Day 1: Sprint Planning
# Create tasks for sprint backlog
task-new "API endpoint for user search" --owner "Backend"
task-new "Search UI component" --owner "Frontend"
task-new "Search integration tests" --owner "QA"
task-new "Deploy search feature" --owner "DevOps"

# Assign tasks to developers
# Edit each task file and set status: assigned

# Generate implementation plans
orchestrator-once
# Output: created_plans=4
```

### Tracking Multiple Tasks

```bash
# Check all tasks status
ls -la ai_docs/tasks/

# Find assigned tasks
grep -l "status: assigned" ai_docs/tasks/*.md

# Find blocked tasks
grep -l "status: blocked" ai_docs/tasks/*.md
```

## Integration Workflow: With Claude Code

### 1. Initial Project Setup

```bash
# In your project repository
export OTK_ARTIFACT_ROOT=ai_docs

# Create initial project structure task
task-new "Setup project structure" --owner "You"
```

### 2. Claude Code Interaction

When working with Claude Code, you can:

1. **Ask Claude to create tasks directly:**
   ```
   "Claude, create a task for implementing OAuth2 integration"
   ```
   Claude will run: `task-new "Implement OAuth2 integration" --owner Dev`

2. **Request plan generation:**
   ```
   "Run the orchestrator to create plans for my assigned tasks"
   ```
   Claude will run: `orchestrator-once`

3. **Process existing markdown:**
   ```
   "Convert my notes.md file into a structured task"
   ```
   Claude can read your file and create appropriate tasks/plans

### 3. Collaborative Development

```bash
# Team member A creates task
task-new "Database schema design" --owner "DBA Team"

# Team member B creates related task
task-new "ORM model implementation" --owner "Backend Team"

# Link plans together
plan-new "Database implementation plan" --task T-0001
plan-new "ORM setup plan" --task T-0002
```

## Migration Workflow: From Legacy Structure

### Scenario: Existing Project with Old Structure

If you have existing `tasks/` and `plans/` directories:

```bash
# Before migration
ls -la
# Shows: tasks/ plans/ directories at root

# Install orchestrator toolkit
pip install -e .

# Run any command - migration happens automatically
task-new "Test migration" --owner test

# After migration
ls -la ai_docs/
# Shows: tasks/ plans/ with all files migrated
# Old directories are removed if empty
```

### Handling Conflicts

If files with same names exist in both old and new locations:

```
Original: tasks/T-0001.md
Existing: ai_docs/tasks/T-0001.md
Result:   ai_docs/tasks/T-0001-migrated-1.md
```

## Automation Workflow: CI/CD Integration

### GitHub Actions Example

```yaml
name: Task Management
on:
  push:
    branches: [main]

jobs:
  update-tasks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'

      - name: Install Orchestrator
        run: |
          pip install -e .
          export OTK_ARTIFACT_ROOT=ai_docs

      - name: Generate Plans
        run: orchestrator-once

      - name: Commit Updates
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add ai_docs/
          git commit -m "Auto-generate plans for assigned tasks" || true
          git push
```

## Reporting Workflow: Status Overview

### Generate Task Summary

```bash
# Count tasks by status
echo "Task Status Summary:"
echo "==================="
echo "New:         $(grep -l 'status: new' ai_docs/tasks/*.md 2>/dev/null | wc -l)"
echo "Assigned:    $(grep -l 'status: assigned' ai_docs/tasks/*.md 2>/dev/null | wc -l)"
echo "In Progress: $(grep -l 'status: in-progress' ai_docs/tasks/*.md 2>/dev/null | wc -l)"
echo "Blocked:     $(grep -l 'status: blocked' ai_docs/tasks/*.md 2>/dev/null | wc -l)"
echo "Done:        $(grep -l 'status: done' ai_docs/tasks/*.md 2>/dev/null | wc -l)"
```

### Find Tasks by Owner

```bash
# List all tasks for specific owner
grep -l 'owner: Backend Team' ai_docs/tasks/*.md

# Get task titles for owner
grep -h 'title:' $(grep -l 'owner: Frontend Team' ai_docs/tasks/*.md)
```

## Best Practices

### 1. Task Naming Conventions

- **Feature**: "Implement [feature name]"
- **Bug Fix**: "Fix [issue description]"
- **Refactor**: "Refactor [component/module]"
- **Documentation**: "Document [feature/API]"
- **Testing**: "Test [component/feature]"

### 2. Status Progression

```
new → assigned → in-progress → done
                      ↓
                   blocked → in-progress
```

### 3. Owner Assignment

- Use team names for team ownership
- Use individual names for specific assignments
- Use "Backlog" for unassigned items
- Use "External" for third-party dependencies

### 4. Plan Linking

Always link plans to tasks when relationship exists:
```bash
plan-new "Implementation details" --task T-0001
```

### 5. Regular Maintenance

- Run `orchestrator-once` daily or on sprint boundaries
- Review and update blocked tasks weekly
- Archive completed tasks monthly (move to `ai_docs/archive/`)

## Troubleshooting Common Issues

### Issue: Duplicate IDs

**Symptom**: Same ID appears twice
**Solution**: The system prevents this by scanning directories, but if it occurs:
```bash
# Check for duplicates
ls ai_docs/tasks/ | sort | uniq -d

# Renumber if needed (manually)
mv ai_docs/tasks/T-0001.md ai_docs/tasks/T-9999.md
```

### Issue: Lost Tasks After Migration

**Symptom**: Can't find old tasks
**Solution**: Check for -migrated suffix:
```bash
ls ai_docs/tasks/*-migrated-*.md
```

### Issue: Plans Not Generating

**Symptom**: orchestrator-once shows created_plans=0
**Solution**: Ensure tasks have `status: assigned`:
```bash
# Check task statuses
grep "status:" ai_docs/tasks/*.md
```

---

This workflow guide provides practical examples for using the Orchestrator Toolkit in real projects. For more details, see the main [README](../README.md).