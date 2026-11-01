from pathlib import Path

from .config import BACKEND_ROOT, IGNORE_DIRS

from .utils import is_python_file


class ProjectScanner:

    def __init__(self):
        self.root = BACKEND_ROOT

    def should_ignore(self, path: Path) -> bool:
        return any(part in IGNORE_DIRS for part in path.parts)

    def scan(self):

        result = {
            "root": str(self.root),
            "directories": [],
            "python_files": [],
            "packages": [],
            "total_directories": 0,
            "total_python_files": 0,
        }

        for item in self.root.rglob("*"):

            if self.should_ignore(item):
                continue

            if item.is_dir():

                result["directories"].append(str(item))
                result["total_directories"] += 1

                if (item / "__init__.py").exists():
                    result["packages"].append(str(item))

            elif is_python_file(item):

                result["python_files"].append(str(item))
                result["total_python_files"] += 1

        return result