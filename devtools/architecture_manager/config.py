from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

BACKEND_ROOT = PROJECT_ROOT / "backend"

IGNORE_DIRS = {
    ".venv",
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
    ".pytest_cache",
}