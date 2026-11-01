"""Stage 2 Python parser and symbol extraction tests."""

from engines.indexer.parser import PythonParser


def test_parser_extracts_classes_and_methods(sample_project):
    parser = PythonParser()
    result = parser.parse(
        str(sample_project / "sample_pkg" / "registry.py"),
        str(sample_project),
    )
    assert result.parse_error is None
    assert any(item.name == "ToolRegistry" for item in result.classes)
    registry = next(item for item in result.classes if item.name == "ToolRegistry")
    assert registry.docstring == "Registry for tools."
    assert any(item.name == "execute" for item in registry.methods)
    assert registry.methods[0].is_async is True


def test_parser_extracts_functions(sample_project):
    parser = PythonParser()
    result = parser.parse(str(sample_project / "main.py"), str(sample_project))
    assert any(item.name == "create_app" for item in result.functions)


def test_parser_extracts_imports(sample_project):
    parser = PythonParser()
    result = parser.parse(str(sample_project / "main.py"), str(sample_project))
    assert any(item.module == "sample_pkg.registry" for item in result.imports)


def test_parser_extracts_symbols(sample_project):
    parser = PythonParser()
    result = parser.parse(
        str(sample_project / "sample_pkg" / "registry.py"),
        str(sample_project),
    )
    symbol_types = {item.symbol_type for item in result.symbols}
    assert "module" in symbol_types
    assert "class" in symbol_types
    assert "method" in symbol_types
    assert "constant" in symbol_types


def test_parser_handles_malformed_python(sample_project):
    parser = PythonParser()
    result = parser.parse(str(sample_project / "broken.py"), str(sample_project))
    assert result.parse_error is not None
