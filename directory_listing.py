import datetime as dt
import html
import os.path
import re
from pathlib import Path

ANTISLASH = "\\"


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
<h1>Index of {str(relative_or_path(folder, base_path)).replace(ANTISLASH, "/")}</h1>
<table>
    <tr>
        <th>Name</th>
        <th>Last modified</th>
        <th>Size</th>
    </tr>
"""

    paths = sorted(folder.iterdir(), key=lambda path: path.is_dir())
    if folder.parent != folder:
        paths.insert(0, folder.parent)

    for path in paths:
        path_escaped = str(os.path.relpath(path, folder)).replace(ANTISLASH, "/") + ("/" if path.is_dir() else "")
        content += f"""\
<tr>
    <td><a href="{html.escape(path_escaped, quote=True)}">{html.escape(path_escaped)}</a></td>
    <td>{dt.datetime.fromtimestamp(int(os.path.getmtime(path)))}</td>
    <td>{"" if path.is_dir() else sizeof_fmt(os.path.getsize(path))}</td>
</tr>
"""

    content += """\
</table>
"""

    return content


def write_directory_listing(folder: Path, base_path: Path | None = None, template: str = "%(content)s"):
    """
    Write a directory listing for the given `folder`.

    The `base_path` is used to format the title.
    """
    data = make_directory_listing(folder, base_path)
    match = re.search(r"<h1>(.*?)</h1>", data)
    with open(folder / "index.html", "w") as f:
        f.write(template % {"title": match.group(1) if match else "Directory listing", "content": data})


def write_directory_listing_recursive(folder: Path, base_path: Path | None = None, template: str = "%(content)s"):
    """
    Write a directory listing for the given `folder` and all subfolders, recursively.

    The `base_path` is used to format the title.
    """
    write_directory_listing(folder, base_path, template)
    for path in folder.iterdir():
        if not path.is_dir():
            continue
        write_directory_listing_recursive(path, base_path, template)
