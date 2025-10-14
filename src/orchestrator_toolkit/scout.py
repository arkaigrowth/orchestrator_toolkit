"""
Scout Command - Generate implementation checklists from SPECs.

Analyzes a SPEC file and produces an actionable checklist for implementation,
including file creation/modification tasks, test requirements, and documentation needs.
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .settings import OrchSettings


def parse_spec(spec_path: Path) -> Dict[str, str]:
    """
    Parse a SPEC file and extract key sections.

    Args:
        spec_path: Path to SPEC file

    Returns:
        Dictionary with spec metadata and content sections
    """
    content = spec_path.read_text(encoding="utf-8")

    # Extract frontmatter
    frontmatter_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return {}

    frontmatter = frontmatter_match.group(1)
    spec_data = {}

    # Parse frontmatter fields
    for line in frontmatter.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            spec_data[key.strip()] = value.strip().strip('"')

    # Extract key sections
    sections = {
        'objective': r'## Objective\s*\n(.*?)(?=\n##|\Z)',
        'approach': r'## Approach\s*\n(.*?)(?=\n##|\Z)',
        'technical_design': r'### Technical Design\s*\n(.*?)(?=\n###|\n##|\Z)',
        'implementation_steps': r'### Implementation Steps\s*\n(.*?)(?=\n###|\n##|\Z)',
        'acceptance_criteria': r'## Acceptance Criteria\s*\n(.*?)(?=\n##|\Z)',
        'risk_assessment': r'## Risk Assessment\s*\n(.*?)(?=\n##|\Z)',
    }

    for name, pattern in sections.items():
        match = re.search(pattern, content, re.DOTALL)
        if match:
            spec_data[name] = match.group(1).strip()

    return spec_data


def analyze_spec_for_tasks(spec_data: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Analyze SPEC content to generate implementation tasks.

    Args:
        spec_data: Parsed SPEC data

    Returns:
        List of tasks with type, description, and priority
    """
    tasks = []

    # Extract tasks from implementation steps
    if 'implementation_steps' in spec_data:
        steps = spec_data['implementation_steps']
        # Find checkbox items
        for match in re.finditer(r'^\d*\.?\s*\[[ x]\]\s*(.+)$', steps, re.MULTILINE):
            task_text = match.group(1)

            # Categorize task
            task_type = 'implementation'
            if any(word in task_text.lower() for word in ['test', 'verify', 'validate']):
                task_type = 'testing'
            elif any(word in task_text.lower() for word in ['document', 'readme', 'comment']):
                task_type = 'documentation'
            elif any(word in task_text.lower() for word in ['create', 'add', 'implement', 'build']):
                task_type = 'development'

            tasks.append({
                'type': task_type,
                'description': task_text,
                'source': 'implementation_steps'
            })

    # Extract from acceptance criteria
    if 'acceptance_criteria' in spec_data:
        criteria = spec_data['acceptance_criteria']
        for match in re.finditer(r'^-?\s*\[[ x]\]\s*(.+)$', criteria, re.MULTILINE):
            criterion = match.group(1)
            tasks.append({
                'type': 'validation',
                'description': f"Ensure: {criterion}",
                'source': 'acceptance_criteria'
            })

    # Infer tasks from technical design
    if 'technical_design' in spec_data:
        design = spec_data['technical_design'].lower()

        # Look for technology mentions
        if 'api' in design or 'endpoint' in design:
            tasks.append({
                'type': 'development',
                'description': 'Implement API endpoints',
                'source': 'inferred_from_design'
            })

        if 'database' in design or 'schema' in design or 'migration' in design:
            tasks.append({
                'type': 'development',
                'description': 'Create database schema/migrations',
                'source': 'inferred_from_design'
            })

        if 'frontend' in design or 'ui' in design or 'component' in design:
            tasks.append({
                'type': 'development',
                'description': 'Build frontend components',
                'source': 'inferred_from_design'
            })

        if 'test' in design:
            tasks.append({
                'type': 'testing',
                'description': 'Write comprehensive tests',
                'source': 'inferred_from_design'
            })

    # Add standard tasks if not already present
    has_tests = any(t['type'] == 'testing' for t in tasks)
    has_docs = any(t['type'] == 'documentation' for t in tasks)

    if not has_tests:
        tasks.append({
            'type': 'testing',
            'description': 'Write unit tests for new functionality',
            'source': 'standard_requirement'
        })

    if not has_docs:
        tasks.append({
            'type': 'documentation',
            'description': 'Update documentation with new features',
            'source': 'standard_requirement'
        })

    return tasks


