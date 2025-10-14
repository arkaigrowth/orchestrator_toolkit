"""
Owner Resolution System

Resolves owner name through an enhanced cascade:
1. OTK_DEFAULT_OWNER environment variable
2. OTK_OWNER environment variable (alias)
3. git config user.name
4. GITHUB_ACTOR environment variable (CI fallback)
5. .otk/.owner persistent cache (per-repo)
6. Interactive prompt (cached to .otk/.owner)
7. Final fallback: "unknown"
"""
import os
import subprocess
from pathlib import Path
from typing import Optional, List

# Global owner cache for session persistence
_owner_cache: Optional[str] = None


def resolve_owner() -> str:
    """
    Resolve owner name through enhanced cascade with persistent caching.

    Cascade order (updated):
    1. Session cache (fast path)
    2. OTK_DEFAULT_OWNER env var
    3. OTK_OWNER env var (alias - more intuitive)
    4. git config user.name
    5. GITHUB_ACTOR env var (CI environments)
    6. .otk/.owner persistent cache (per-repo)
    7. Interactive prompt (cached to .otk/.owner)
    8. Fallback: "unknown"

    Returns:
        Owner name string
    """
    global _owner_cache

    # 0. Session cache (fast path)
    if _owner_cache:
        return _owner_cache

    # 1. OTK_DEFAULT_OWNER env var
    v = os.getenv('OTK_DEFAULT_OWNER')
    if v:
        _owner_cache = v
        return v

    # 2. OTK_OWNER env var (alias - more intuitive)
    v = os.getenv('OTK_OWNER')
    if v:
        _owner_cache = v
        return v

    # 3. .otk/.owner persistent cache (per-repo) - moved before git
    cache_file = Path.cwd() / ".otk" / ".owner"
    if cache_file.exists():
        try:
            v = cache_file.read_text(encoding='utf-8').strip()
            if v:
                _owner_cache = v
                return v
        except Exception:
            pass

    # 4. git config user.name
    try:
        v = subprocess.check_output(
            ['git', 'config', 'user.name'],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()
        if v:
            _owner_cache = v
            return v
    except Exception:
        pass

    # 5. GITHUB_ACTOR env var (CI environments)
    v = os.getenv('GITHUB_ACTOR')
    if v:
        _owner_cache = v
        return v


    # 6. Interactive prompt (write to persistent cache)
    try:
        # Use click if available (most CLI contexts)
        from click import prompt
        v = prompt("Owner name (for task tracking)", default="unknown")
    except Exception:
        # Fallback to basic input if click not available
        try:
            v = input("Owner name (for task tracking) [unknown]: ").strip() or "unknown"
        except Exception:
            v = "unknown"

    # Cache persistently if not "unknown"
    if v and v != "unknown":
        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_file.write_text(v, encoding='utf-8')
        except Exception:
            pass  # Silent failure on cache write

    _owner_cache = v
    return v


def pick_plan_interactively() -> Optional[str]:
    """
    List existing plans and let user choose one interactively.

    Returns:
        Selected plan ID (e.g., "PLAN-20251013-01T6N8") or None if cancelled
    """
    from .settings import OrchSettings

    s = OrchSettings.load()
    plans_dir = s.plans_dir

    if not plans_dir.exists():
        print("No plans directory found.")
        return None

    # Find all plan files (both new PLAN-* and legacy P-* formats)
    plan_files = sorted(
        list(plans_dir.glob("PLAN-*.md")) + list(plans_dir.glob("P-*.md"))
    )

    if not plan_files:
        print("No plans found.")
        return None

    print("\n📋 Available Plans:")
    print("-" * 60)

    # Display plans with numbering
    for idx, plan_file in enumerate(plan_files, start=1):
        plan_id = plan_file.stem
        # Try to extract title from frontmatter
        try:
            content = plan_file.read_text(encoding='utf-8')
            title = _extract_title_from_frontmatter(content)
        except Exception:
            title = "Untitled"

        print(f"{idx}. {plan_id:<30} | {title}")

    print("-" * 60)

    # Prompt for selection
    try:
        choice = input("\nSelect plan number (or 'q' to cancel): ").strip()
        if choice.lower() == 'q':
            return None

        idx = int(choice)
        if 1 <= idx <= len(plan_files):
            return plan_files[idx - 1].stem
        else:
            print(f"Invalid selection: {choice}")
            return None
    except (ValueError, KeyboardInterrupt):
        return None


def pick_spec_interactively() -> Optional[str]:
    """
    List existing specs and let user choose one interactively.

    Returns:
        Selected spec ID (e.g., "SPEC-20251013-02NZ6Q") or None if cancelled
    """
    from .settings import OrchSettings

    s = OrchSettings.load()
    specs_dir = Path("ai_docs/specs")

    if not specs_dir.exists():
        print("No specs directory found.")
        return None

    # Find all spec files
    spec_files = sorted(specs_dir.glob("SPEC-*.md"))

    if not spec_files:
        print("No specs found.")
        return None

    print("\n📐 Available Specs:")
    print("-" * 60)

    # Display specs with numbering
    for idx, spec_file in enumerate(spec_files, start=1):
        spec_id = spec_file.stem
        # Try to extract title from frontmatter
        try:
            content = spec_file.read_text(encoding='utf-8')
            title = _extract_title_from_frontmatter(content)
        except Exception:
            title = "Untitled"

        print(f"{idx}. {spec_id:<30} | {title}")

    print("-" * 60)

    # Prompt for selection
    try:
        choice = input("\nSelect spec number (or 'q' to cancel): ").strip()
        if choice.lower() == 'q':
            return None

        idx = int(choice)
        if 1 <= idx <= len(spec_files):
            return spec_files[idx - 1].stem
        else:
            print(f"Invalid selection: {choice}")
            return None
    except (ValueError, KeyboardInterrupt):
        return None


def _extract_title_from_frontmatter(content: str) -> str:
    """
    Extract title from YAML frontmatter.

    Args:
        content: File content with YAML frontmatter

    Returns:
        Title string or "Untitled"
    """
    lines = content.split('\n')
    in_frontmatter = False
    title = "Untitled"

    for line in lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break  # End of frontmatter

        if in_frontmatter and line.startswith('title:'):
            title = line.split(':', 1)[1].strip()
            break

    return title


def clear_owner_cache():
    """
    Clear the owner cache (useful for testing).
    """
    global _owner_cache
    _owner_cache = None
