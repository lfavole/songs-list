import shutil
from pathlib import Path


def write_zipfile(folder: Path):
    """
    Create a zip archive for the given `folder` with the name of the folder.
    """
    shutil.make_archive(str(folder), "zip", folder)


def write_zipfile_recursive(folder: Path):
    """
    Create zip archives for all folders starting from the specified `folder`, recursively.
    """
    write_zipfile(folder)
    for path in folder.iterdir():
        if not path.is_dir():
            continue
        write_zipfile(path)
