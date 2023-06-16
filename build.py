import concurrent.futures
import os.path
import sys
import traceback
from pathlib import Path
from urllib.parse import quote

from songs_dl import download_song  # type: ignore


def download_and_move(song):
    path = Path(download_song(song))
    return path.replace(songs_output / path)


SLASH = "\\"
enc = "utf-8"

BASE = Path(__file__).parent
INDEX = BASE / "source/index.md"
songs_lists = BASE / "songs_lists"
source = BASE / "source"
songs_output = source / "_static/songs"
pages_output = source / "songs"

songs_output.mkdir(parents=True, exist_ok=True)
pages_output.mkdir(parents=True, exist_ok=True)

index_content = """\
# Chansons

"""

for file in songs_lists.iterdir():
    with file.open(encoding=enc) as f:
        songs = f.readlines()

    songs = [song.strip() for song in songs]

    ret: dict[str, Path] = {song: Path() for song in songs}
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_song = {executor.submit(download_and_move, song): song for song in songs}
        for future in concurrent.futures.as_completed(future_to_song):
            song = future_to_song[future]
            try:
                ret[song] = Path(future.result())
            except:  # noqa
                print(f"Error when downloading '{song}':", file=sys.stderr)
                traceback.print_exc()

    output_file = pages_output / (os.path.splitext(file.name)[0] + ".md")
    with output_file.open("w", encoding=enc) as f:
        f.write(
            f"""\
# {file.name}

"""
        )
        for song, path in ret.items():
            f.write(
                f"""\
- [{song}](../{quote(str(path.relative_to(source)).replace(SLASH, "/"))})
"""
            )

    index_content += f"""\
- [{file.name}]({output_file.relative_to(source)})
"""

with INDEX.open("w", encoding=enc) as f:
    f.write(index_content.replace("\\", "/"))
