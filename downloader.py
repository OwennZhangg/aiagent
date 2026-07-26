"""Download and save candidate images."""
from pathlib import Path

import httpx


def download_image(image_url: str, output_path: Path) -> None:
    response = httpx.get(
        image_url,
        follow_redirects=True,
        timeout=30.0,
    )

    response.raise_for_status()

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_bytes(response.content)

    