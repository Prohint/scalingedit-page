"""Embed the web-optimized project video in index.html for 4open Pages."""

from __future__ import annotations

import base64
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "index.html"
VIDEO_PATH = ROOT / "project-video-web.mp4"
EXTERNAL_SRC = 'src="project-video.mp4"'


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    if EXTERNAL_SRC not in html:
        raise SystemExit("Expected external project-video.mp4 source was not found")

    payload = base64.b64encode(VIDEO_PATH.read_bytes()).decode("ascii")
    embedded_src = f'src="data:video/mp4;base64,{payload}"'
    html = html.replace(EXTERNAL_SRC, embedded_src, 1)
    HTML_PATH.write_text(html, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
