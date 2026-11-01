"""Python AST parser for deterministic, non-executing structural analysis."""

import ast
from pathlib import Path

from engines.indexer.models import ClassInfo, FunctionInfo, ImportInfo, PythonFileInfo, SymbolInfo
from shared.constants import DEFAULT_ENCODING


def _source(node: ast.AST | None) -> str | None:
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except ValueError:
        return None


def _parameters(node: ast.arguments) -> list[str]:
    values = [argument.arg for argument in node.posonlyargs + node.args + node.kwonlyargs]
    if node.vararg:
        values.append(f"*{node.vararg.arg}")
    if node.kwarg:
        values.append(f"**{node.kwarg.arg}")
    return values


class PythonParser:
    """Extract modules, imports, classes, functions, methods, and constants."""

    def parse(
        self, file_path: str, project_root: str | None = None,
    ) -> PythonFileInfo:
        path = Path(file_path)
        relative = path.name
        if project_root:
            try:
                relative = path.resolve().relative_to(Path(project_root).resolve()).as_posix()
            except ValueError:
                pass
        module_path = relative.removesuffix(".py").replace("/", ".")
        if module_path.endswith(".__init__"):
            module_path = module_path[:-9]
        try:
            source = path.read_text(encoding=DEFAULT_ENCODING, errors="replace")
            tree = ast.parse(source, filename=str(path))
        except (OSError, SyntaxError, UnicodeError) as error:
            return PythonFileInfo(path=str(path), relative_path=relative, module_path=module_path, parse_error=str(error))

        imports: list[ImportInfo] = []
        classes: list[ClassInfo] = []
        functions: list[FunctionInfo] = []
        symbols: list[SymbolInfo] = [SymbolInfo(
            name=module_path or path.stem, qualified_name=module_path or path.stem,
            symbol_type="module", line_start=1, line_end=len(source.splitlines()),
        )]

        for node in tree.body:
            if isinstance(node, ast.Import):
                for imported in node.names:
                    imports.append(ImportInfo(module=imported.name, alias=imported.asname, line=node.lineno))
            elif isinstance(node, ast.ImportFrom):
                imports.append(ImportInfo(
                    module=node.module or "", imported=[item.name for item in node.names],
                    alias=node.names[0].asname if len(node.names) == 1 else None,
                    relative_level=node.level, line=node.lineno,
                ))
            elif isinstance(node, ast.ClassDef):
                class_info = self._class(node, module_path)
                classes.append(class_info)
                symbols.append(SymbolInfo(
                    name=node.name, qualified_name=class_info.qualified_name or node.name,
                    symbol_type="class", line_start=node.lineno, line_end=getattr(node, "end_lineno", None),
                    metadata={"bases": class_info.bases, "decorators": class_info.decorators},
                ))
                for child in node.body:
                    if isinstance(child, (ast.Assign, ast.AnnAssign)):
                        for target in self._assignment_names(child):
                            symbols.append(SymbolInfo(
                                name=target,
                                qualified_name=f"{class_info.qualified_name}.{target}" if class_info.qualified_name else target,
                                symbol_type="constant" if target.isupper() else "variable",
                                line_start=child.lineno,
                                line_end=getattr(child, "end_lineno", None),
                                parent_symbol=class_info.qualified_name,
                            ))
                for method in class_info.methods:
                    symbols.append(SymbolInfo(
                        name=method.name, qualified_name=method.qualified_name or method.name,
                        symbol_type="method", line_start=method.line, line_end=method.end_line,
                        parent_symbol=class_info.qualified_name, metadata={"async": method.is_async},
                    ))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function = self._function(node, module_path)
                functions.append(function)
                symbols.append(SymbolInfo(
                    name=function.name, qualified_name=function.qualified_name or function.name,
                    symbol_type="function", line_start=function.line, line_end=function.end_line,
                    metadata={"async": function.is_async, "decorators": function.decorators},
                ))
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                for target in self._assignment_names(node):
                    symbols.append(SymbolInfo(
                        name=target, qualified_name=f"{module_path}.{target}" if module_path else target,
                        symbol_type="constant" if target.isupper() else "variable",
                        line_start=node.lineno, line_end=getattr(node, "end_lineno", None),
                    ))
        return PythonFileInfo(
            path=str(path), relative_path=relative, module_path=module_path,
            module_docstring=ast.get_docstring(tree), imports=imports, classes=classes,
            functions=functions, symbols=symbols,
        )

    @staticmethod
    def _assignment_names(node: ast.Assign | ast.AnnAssign) -> list[str]:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        return [target.id for target in targets if isinstance(target, ast.Name)]

    def _class(self, node: ast.ClassDef, module: str) -> ClassInfo:
        qualified = f"{module}.{node.name}" if module else node.name
        methods = [self._function(child, qualified) for child in node.body
                   if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))]
        return ClassInfo(
            name=node.name, qualified_name=qualified, line=node.lineno,
            end_line=getattr(node, "end_lineno", None), bases=[_source(base) or "" for base in node.bases],
            decorators=[_source(item) or "" for item in node.decorator_list], methods=methods,
            docstring=ast.get_docstring(node),
        )

    @staticmethod
    def _function(node: ast.FunctionDef | ast.AsyncFunctionDef, parent: str) -> FunctionInfo:
        qualified = f"{parent}.{node.name}" if parent else node.name
        return FunctionInfo(
            name=node.name, qualified_name=qualified, line=node.lineno,
            end_line=getattr(node, "end_lineno", None), parameters=_parameters(node.args),
            decorators=[_source(item) or "" for item in node.decorator_list],
            return_annotation=_source(node.returns), docstring=ast.get_docstring(node),
            is_async=isinstance(node, ast.AsyncFunctionDef),
        )
