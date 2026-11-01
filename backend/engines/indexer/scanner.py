"""Safe, configurable project scanning and language detection."""

import hashlib
from pathlib import Path

from config.settings import settings
from engines.indexer.language import detect_language
from engines.indexer.models import FileInfo

DEFAULT_EXCLUSIONS = {
    ".git", ".venv", "venv", "env", ".idea", ".vscode", "__pycache__",
    ".pytest_cache", "node_modules", "dist", "build", "coverage", ".next",
    ".cache", "cache",
}


class ProjectScanner:
    """Recursively scan indexable project files without following symlinks."""

    def __init__(
        self,
        project_path: str,
        excluded_dirs: set[str] | None = None,
        max_file_size: int | None = None,
    ) -> None:
        self.project = Path(project_path).resolve()
        self.ignore = DEFAULT_EXCLUSIONS | set(settings.indexer_ignore_dirs)
        if excluded_dirs:
            self.ignore |= excluded_dirs
        self.max_file_size = max_file_size or settings.indexer_max_file_size

    def scan(self) -> list[Path]:
        """Stage 1-compatible Python source file discovery."""
        return [Path(item.absolute_path) for item in self.scan_files() if item.language == "Python"]

    def scan_files(self) -> list[FileInfo]:
        """Return metadata for supported files, safely skipping unsuitable files."""
        if not self.project.is_dir():
            return []
        results: list[FileInfo] = []
        for path in self.project.rglob("*"):
            try:
                if path.is_symlink() or not path.is_file():
                    continue
                relative = path.relative_to(self.project)
                if any(part in self.ignore for part in relative.parts):
                    continue
                language = detect_language(path)
                if language == "Unknown":
                    continue
                stat = path.stat()
                indexable = stat.st_size <= self.max_file_size
                results.append(FileInfo(
                    relative_path=relative.as_posix(), absolute_path=str(path),
                    extension=path.suffix.lower(), language=language, size=stat.st_size,
                    modified_at=stat.st_mtime, content_hash=self._hash(path) if indexable else None,
                    indexable=indexable, skip_reason=None if indexable else "file exceeds size limit",
                ))
            except (OSError, ValueError):
                continue
        return sorted(results, key=lambda item: item.relative_path)

    @staticmethod
    def _hash(path: Path) -> str | None:
        try:
            digest = hashlib.sha256()
            with path.open("rb") as source:
                for chunk in iter(lambda: source.read(65536), b""):
                    digest.update(chunk)
            return digest.hexdigest()
        except OSError:
            return None
