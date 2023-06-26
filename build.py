import concurrent.futures
import html
import os.path
import shutil
import sys
import traceback
from pathlib import Path
from urllib.parse import quote
from directory_listing import write_directory_listing_recursive

from utils import full_iterdir
from zipfiles import write_zipfile_recursive

# from songs_dl import download_song  # type: ignore


def download_song(song):
    filename = song + ".mp3"
    with open(filename, "w") as f:
        f.write(filename)
    return filename


def download_and_move(song):
    path_str = download_song(song)
    if path_str is None:
        return None
    path = Path(path_str)
    return path.replace(songs_output / path.name)


SLASH = "\\"
enc = "utf-8"

BASE = Path(__file__).parent
songs_lists = BASE / "songs_lists"

pages_output = BASE / "build"
repo = pages_output / "repo"
songs_output = repo / "songs"
INDEX = pages_output / "index.html"

PAGE_MODEL = (BASE / "page_model.html").read_text(enc)

index_content = """\
<h1>Chansons</h1>
<ul>
"""

pages_output_old = pages_output.with_name(pages_output.name + ".old")
if pages_output_old.exists():
    shutil.rmtree(pages_output_old)
if pages_output.exists():
    shutil.rmtree(pages_output)

pages_output.mkdir(parents=True, exist_ok=True)
songs_output.mkdir(parents=True, exist_ok=True)

for file in full_iterdir(songs_lists):
    with file.open(encoding=enc) as f:
        songs = f.readlines()

    songs = [song.strip() for song in songs]

    ret: dict[str, Path | None] = {song: Path() for song in songs}
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_song = {executor.submit(download_and_move, song): song for song in songs}
        for future in concurrent.futures.as_completed(future_to_song):
            song = future_to_song[future]
            try:
                ret[song] = future.result()
            except:  # noqa
                print(f"Error when downloading '{song}':", file=sys.stderr)
                traceback.print_exc()

    output_file = pages_output / (os.path.splitext(file.name)[0] + ".html")
    content = f"""
<h1>{file.name}</h1>
<ul>
"""

    for song, path in ret.items():
        if path is None:
            relative_path = "#"
            extra = ' <span style="color:red">(erreur)</span>'
        else:
            relative_path = os.path.relpath(path, output_file).replace(SLASH, "/")
            extra = ""
        content += f"""\
<li><a href="{html.escape(quote(relative_path))}">{html.escape(song)}{extra}</a></li>
"""

    content += """\
    </ul>
    """

    with output_file.open("w", encoding=enc) as f:
        f.write(PAGE_MODEL % {"title": file.name, "content": content})

    relative_path = os.path.relpath(output_file, INDEX.parent)
    index_content += f"""\
<li><a href="{html.escape(quote(relative_path))}">{file.name}</a></li>
"""

index_content += """\
</ul>
"""

with INDEX.open("w", encoding=enc) as f:
    f.write(PAGE_MODEL % {"title": "Chansons", "content": index_content.replace("\\", "/")})

write_directory_listing_recursive(repo)
write_zipfile_recursive(repo)
