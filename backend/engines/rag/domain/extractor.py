"""Document extraction pipeline combining filesystem files with Stage 2 intelligence."""

import hashlib
from pathlib import Path

from engines.indexer.database.repository import IndexRepository
from engines.indexer.models import FileInfo
from engines.indexer.parser import PythonParser
from engines.rag.models import KnowledgeDocument
from shared.constants import DEFAULT_ENCODING
from shared.logger import get_logger

logger = get_logger("rag.extractor")

SOURCE_CODE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".rs", ".c", ".cpp", ".h", ".sql", ".sh"
}
DOCUMENTATION_EXTENSIONS = {".md", ".txt", ".rst", ".html"}
CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".env", ".example"}


class DocumentExtractor:
    """Extracts raw documents and attaches Stage 2 structural metadata where available."""

    def __init__(self, repository: IndexRepository | None = None) -> None:
        self.repository = repository
        self.python_parser = PythonParser()

    def classify_source_type(self, relative_path: str) -> str:
        """Classify source type as test, documentation, configuration, or source_code."""
        path_obj = Path(relative_path)
        name = path_obj.name.lower()
        parts = [p.lower() for p in path_obj.parts]

        if "tests" in parts or "test" in parts or name.startswith("test_") or name.endswith("_test.py"):
            return "test"

        ext = path_obj.suffix.lower()
        if ext in DOCUMENTATION_EXTENSIONS:
            return "documentation"
        if ext in CONFIG_EXTENSIONS or name in {"pyproject.toml", "requirements.txt", "package.json"}:
            return "configuration"
        if ext in SOURCE_CODE_EXTENSIONS:
            return "source_code"

        return "other"

    def extract_document(self, project_path: str, file_info: FileInfo) -> KnowledgeDocument | None:
        """Extract a single document, incorporating Stage 2 AST analysis for Python files."""
        abs_path = Path(file_info.absolute_path)
        if not abs_path.is_file():
            return None

        try:
            content = abs_path.read_text(encoding=DEFAULT_ENCODING, errors="replace")
        except OSError as e:
            logger.warning("Failed to read file for extraction %s: %s", file_info.relative_path, e)
            return None

        content_hash = file_info.content_hash or hashlib.sha256(content.encode("utf-8")).hexdigest()
        source_type = self.classify_source_type(file_info.relative_path)

        ast_symbols: list[dict] = []
        ast_imports: list[dict] = []

        if file_info.language == "Python":
            # Prefer Stage 2 SQLite repository intelligence if available, else parse on the fly
            if self.repository:
                try:
                    intel = self.repository.get_file(project_path, file_info.relative_path)
                    if intel:
                        ast_symbols = intel.get("symbols", [])
                        ast_imports = intel.get("imports", [])
                except Exception:
                    pass
            if not ast_symbols:
                parsed = self.python_parser.parse(file_info.absolute_path, project_path)
                ast_symbols = [s.model_dump() for s in parsed.symbols]
                ast_imports = [i.model_dump() for i in parsed.imports]

        return KnowledgeDocument(
            file_path=file_info.absolute_path,
            relative_path=file_info.relative_path,
            language=file_info.language,
            source_type=source_type,
            content=content,
            content_hash=content_hash,
            ast_symbols=ast_symbols,
            ast_imports=ast_imports,
        )
