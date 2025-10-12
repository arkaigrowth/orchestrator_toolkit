#!/usr/bin/env python3
"""
Migrate .ai_docs to ai_docs for better IDE visibility.

This script safely migrates the hidden .ai_docs folder to ai_docs,
updates all references in the codebase, and creates a rollback script.
"""
from pathlib import Path
import shutil
import json
import sys
from typing import List, Dict, Any
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestrator_toolkit.models.migration import (
    FolderMigrationConfig,
    MigrationResult,
    FileReference,
    MigrationPlan
)


def create_backup(old_path: Path, backup_path: Path) -> bool:
    """Create backup of existing folder."""
    try:
        if old_path.exists():
            print(f"📦 Creating backup: {old_path} → {backup_path}")
            shutil.copytree(old_path, backup_path)
            print(f"✅ Backup created successfully")
            return True
        return False
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False


def move_folder(config: FolderMigrationConfig) -> MigrationResult:
    """Execute the folder migration."""
    result = MigrationResult()

    # Create backup first
    if config.backup_path:
        result.backup_created = create_backup(config.old_path, config.backup_path)
        result.backup_location = config.backup_path

    if config.dry_run:
        print(f"🔍 DRY RUN: Would move {config.old_path} → {config.new_path}")
        result.success = True
        return result

    try:
        # Move the folder
        print(f"📁 Moving folder: {config.old_path} → {config.new_path}")
        shutil.move(str(config.old_path), str(config.new_path))

        # Count files moved
        result.files_moved = sum(1 for _ in config.new_path.rglob("*") if _.is_file())
        result.success = True
        print(f"✅ Moved {result.files_moved} files successfully")

    except Exception as e:
        result.add_issue(f"Failed to move folder: {e}")
        print(f"❌ Migration failed: {e}")

    return result


def update_file_references(references: List[FileReference], dry_run: bool = True) -> int:
    """Update all file references from .ai_docs to ai_docs."""
    updated_count = 0

    for ref in references:
        try:
            # Read file content
            content = ref.file_path.read_text()

            # Replace pattern
            new_content = content.replace(ref.old_pattern, ref.new_pattern)

            if content != new_content:
                if dry_run:
                    print(f"🔍 Would update: {ref.file_path}")
                else:
                    ref.file_path.write_text(new_content)
                    print(f"✅ Updated: {ref.file_path}")
                updated_count += 1

        except Exception as e:
            print(f"❌ Failed to update {ref.file_path}: {e}")

    return updated_count


def generate_rollback_script(config: FolderMigrationConfig, result: MigrationResult) -> Path:
    """Generate a rollback script to reverse the migration."""
    rollback_script = Path("scripts/rollback_migration.py")

    rollback_code = f'''#!/usr/bin/env python3
"""
Rollback migration from ai_docs to .ai_docs

Generated: {datetime.utcnow().isoformat()}Z
"""
from pathlib import Path
import shutil

def rollback():
    """Reverse the folder migration."""
    new_path = Path("{config.new_path}")
    old_path = Path("{config.old_path}")
    backup_path = Path("{config.backup_path}") if "{config.backup_path}" != "None" else None

    print("🔄 Rolling back migration...")

    # Restore from backup if available
    if backup_path and backup_path.exists():
        print(f"📦 Restoring from backup: {{backup_path}} → {{old_path}}")
        if old_path.exists():
            shutil.rmtree(old_path)
        shutil.copytree(backup_path, old_path)
        print("✅ Restored from backup")

    # Or move folder back
    elif new_path.exists() and not old_path.exists():
        print(f"📁 Moving back: {{new_path}} → {{old_path}}")
        shutil.move(str(new_path), str(old_path))
        print("✅ Folder moved back")

    else:
        print("⚠️  Cannot rollback - check paths manually")
        return False

    # TODO: Reverse file reference updates
    print("⚠️  Note: File references need manual reversal or re-run original setup")
    return True

if __name__ == "__main__":
    success = rollback()
    exit(0 if success else 1)
'''

    rollback_script.write_text(rollback_code)
    rollback_script.chmod(0o755)  # Make executable
    print(f"📝 Rollback script created: {rollback_script}")

    return rollback_script


