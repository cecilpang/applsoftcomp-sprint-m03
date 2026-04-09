"""File utilities for trip planner."""

import shutil
from pathlib import Path
from typing import Optional


def copy_templates(templates_dir: Path, working_dir: Path):
    """Copy template files to working directory if they don't exist."""
    templates_dir = Path(templates_dir)
    working_dir = Path(working_dir)

    working_dir.mkdir(parents=True, exist_ok=True)

    template_files = [
        "preferences.md",
        "trip_draft.md",
        "trip_final.md",
        "progress.txt",
        "requirements.txt",
    ]

    for filename in template_files:
        src = templates_dir / filename
        dst = working_dir / filename

        if not dst.exists():
            if src.exists():
                shutil.copy2(src, dst)
            else:
                dst.touch()


def read_file(filepath: Path) -> str:
    """Read file contents."""
    filepath = Path(filepath)
    if not filepath.exists():
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def write_file(filepath: Path, content: str):
    """Write content to file."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def append_file(filepath: Path, content: str):
    """Append content to file."""
    filepath = Path(filepath)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content)


def file_exists(filepath: Path) -> bool:
    """Check if file exists."""
    return Path(filepath).exists()


def get_file_timestamp(filepath: Path) -> Optional[str]:
    """Get file modification timestamp."""
    filepath = Path(filepath)
    if filepath.exists():
        from datetime import datetime

        mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
        return mtime.strftime("%Y-%m-%d %H:%M")
    return None
