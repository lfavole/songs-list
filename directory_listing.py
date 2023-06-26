import datetime as dt
import html
import os.path
from pathlib import Path

SLASH = "\\"


# https://stackoverflow.com/a/1094933
def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def relative_or_path(path: Path, base_path: Path | None):
    return path.relative_to(base_path) if base_path else path


def make_directory_listing(folder: Path, base_path: Path | None = None):
    content = f"""\
<h1>Index of {relative_or_path(folder, base_path)}</h1>
<table>
    <tr>
        <td>Name</td>
        <td>Last modified</td>
        <td>Size</td>
    </tr>
"""

    for el in sorted(folder.iterdir(), key=lambda el: el.is_dir()):
        path_escaped = html.escape(str(el.relative_to(folder)).replace(SLASH, "/")) + ("/" if el.is_dir() else "")
        content += f"""\
<tr>
    <td><a href="{path_escaped}">{path_escaped}</a></td>
    <td>{dt.datetime.fromtimestamp(os.path.getmtime(el))}</td>
    <td>{sizeof_fmt(os.path.getsize(el))}</td>
</tr>
"""

    content += """\
</table>
"""

    return content


def write_directory_listing(folder: Path, base_path: Path | None = None):
    data = make_directory_listing(folder, base_path)
    with open(folder / "index.html", "w") as f:
        f.write(data)


def write_directory_listing_recursive(folder: Path, base_path: Path | None = None):
    write_directory_listing(folder, base_path)
    for el in folder.iterdir():
        if not el.is_dir():
            continue
        write_directory_listing_recursive(el, base_path)