def generate_checklist(spec_id: str, tasks: List[Dict[str, str]]) -> str:
    """
    Generate a markdown checklist from tasks.

    Args:
        spec_id: SPEC identifier
        tasks: List of tasks

    Returns:
        Markdown formatted checklist
    """
    now = datetime.now().isoformat(timespec='seconds')

    checklist = f"""# Scout Report: {spec_id}

Generated: {now}

## Implementation Checklist

"""

    # Group tasks by type
    task_groups = {}
    for task in tasks:
        task_type = task['type']
        if task_type not in task_groups:
            task_groups[task_type] = []
        task_groups[task_type].append(task)

    # Output by group
    group_order = ['development', 'implementation', 'testing', 'validation', 'documentation']
    group_icons = {
        'development': '🔨',
        'implementation': '⚙️',
        'testing': '🧪',
        'validation': '✅',
        'documentation': '📚'
    }

    for group in group_order:
        if group in task_groups:
            icon = group_icons.get(group, '📋')
            checklist += f"### {icon} {group.title()}\n\n"

            for task in task_groups[group]:
                checklist += f"- [ ] {task['description']}\n"
                if task['source'] != 'standard_requirement':
                    checklist += f"      *(from: {task['source']})*\n"

            checklist += "\n"

    # Add execution guidance
    checklist += """## Execution Guidance

1. Review all tasks and adjust based on actual requirements
2. Start with development/implementation tasks
3. Write tests as you implement features
4. Validate against acceptance criteria
5. Update documentation before marking complete

## Notes

This checklist was auto-generated from the SPEC.
Modify as needed based on actual implementation requirements.
"""

    return checklist


def scout_spec(spec_id: str) -> int:
    """
    Scout a SPEC and generate implementation checklist.

    Args:
        spec_id: SPEC identifier (partial or full)

    Returns:
        Exit code (0 = success)
    """
    s = OrchSettings.load()

    # Find the SPEC file
    spec_files = list(s.specs_dir.glob(f"{spec_id}*.md"))
    if not spec_files:
        print(f"❌ SPEC not found: {spec_id}")
        return 1

    if len(spec_files) > 1:
        print(f"⚠️  Multiple SPECs found matching '{spec_id}':")
        for f in spec_files:
            print(f"   - {f.name}")
        print("\nPlease be more specific.")
        return 1

    spec_path = spec_files[0]
    print(f"🔍 Scouting: {spec_path.name}")

    # Parse the SPEC
    spec_data = parse_spec(spec_path)
    if not spec_data:
        print("❌ Failed to parse SPEC file")
        return 1

    # Analyze for tasks
    tasks = analyze_spec_for_tasks(spec_data)
    print(f"   Found {len(tasks)} implementation tasks")

    # Generate checklist
    checklist = generate_checklist(spec_path.stem, tasks)

    # Save checklist
    scout_dir = s.artifact_root / "scout_reports"
    scout_dir.mkdir(parents=True, exist_ok=True)

    report_path = scout_dir / f"{spec_path.stem}-scout.md"
    report_path.write_text(checklist, encoding="utf-8")

    print(f"✅ Scout report saved: {report_path}")
    print(f"\n📋 Summary:")

    # Show task summary
    task_counts = {}
    for task in tasks:
        task_type = task['type']
        task_counts[task_type] = task_counts.get(task_type, 0) + 1

    for task_type, count in sorted(task_counts.items()):
        print(f"   - {task_type.title()}: {count} tasks")

    print(f"\n💡 Next: Review {report_path.name} and start implementation")

    return 0


def main():
    """CLI entry point for scout command."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: otk scout <SPEC-ID>")
        print("\nExample:")
        print("  otk scout SPEC-20251013-02NZ6Q")
        return 1

    spec_id = sys.argv[1]
    return scout_spec(spec_id)


if __name__ == "__main__":
    raise SystemExit(main())