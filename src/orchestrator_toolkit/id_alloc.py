from pathlib import Path

def next_numeric(prefix: str, dir_: Path) -> str:
    """
    Scans dir_ for files named like 'T-0001.md' or 'P-0123.md'
    and returns the next zero-padded number as a 4-digit string.

    This avoids global counter files that can cause merge conflicts
    and instead derives the next ID from existing files in the directory.
    """
    hi = 0
    if dir_.is_dir():
        for p in dir_.glob(f"{prefix}-*.md"):
            try:
                # Extract the numeric part after the prefix
                num = int(p.stem.split("-")[1])
                hi = max(hi, num)
            except Exception:
                # Ignore files that don't match the expected pattern
                continue
    return f"{hi + 1:04d}"