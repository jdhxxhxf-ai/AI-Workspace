"""Deterministic project discovery and metadata extraction."""

import json
from pathlib import Path

from engines.indexer.language import detect_language
from engines.indexer.models import FileInfo
from engines.indexer.scanner import ProjectScanner
from shared.exceptions import WorkspaceNotFoundError


MANIFEST_FILES = {
    "requirements.txt": "python",
    "pyproject.toml": "python",
    "setup.py": "python",
    "setup.cfg": "python",
    "package.json": "javascript",
    "tsconfig.json": "typescript",
    "Cargo.toml": "rust",
    "go.mod": "go",
    "pom.xml": "java",
    "build.gradle": "java",
}

ENTRY_POINT_CANDIDATES = {
    "main.py",
    "app.py",
    "manage.py",
    "wsgi.py",
    "asgi.py",
    "index.js",
    "index.ts",
    "main.go",
}


class ProjectDiscovery:
    """Discover project metadata without executing project code."""

    def __init__(self, project_path: str) -> None:
        self.root = Path(project_path).resolve()
        if not self.root.is_dir():
            raise WorkspaceNotFoundError(project_path)

    def discover(self) -> dict:
        """Return deterministic project metadata."""
        scanner = ProjectScanner(str(self.root))
        files = scanner.scan_files()
        languages = self._count_languages(files)
        manifests = self._find_manifests()
        entry_points = self._find_entry_points(files)

        return {
            "project_path": str(self.root),
            "name": self.root.name,
            "languages": languages,
            "source_directories": self._source_directories(files),
            "manifest_files": manifests,
            "framework_indicators": self._framework_indicators(manifests),
            "entry_points": entry_points,
            "file_count": len(files),
            "python_file_count": languages.get("Python", 0),
        }

    def _count_languages(self, files: list[FileInfo]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in files:
            counts[item.language] = counts.get(item.language, 0) + 1
        return dict(sorted(counts.items()))

    def _find_manifests(self) -> list[str]:
        found: list[str] = []
        for name in MANIFEST_FILES:
            if (self.root / name).is_file():
                found.append(name)
        return sorted(found)

    def _find_entry_points(self, files: list[FileInfo]) -> list[str]:
        found: list[str] = []
        for item in files:
            if Path(item.relative_path).name in ENTRY_POINT_CANDIDATES:
                found.append(item.relative_path)
        return sorted(found)

    def _source_directories(self, files: list[FileInfo]) -> list[str]:
        directories: set[str] = set()
        for item in files:
            parent = str(Path(item.relative_path).parent)
            if parent and parent != ".":
                directories.add(parent)
        return sorted(directories)

    def _framework_indicators(self, manifests: list[str]) -> list[str]:
        indicators: list[str] = []
        if "pyproject.toml" in manifests or "requirements.txt" in manifests:
            indicators.append("python")
        if "package.json" in manifests:
            package_json = self.root / "package.json"
            try:
                data = json.loads(package_json.read_text(encoding="utf-8"))
                deps = {
                    **data.get("dependencies", {}),
                    **data.get("devDependencies", {}),
                }
                for name in ("react", "next", "vue", "express", "typescript"):
                    if name in deps:
                        indicators.append(name)
            except (OSError, json.JSONDecodeError):
                indicators.append("javascript")
        if "tsconfig.json" in manifests:
            indicators.append("typescript")
        return sorted(set(indicators))
