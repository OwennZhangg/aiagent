"""Download and save candidate images."""

import shutil
from pathlib import Path

import httpx


def download_image(image_url: str, output_path: Path) -> bool:
    response = httpx.get(
        image_url,
        follow_redirects=True,
        timeout=30.0,
    )

    response.raise_for_status()

    if not response.content.startswith(b"\xff\xd8\xff"):
        print(f"Skipped non-JPEG candidate: {image_url}")
        return False

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_bytes(response.content)

    return True


def download_images(
    image_urls: list[str],
    image_directory: Path,
) -> list[Path]:
    downloaded_paths: list[Path] = []

    for index, image_url in enumerate(image_urls, start=1):
        output_path = image_directory / f"candidate{index}.jpg"

        downloaded = download_image(
            image_url,
            output_path,
        )

        if downloaded:
            downloaded_paths.append(output_path)

    return downloaded_paths


def save_selected_image(
    selected_path: Path,
    image_directory: Path,
) -> Path:
    output_path = image_directory / "selected.jpg"

    shutil.copy2(
        selected_path,
        output_path,
    )

    return output_path
