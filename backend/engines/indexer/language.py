"""Language detection abstraction for project files."""

from pathlib import Path

EXTENSION_MAP: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".json": "JSON",
    ".md": "Markdown",
    ".html": "HTML",
    ".css": "CSS",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".toml": "TOML",
    ".sql": "SQL",
}


def detect_language(path: Path) -> str:
    """Return a deterministic language label based on file extension."""
    return EXTENSION_MAP.get(path.suffix.lower(), "Unknown")


def is_indexable_language(language: str) -> bool:
    """Return True when the language supports deep static analysis."""
    return language == "Python"
