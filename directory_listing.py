import datetime as dt
import html
import os.path
from pathlib import Path

SLASH = "\\"


# https://stackoverflow.com/a/1094933
def sizeof_fmt(num, suffix="B"):
    """
    Return a human formatted file size with the given suffix.
    """
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def relative_or_path(path: Path, base_path: Path | None):
    """
    Return the path relative to the base path if the latter is given, or return the path unchanged.
    """
    return path.relative_to(base_path) if base_path else path


def make_directory_listing(folder: Path, base_path: Path | None = None):
    """
    Return the HTML body of the directory listing for the given `folder`.

    The `base_path` is used to format the title.
    """
    content = f"""\
<h1>Index of {relative_or_path(folder, base_path)}</h1>
<table>
    <tr>
        <td>Name</td>
        <td>Last modified</td>
        <td>Size</td>
    </tr>
"""

    for path in sorted(folder.iterdir(), key=lambda path: path.is_dir()):
        path_escaped = html.escape(str(path.relative_to(folder)).replace(SLASH, "/")) + ("/" if path.is_dir() else "")
        content += f"""\
<tr>
    <td><a href="{path_escaped}">{path_escaped}</a></td>
    <td>{dt.datetime.fromtimestamp(os.path.getmtime(path))}</td>
    <td>{sizeof_fmt(os.path.getsize(path))}</td>
</tr>
"""

    content += """\
</table>
"""

    return content


def write_directory_listing(folder: Path, base_path: Path | None = None):
    """
    Write a directory listing for the given `folder`.

    The `base_path` is used to format the title.
    """
    data = make_directory_listing(folder, base_path)
    with open(folder / "index.html", "w") as f:
        f.write(data)


def write_directory_listing_recursive(folder: Path, base_path: Path | None = None):
    """
    Write a directory listing for the given `folder` and all subfolders, recursively.

    The `base_path` is used to format the title.
    """
    write_directory_listing(folder, base_path)
    for path in folder.iterdir():
        if not path.is_dir():
            continue
        write_directory_listing_recursive(path, base_path)
