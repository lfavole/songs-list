import argparse
import concurrent.futures
import html
import logging
import os.path
import shutil
import sys
import traceback
from pathlib import Path
from urllib.parse import quote

from songs_dl import download_song as real_dl  # type: ignore

from directory_listing import write_directory_listing_recursive
from utils import full_iterdir
from zipfiles import write_zipfile_recursive

logger = logging.getLogger(__name__)

BASE = Path(__file__).parent
ANTISLASH = "\\"


def download_song_debug(song):
    filename = song + ".mp3"
    logger.info("Fake downloading '%s'", filename)
    with open(filename, "w") as f:
        f.write(filename)
    return filename


def main(fake=False):
    """
    Create a build of all the songs specified in the `songs_lists` folder.
    """
    logger.info("Starting build")
    if fake:
        download_song = download_song_debug
        logger.info("Fake mode enabled")
    else:
        download_song = real_dl

    def download_and_move(song):
        logger.debug("Downloading song '%s'", song)
        path_str = download_song(song)
        if path_str is None:
            logger.debug("Error while downloading '%s', aborting", song)
            return None

        path = Path(path_str)
        ret = path.replace(songs_output / path.name)
        logger.debug("Song %s moved to %s", path, ret)
        return ret

    enc = "utf-8"

    songs_lists = BASE / "songs_lists"

    pages_output = BASE / "build"
    repo = pages_output / "repo"
    songs_output = repo / "songs"
    index = pages_output / "index.html"

    logger.debug("pages_output=%r", pages_output)
    logger.debug("repo=%r", repo)
    logger.debug("songs_output=%r", songs_output)
    logger.debug("index=%r", index)

    page_model = (BASE / "page_model.html").read_text(enc)
    logger.debug("page model loaded, length = %d", len(page_model))

    index_content = """\
<h1>Chansons</h1>
<ul>
"""

    if pages_output.exists():
        logger.debug("Removing old build %s", pages_output)
        shutil.rmtree(pages_output)

    logger.debug("Creating folder %s", pages_output)
    pages_output.mkdir(parents=True, exist_ok=True)
    songs_output.mkdir(parents=True, exist_ok=True)

    for file in full_iterdir(songs_lists):
        logger.info("Song list found: %s", file)
        with file.open(encoding=enc) as f:
            songs = f.readlines()

        songs = [song.strip() for song in songs]
        logger.info("%d songs found", len(songs))

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
                relative_path = ""
                extra = ' <span style="color:red">(erreur)</span>'
            else:
                relative_path = os.path.relpath(path, output_file).replace(ANTISLASH, "/")
                extra = ""
            content += f"""\
    <li><a href="{html.escape(quote(relative_path))}">{html.escape(song)}{extra}</a></li>
"""

        content += """\
</ul>
"""

        with output_file.open("w", encoding=enc) as f:
            f.write(page_model % {"title": file.name, "content": content})

        relative_path = os.path.relpath(output_file, index.parent)
        index_content += f"""\
    <li><a href="{html.escape(quote(relative_path))}">{file.name}</a></li>
"""

    index_content += """\
</ul>
"""

    with index.open("w", encoding=enc) as f:
        f.write(page_model % {"title": "Chansons", "content": index_content.replace("\\", "/")})

    write_directory_listing_recursive(repo)
    write_zipfile_recursive(repo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="count", help="show more information")
    parser.add_argument("--fake", help="create a build with fake songs")
    args = parser.parse_args()

    logging.root.setLevel(
        {
            0: logging.WARNING,
            1: logging.INFO,
            2: logging.DEBUG,
        }.get(args.verbose, logging.WARNING)
    )

    main(args.fake)
