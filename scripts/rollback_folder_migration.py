#!/usr/bin/env python3
"""
Rollback migration from ai_docs to .ai_docs

This script reverses the folder migration if needed.
Generated: 2025-10-12
"""
from pathlib import Path
import shutil
import sys

def rollback():
    """Reverse the folder migration."""
    new_path = Path("ai_docs")
    old_path = Path(".ai_docs")
    backup_path = Path(".ai_docs.backup")

    print("🔄 Rolling back migration from ai_docs to .ai_docs...")

    # Check if backup exists
    if backup_path.exists():
        print(f"📦 Restoring from backup: {backup_path} → {old_path}")

        # Remove current ai_docs if it exists
        if new_path.exists():
            print(f"🗑️  Removing current ai_docs folder...")
            shutil.rmtree(new_path)

        # Restore from backup
        shutil.copytree(backup_path, old_path)
        print("✅ Restored from backup successfully")

        # Ask if user wants to remove backup
        response = input("\nRemove backup folder? (y/N): ").strip().lower()
        if response == 'y':
            shutil.rmtree(backup_path)
            print("🗑️  Backup removed")
        else:
            print(f"📦 Backup kept at: {backup_path}")

        return True

    # Or move folder back if no backup
    elif new_path.exists() and not old_path.exists():
        print(f"📁 Moving back: {new_path} → {old_path}")
        shutil.move(str(new_path), str(old_path))
        print("✅ Folder moved back successfully")
        return True

    else:
        print("⚠️  Cannot rollback - check paths manually")
        print(f"   ai_docs exists: {new_path.exists()}")
        print(f"   .ai_docs exists: {old_path.exists()}")
        print(f"   backup exists: {backup_path.exists()}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("📦 ROLLBACK MIGRATION: ai_docs → .ai_docs")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This will reverse the folder migration!")
    print("   This will restore the .ai_docs folder structure.")
    print()

    response = input("Are you sure you want to rollback? (yes/N): ").strip().lower()

    if response != 'yes':
        print("❌ Rollback cancelled")
        sys.exit(1)

    success = rollback()

    if success:
        print()
        print("=" * 60)
        print("✅ ROLLBACK COMPLETE")
        print("=" * 60)
        print()
        print("⚠️  Note: You may need to manually revert file references")
        print("   in scripts and documentation to use .ai_docs again.")
        sys.exit(0)
    else:
        print()
        print("❌ Rollback failed - manual intervention required")
        sys.exit(1)
