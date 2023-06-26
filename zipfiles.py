from pathlib import Path
import shutil


def write_zipfile(folder: Path):
    shutil.make_archive(str(folder), "zip", folder)


def write_zipfile_recursive(folder: Path):
    write_zipfile(folder)
    for el in folder.iterdir():
        if not el.is_dir():
            continue
        write_zipfile(el)
