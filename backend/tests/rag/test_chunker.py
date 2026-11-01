"""Unit tests for code-aware Python AST chunker, Markdown chunker, and Generic chunker."""

from engines.rag.chunking.generic_chunker import GenericChunker
from engines.rag.chunking.markdown_chunker import MarkdownChunker
from engines.rag.chunking.python_chunker import PythonCodeChunker
from engines.rag.models import KnowledgeDocument


def test_python_code_chunker():
    doc = KnowledgeDocument(
        file_path="/tmp/sample.py",
        relative_path="sample.py",
        language="Python",
        source_type="source_code",
        content="""
class Calculator:
    def add(self, a, b):
        return a + b

def standalone():
    return True
""",
        content_hash="hash1",
        ast_symbols=[
            {"name": "Calculator", "symbol_type": "class", "line_start": 2, "line_end": 4, "qualified_name": "sample.Calculator"},
            {"name": "add", "symbol_type": "method", "line_start": 3, "line_end": 4, "qualified_name": "sample.Calculator.add", "parent_symbol": "sample.Calculator"},
            {"name": "standalone", "symbol_type": "function", "line_start": 6, "line_end": 7, "qualified_name": "sample.standalone"},
        ],
    )

    chunker = PythonCodeChunker()
    chunks = chunker.chunk_document(doc, "/tmp")
    assert len(chunks) >= 2
    symbol_names = {c.metadata.symbol_name for c in chunks if c.metadata.symbol_name}
    assert "add" in symbol_names or "Calculator" in symbol_names
    assert "standalone" in symbol_names


def test_markdown_chunker():
    doc = KnowledgeDocument(
        file_path="/tmp/doc.md",
        relative_path="doc.md",
        language="Markdown",
        source_type="documentation",
        content="""# Title Section
This is preamble text.

## Section 1
Content of section 1.

## Section 2
Content of section 2.
""",
        content_hash="hash2",
    )

    chunker = MarkdownChunker()
    chunks = chunker.chunk_document(doc, "/tmp")
    assert len(chunks) >= 2
    titles = {c.metadata.symbol_name for c in chunks if c.metadata.symbol_name}
    assert "Title Section" in titles or "Section 1" in titles


def test_generic_chunker():
    doc = KnowledgeDocument(
        file_path="/tmp/config.json",
        relative_path="config.json",
        language="JSON",
        source_type="configuration",
        content='{"key": "value", "debug": true}',
        content_hash="hash3",
    )

    chunker = GenericChunker()
    chunks = chunker.chunk_document(doc, "/tmp")
    assert len(chunks) == 1
    assert chunks[0].metadata.language == "JSON"
