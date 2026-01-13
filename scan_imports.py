# scan_imports.py
# Run from project root: python scan_imports.py
# Finds files with old-style imports: from mcp_db_analyst_assignment.xxx

import os
import re
from pathlib import Path

# ────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────

# Use the folder where THIS SCRIPT lives as project root
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR
SRC_DIR = PROJECT_ROOT / "src"

if not SRC_DIR.is_dir():
    print(f"Error: src/ folder not found at {SRC_DIR}")
    print("Make sure you run this script from the project root (where pyproject.toml is)")
    exit(1)

# Patterns to detect old/incorrect imports
OLD_IMPORT_PATTERNS = [
    r"^\s*from\s+mcp_db_analyst_assignment\s*\.",     # from mcp_db_analyst_assignment.xxx
    r"^\s*from\s+mcp_db_analyst_assignment\s+import", # from mcp_db_analyst_assignment import xxx
    r"^\s*import\s+mcp_db_analyst_assignment\.",      # import mcp_db_analyst_assignment.xxx
]

# Folders/files to skip
SKIP_DIRS = {
    "__pycache__", ".pytest_cache", ".git", "venv", ".idea", ".vscode",
    "node_modules", "dist", "build", "eggs", "parts", ".eggs"
}
SKIP_EXTENSIONS = {".pyc", ".pyo", ".pyd", ".egg-info", ".log", ".json", ".yaml"}

def should_skip(path: Path) -> bool:
    if path.name in SKIP_DIRS:
        return True
    if path.suffix in SKIP_EXTENSIONS:
        return True
    return False

def scan_file(file_path: Path) -> list[tuple[int, str]]:
    bad_lines = []
    try:
        content = file_path.read_text(encoding="utf-8")
        for i, line in enumerate(content.splitlines(), 1):
            if any(re.search(pat, line) for pat in OLD_IMPORT_PATTERNS):
                bad_lines.append((i, line.rstrip()))
    except Exception as e:
        print(f"  Skipping {file_path.name} – {e}")
    return bad_lines

def main():
    print("Scanning for old imports (mcp_db_analyst_assignment.) inside src/")
    print(f"  Project root: {PROJECT_ROOT}")
    print(f"  Scanning: {SRC_DIR}\n")

    found_files = 0
    total_files_checked = 0

    for root, dirs, files in os.walk(SRC_DIR):
        root_path = Path(root)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = root_path / file
            if should_skip(file_path):
                continue

            total_files_checked += 1
            bad = scan_file(file_path)
            if bad:
                found_files += 1
                rel_path = file_path.relative_to(PROJECT_ROOT)
                print(f"Found old imports in:\n  {rel_path}")
                for line_num, line_content in bad:
                    print(f"    line {line_num:3d} | {line_content}")
                print()

    if found_files == 0:
        print("No old-style imports found ✓ Clean!")
    else:
        print(f"Found issues in {found_files} file(s). Fix by removing 'mcp_db_analyst_assignment.' prefix.")

    print(f"\nChecked {total_files_checked} .py files.")

if __name__ == "__main__":
    main()