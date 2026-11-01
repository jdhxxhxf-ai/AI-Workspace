from pathlib import Path


def is_python_file(path: Path):

    return path.suffix == ".py"


def normalize(path: Path):

    return path.resolve()