from pathlib import Path
from typing import Generator


def full_iterdir(path: Path, only_files=False) -> Generator[Path, None, None]:
    for el in sorted(path.iterdir(), key=lambda el: el.is_dir()):
        if el.is_dir():
            yield from full_iterdir(el, only_files)
        if only_files and el.is_dir():
            continue
        yield el