def build_migration_plan() -> MigrationPlan:
    """Build the complete migration plan."""
    config = FolderMigrationConfig(
        old_path=Path(".ai_docs"),
        new_path=Path("ai_docs"),
        backup_path=Path(".ai_docs.backup"),
        dry_run=True  # Start with dry run
    )

    plan = MigrationPlan(
        config=config,
        validation_steps=[
            "Verify no .ai_docs references remain (except in migration scripts)",
            "Run test suite to ensure functionality",
            "Test IDE autocomplete for ai_docs/tasks/T-",
            "Verify git status shows expected changes only"
        ],
        risk_level="medium",
        estimated_duration_minutes=60
    )

    # Add file references based on analysis
    # Python files
    plan.add_file_reference(FileReference(
        file_path=Path("src/orchestrator_toolkit/settings.py"),
        line_numbers=[16, 19, 20],
        old_pattern=".ai_docs",
        new_pattern="ai_docs",
        context="Settings default values - critical"
    ))

    # Shell scripts
    for script in ["setup.sh", "setup.bat", "test_installation.sh"]:
        if Path(script).exists():
            plan.add_file_reference(FileReference(
                file_path=Path(script),
                old_pattern=".ai_docs",
                new_pattern="ai_docs",
                context=f"Setup script: {script}"
            ))

    # Documentation
    for doc in ["README.md", "EXAMPLE_USAGE.md", "examples/workflow.md"]:
        if Path(doc).exists():
            plan.add_file_reference(FileReference(
                file_path=Path(doc),
                old_pattern=".ai_docs",
                new_pattern="ai_docs",
                context=f"Documentation: {doc}"
            ))

    # .gitignore
    plan.add_file_reference(FileReference(
        file_path=Path(".gitignore"),
        old_pattern=".ai_docs/",
        new_pattern="ai_docs/",
        context="Git ignore pattern"
    ))

    return plan


def main():
    """Main migration execution."""
    print("=" * 60)
    print("📦 FOLDER MIGRATION: .ai_docs → ai_docs")
    print("=" * 60)

    # Build migration plan
    plan = build_migration_plan()
    print(f"\n📋 Migration Plan:")
    print(f"   - Files to update: {len(plan.files_to_update)}")
    print(f"   - Total references: {plan.total_references}")
    print(f"   - Risk level: {plan.risk_level}")
    print(f"   - Estimated duration: {plan.estimated_duration_minutes} minutes")

    # Ask for confirmation
    print("\n⚠️  This is a DRY RUN by default")
    response = input("\nProceed with DRY RUN? (y/n): ").strip().lower()

    if response != 'y':
        print("❌ Migration cancelled")
        return

    # Execute dry run
    print("\n🔍 Starting DRY RUN...\n")

    # Simulate folder move
    result = move_folder(plan.config)

    # Simulate reference updates
    refs_updated = update_file_references(plan.files_to_update, dry_run=True)
    result.references_updated = refs_updated

    # Generate rollback script
    result.rollback_script = generate_rollback_script(plan.config, result)

    # Show results
    print("\n" + "=" * 60)
    print("📊 DRY RUN RESULTS")
    print("=" * 60)
    print(f"Files to move: {result.files_moved}")
    print(f"References to update: {result.references_updated}")
    print(f"Backup would be created: {result.backup_created}")
    print(f"Rollback script: {result.rollback_script}")

    # Ask if user wants to execute for real
    print("\n⚠️  DRY RUN COMPLETE")
    print("\nTo execute the actual migration:")
    print("1. Review the changes above")
    print("2. Commit any pending work")
    print("3. Re-run with: python scripts/migrate_docs_folder.py --execute")


if __name__ == "__main__":
    # Check for --execute flag
    if "--execute" in sys.argv:
        print("❌ --execute mode not yet implemented")
        print("Please review dry run results first")
        sys.exit(1)

    main()
