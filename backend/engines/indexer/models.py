"""Deterministic models used by the Project Intelligence engine."""

from typing import Any

from pydantic import BaseModel, Field


class ImportInfo(BaseModel):
    """An import statement, including enough data for static resolution."""

    module: str
    imported: list[str] = Field(default_factory=list)
    alias: str | None = None
    relative_level: int = 0
    line: int = 0
    resolved_path: str | None = None
    kind: str = "unresolved"


class FunctionInfo(BaseModel):
    """A function or method definition."""

    name: str
    line: int
    end_line: int | None = None
    qualified_name: str | None = None
    parameters: list[str] = Field(default_factory=list)
    decorators: list[str] = Field(default_factory=list)
    return_annotation: str | None = None
    docstring: str | None = None
    is_async: bool = False


class ClassInfo(BaseModel):
    """A class definition and its directly declared methods."""

    name: str
    line: int
    end_line: int | None = None
    qualified_name: str | None = None
    bases: list[str] = Field(default_factory=list)
    decorators: list[str] = Field(default_factory=list)
    methods: list[FunctionInfo] = Field(default_factory=list)
    docstring: str | None = None


class SymbolInfo(BaseModel):
    """A stable structural symbol stored in the project index."""

    id: str = ""
    name: str
    qualified_name: str
    symbol_type: str
    line_start: int
    line_end: int | None = None
    parent_symbol: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PythonFileInfo(BaseModel):
    """Parsed information about a Python source file.

    ``path``, ``imports``, ``classes`` and ``functions`` retain the Stage 1
    response contract. The remaining fields are additive Stage 2 metadata.
    """

    path: str
    relative_path: str = ""
    module_path: str = ""
    language: str = "Python"
    module_docstring: str | None = None
    imports: list[ImportInfo] = Field(default_factory=list)
    classes: list[ClassInfo] = Field(default_factory=list)
    functions: list[FunctionInfo] = Field(default_factory=list)
    symbols: list[SymbolInfo] = Field(default_factory=list)
    parse_error: str | None = None


class FileInfo(BaseModel):
    """Scanner metadata for every supported project file."""

    relative_path: str
    absolute_path: str
    extension: str
    language: str
    size: int
    modified_at: float
    content_hash: str | None = None
    indexable: bool = True
    skip_reason: str | None = None


class DependencyEdge(BaseModel):
    """A proven static relationship between structural nodes."""

    source: str
    target: str
    import_type: str = "direct"
    relationship: str = "IMPORTS"
    line: int = 0
    resolved: bool = False


class ProjectIndex(BaseModel):
    """Legacy-compatible in-memory representation of an index operation."""

    files: list[PythonFileInfo] = Field(default_factory=list)
    dependencies: list[DependencyEdge] = Field(default_factory=list)


class IndexStats(BaseModel):
    scanned: int = 0
    indexed: int = 0
    unchanged: int = 0
    changed: int = 0
    new: int = 0
    deleted: int = 0
    failed: int = 0
    duration_ms: int = 0


class ProjectSummary(BaseModel):
    project_path: str
    name: str
    languages: dict[str, int] = Field(default_factory=dict)
    file_count: int = 0
    python_file_count: int = 0
    symbol_count: int = 0
    class_count: int = 0
    function_count: int = 0
    import_count: int = 0
    internal_dependency_count: int = 0
    entry_points: list[str] = Field(default_factory=list)
    last_indexed_at: str | None = None
