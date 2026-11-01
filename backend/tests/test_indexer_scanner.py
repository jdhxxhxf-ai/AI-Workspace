"""Stage 2 scanner and language detection tests."""

from pathlib import Path

from engines.indexer.language import detect_language, is_indexable_language
from engines.indexer.scanner import ProjectScanner


def test_detect_language_python():
    assert detect_language(Path("main.py")) == "Python"


def test_detect_language_unknown():
    assert detect_language(Path("file.xyz")) == "Unknown"


def test_is_indexable_language():
    assert is_indexable_language("Python") is True
    assert is_indexable_language("Markdown") is False


def test_scanner_excludes_node_modules(sample_project: Path):
    scanner = ProjectScanner(str(sample_project))
    files = scanner.scan_files()
    paths = {item.relative_path for item in files}
    assert "node_modules/ignored.js" not in paths
    assert "main.py" in paths
    assert "readme.md" in paths


def test_scanner_hashes_files(sample_project: Path):
    scanner = ProjectScanner(str(sample_project))
    files = scanner.scan_files()
    main = next(item for item in files if item.relative_path == "main.py")
    assert main.content_hash
    assert len(main.content_hash) == 64


def test_scanner_skips_large_files(tmp_path: Path):
    root = tmp_path / "large"
    root.mkdir()
    large = root / "big.py"
    large.write_text("x = 1\n", encoding="utf-8")
    scanner = ProjectScanner(str(root), max_file_size=1)
    files = scanner.scan_files()
    assert files[0].indexable is False
    assert files[0].skip_reason == "file exceeds size limit"
