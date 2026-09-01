"""Compose completed scene data into a production guide.

The composer-agent implementation will be added after scene production and
image selection are connected.
"""
from pathlib import Path
import json

from dotenv import load_dotenv
from openai import OpenAI

from config import COMPOSER_MODEL
from models import FinalGuide, ProductionPlan

SYSTEM_PROMPT = """You are the Composer Agent for fast talking-head videos.

Turn the approved script and selected image paths into a practical editing guide.

Rules:
- Preserve the title, beat order, and approved script exactly.
- Do not rewrite the creator's spoken lines.
- Assume the creator filmed one continuous talking-head recording.
- Keep the creator visible for most of the video.
- Use selected pictures as overlays around or above the creator.
- Do not invent picture paths.
- If a beat has no selected picture, keep it creator-only.
- Use short on-screen text only when it adds clarity or emphasis.
- Editing notes should be specific and easy to follow.
- Avoid unnecessary full-screen B-roll.
- Estimate each beat at roughly 1–3 seconds based on its script length.
- The first beat should begin immediately.
- The final beat should deliver the payoff or CTA.

Return only the required structured output.
"""

def _validate_final_guide(
    production_plan: ProductionPlan,
    selected_images: dict[int, Path | None],
    final_guide: FinalGuide,
) -> None:
    expected_numbers = [
        beat.beat
        for beat in production_plan.beats
    ]

    actual_numbers = [
        beat.beat
        for beat in final_guide.beats
    ]

    if actual_numbers != expected_numbers:
        raise ValueError(
            "The Composer Agent must return every beat in order."
        )
    if final_guide.title != production_plan.title:
        raise ValueError(
            "The Composer Agent must preserve the approved title."
        )

    for production_beat, final_beat in zip(
        production_plan.beats,
        final_guide.beats,
    ):
        if final_beat.script != production_beat.script:
            raise ValueError(
                f"The Composer Agent changed the approved "
                f"script for Beat {production_beat.beat}."
            )

        selected_path = selected_images.get(
            production_beat.beat
        )

        expected_picture = (
            str(selected_path)
            if selected_path is not None
            else None
        )

        if final_beat.picture != expected_picture:
            raise ValueError(
                f"The Composer Agent returned the wrong "
                f"picture for Beat {production_beat.beat}."
            )

def composer_agent(
    production_plan: ProductionPlan,
    selected_images: dict[int, Path | None],
    *,
    client: OpenAI | None = None,
    model: str = COMPOSER_MODEL,
) -> FinalGuide:
    load_dotenv()

    openai_client = client or OpenAI()

    image_data = {
        str(beat_number): (
            str(image_path)
            if image_path is not None
            else None
        )
        for beat_number, image_path
        in selected_images.items()
    }
    response = openai_client.responses.parse(
        model=model,
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "Create the final editing guide.\n\n"
                    "Approved production plan:\n"
                    f"{production_plan.model_dump_json(indent=2)}\n\n"
                    "Selected images by beat:\n"
                    f"{json.dumps(image_data, indent=2)}"
                ),
            },
        ],
        text_format=FinalGuide,
    )
    final_guide = response.output_parsed

    if final_guide is None:
        raise ValueError(
            "OpenAI did not return a final editing guide."
        )

    _validate_final_guide(
        production_plan,
        selected_images,
        final_guide,
    )

    return final_guide

def render_production_guide(
    final_guide: FinalGuide,
) -> str:
    lines = [
        f"# {final_guide.title}",
        "",
    ]

    for beat in final_guide.beats:
        lines.extend(
            [
                f"## Beat {beat.beat}",
                "",
                "### Script",
                "",
                beat.script,
                "",
            ]
        )
        lines.extend(
            [
                "### Supporting visual",
                "",
                beat.picture or "Creator only — no image.",
                "",
                "### On-screen text",
                "",
                beat.on_screen_text or "None",
                "",
            ]
        )

        lines.extend(
            [
                "### Editing note",
                "",
                beat.editing_note,
                "",
                "### Estimated duration",
                "",
                f"{beat.estimated_duration:g} seconds",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"

def save_production_guide(
    final_guide: FinalGuide,
    output_path: Path,
) -> Path:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        render_production_guide(final_guide),
        encoding="utf-8",
    )

    return output_path