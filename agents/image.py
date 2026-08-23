"""Find and select supporting images for approved production beats.

This agent will orchestrate the reusable image utilities in ``tools``.
"""

from pathlib import Path

from models import ProductionPlan
from tools.browser import search_google_images_batch
from tools.downloader import (
    download_images,
    save_selected_image,
)
from tools.selector import select_best_image

def image_agent(
    production_plan: ProductionPlan,
    run_directory: Path,
    *,
    search_fn=search_google_images_batch,
    download_fn=download_images,
    select_fn=select_best_image,
    save_fn=save_selected_image,
) -> dict[int, Path | None]:
    selected_images: dict[int, Path | None] = {}
    visual_beats = []
    search_queries: list[str] = []

    for beat in production_plan.beats:
        if not beat.visual_needed:
            selected_images[beat.beat] = None

            print(
                f"Beat {beat.beat} — creator only, "
                "skipping image search"
            )

            continue

        if not beat.search_query:
            selected_images[beat.beat] = None

            print(
                f"Beat {beat.beat} — missing search query"
            )

            continue

        visual_beats.append(beat)
        search_queries.append(beat.search_query)

    # creator only
    if not visual_beats:
        return selected_images

    try:
        image_url_batches = search_fn(
            search_queries
        )
    except Exception as error:
        print(f"Batch image search failed: {error}")

        for beat in visual_beats:
            selected_images[beat.beat] = None

        return selected_images

    if len(image_url_batches) != len(visual_beats):
        print(
            "Batch image search returned the wrong "
            "number of result groups."
        )

        for beat in visual_beats:
            selected_images[beat.beat] = None

        return selected_images

    for beat, image_urls in zip(
        visual_beats,
        image_url_batches,
    ):
        beat_directory = (
            run_directory
            / "beats"
            / f"beat{beat.beat}"
        )

        try:
            if not image_urls:
                raise ValueError(
                    f"Beat {beat.beat} found no image URLs."
                )
            candidate_paths = download_fn(
                image_urls,
                beat_directory,
            )

            if not candidate_paths:
                raise ValueError(
                    f"Beat {beat.beat} downloaded no usable images."
                )

            selected_candidate = select_fn(
                beat.search_query,
                candidate_paths,
            )

            selected_path = save_fn(
                selected_candidate,
                beat_directory,
            )

            selected_images[beat.beat] = selected_path

            print(
                f"Beat {beat.beat} — selected "
                f"{selected_path}"
            )
        except Exception as error:
            selected_images[beat.beat] = None

            print(
                f"Beat {beat.beat} — image failed: "
                f"{error}"
            )

    return selected_images
