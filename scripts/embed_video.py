"""Embed the web video while allowing an immediate poster-first paint."""

from __future__ import annotations

import base64
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "index.html"
VIDEO_PATH = ROOT / "project-video-web.mp4"
POSTER_PATH = ROOT / "video-poster.jpg"


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    video_payload = base64.b64encode(VIDEO_PATH.read_bytes()).decode("ascii")
    poster_payload = base64.b64encode(POSTER_PATH.read_bytes()).decode("ascii")

    video_markup = (
        '<video id="project-video" class="project-video" controls playsinline '
        f'preload="metadata" poster="data:image/jpeg;base64,{poster_payload}" '
        'aria-describedby="project-video-status">\n'
        '              Your browser does not support HTML5 video.\n'
        '            </video>'
    )
    html, count = re.subn(
        r'<video id="project-video"[\s\S]*?</video>',
        video_markup,
        html,
        count=1,
    )
    if count != 1:
        raise SystemExit("Expected project video element was not found")

    data_block = (
        '<script id="project-video-data" type="application/octet-stream">'
        f'{video_payload}</script>\n    '
    )
    if 'id="project-video-data"' not in html:
        anchor = "<script>\nconst embeddedImages ="
        if anchor not in html:
            raise SystemExit("Main script anchor was not found")
        html = html.replace(anchor, data_block + anchor, 1)

    loader = '''

const projectVideoData = document.querySelector("#project-video-data");
if (projectVideo && projectVideoData) {
  try {
    const encodedVideo = projectVideoData.textContent.trim();
    const binaryVideo = atob(encodedVideo);
    const videoBytes = new Uint8Array(binaryVideo.length);
    for (let index = 0; index < binaryVideo.length; index += 1) {
      videoBytes[index] = binaryVideo.charCodeAt(index);
    }
    const projectVideoUrl = URL.createObjectURL(new Blob([videoBytes], { type: "video/mp4" }));
    projectVideo.src = projectVideoUrl;
    projectVideo.load();
    window.addEventListener("pagehide", () => URL.revokeObjectURL(projectVideoUrl), { once: true });
  } catch (error) {
    if (projectVideoStatus) {
      projectVideoStatus.hidden = false;
      projectVideoStatus.textContent = "The project video could not be loaded. Please refresh and try again.";
    }
  }
}
'''
    if "const projectVideoData" not in html:
        anchor = "\nconst fallbackTitle = \"ScalingEdit\";"
        if anchor not in html:
            raise SystemExit("Video loader insertion point was not found")
        html = html.replace(anchor, loader + anchor, 1)

    HTML_PATH.write_text(html, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
