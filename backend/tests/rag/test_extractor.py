"""Unit tests for document extraction pipeline."""

from pathlib import Path

from engines.indexer.models import FileInfo
from engines.rag.domain.extractor import DocumentExtractor


def test_classify_source_types():
    extractor = DocumentExtractor()
    assert extractor.classify_source_type("main.py") == "source_code"
    assert extractor.classify_source_type("README.md") == "documentation"
    assert extractor.classify_source_type("pyproject.toml") == "configuration"
    assert extractor.classify_source_type("tests/test_api.py") == "test"


def test_extract_python_document(sample_project: Path):
    extractor = DocumentExtractor()
    file_info = FileInfo(
        relative_path="main.py",
        absolute_path=str(sample_project / "main.py"),
        extension=".py",
        language="Python",
        size=100,
        modified_at=0.0,
        content_hash="hash123",
        indexable=True,
    )

    doc = extractor.extract_document(str(sample_project), file_info)
    assert doc is not None
    assert doc.relative_path == "main.py"
    assert doc.language == "Python"
    assert doc.source_type == "source_code"
    assert len(doc.ast_symbols) > 0
