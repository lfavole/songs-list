from pathlib import Path
from typing import Generator


def full_iterdir(base_path: Path, only_files=False) -> Generator[Path, None, None]:
    """
    Iterate recursively over all the files and folders in the specified path.
    """
    for path in sorted(base_path.iterdir(), key=lambda el: el.is_dir()):
        if path.is_dir():
            yield from full_iterdir(path, only_files)
        if only_files and path.is_dir():
            continue
        yield path
