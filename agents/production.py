"""Turn an approved video plan into scripts and image requirements.

Implement this module test-first using ``tests/test_production.py``.
"""
from dotenv import load_dotenv
from openai import OpenAI

from config import PRODUCTION_MODEL
from models import ProductionPlan, VideoPlan

# this is for type checking only, so we don't have to import the whole OpenAI client in production
from collections.abc import Callable
from pathlib import Path
import re

SYSTEM_PROMPT = """You are the Production Agent for fast talking-head videos.

Turn the supplied video plan into the exact words the creator should say.

Rules:
- Preserve the title, beat order, and purpose of each beat.
- Write one short, conversational script line per beat.
- Each line should take roughly 1–3 seconds to say.
- Make the full script flow like one continuous recording.
- Start immediately with the hook.
- End with a clear payoff or short CTA.
- Keep the creator visible for most of the video.
- Do not require a visual for every beat.
- Some beats should intentionally be creator-only.
- Supporting visuals should normally appear as overlays.
- When a visual is needed, provide a visual type, picture description, and specific search query.
- For creator-only beats, set visual_needed to false and all visual fields to null.
- Do not generate editing notes or on-screen text.

Return only the required structured output.
"""

SCRIPT_START = "<!-- beat-{beat}-script-start -->"
SCRIPT_END = "<!-- beat-{beat}-script-end -->"

def _validate_production_plan(
    video_plan: VideoPlan,
    production_plan: ProductionPlan,
) -> None:
    expected_numbers = [
        beat.beat
        for beat in video_plan.beats
    ]

    actual_numbers = [
        beat.beat
        for beat in production_plan.beats
    ]

    if actual_numbers != expected_numbers:
        raise ValueError(
            "The production agent must return every planned beat in order."
        )
    if production_plan.title != video_plan.title:
        raise ValueError(
            "The production agent must preserve the planned title."
        )

    for beat in production_plan.beats:
        if not beat.script.strip():
            raise ValueError(
                f"Beat {beat.beat} has an empty script."
            )
        visual_fields = (
            beat.visual_type,
            beat.picture_description,
            beat.search_query,
        )

        if beat.visual_needed:
            if any(
                not value or not value.strip()
                for value in visual_fields
            ):
                raise ValueError(
                    f"Beat {beat.beat} needs complete "
                    "supporting-visual details."
                )
        else:
            if any(
                value is not None
                for value in visual_fields
            ):
                raise ValueError(
                    f"Beat {beat.beat} is creator-only, "
                    "so its visual fields must be null."
                )

def production_agent(
    video_plan: VideoPlan,
    *,
    client: OpenAI | None = None,
    model: str = PRODUCTION_MODEL,
) -> ProductionPlan:
    load_dotenv()

    openai_client = client or OpenAI()

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
                    "Create the production script for this plan:\n"
                    f"{video_plan.model_dump_json(indent=2)}"
                ),
            },
        ],
        text_format=ProductionPlan,
    )

    production_plan = response.output_parsed

    if production_plan is None:
        raise ValueError("OpenAI did not return a production plan.")

    _validate_production_plan(video_plan, production_plan)

    return production_plan

def render_script_markdown(
    production_plan: ProductionPlan,
) -> str:
    lines = [
        f"# {production_plan.title}",
        "",
        "> Review the spoken lines below.",
        "> Edit only the text between the script markers.",
        "> Save this file, then return to the terminal and press Enter.",
        "",
    ]
    for beat in production_plan.beats:
        lines.extend(
            [
                f"## Beat {beat.beat}",
                "",
                f"**Purpose:** {beat.purpose}",
                "",
                "### Script",
                "",
                SCRIPT_START.format(beat=beat.beat),
                beat.script.strip(),
                SCRIPT_END.format(beat=beat.beat),
                "",
            ]
        )
        lines.extend(
            [
                "### Planned supporting visual",
                "",
            ]
        )

        if beat.visual_needed:
            lines.extend(
                [
                    f"- Type: {beat.visual_type}",
                    f"- Description: {beat.picture_description}",
                    f"- Search query: `{beat.search_query}`",
                ]
            )
        else:
            lines.append(
                "Creator only — no image search."
            )

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"

def save_script_for_review(
    production_plan: ProductionPlan,
    script_path: Path,
) -> Path:
    script_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    script_path.write_text(
        render_script_markdown(production_plan),
        encoding="utf-8",
    )

    return script_path


def load_script_edits(
    production_plan: ProductionPlan,
    script_path: Path,
) -> ProductionPlan:
    markdown = script_path.read_text(
        encoding="utf-8"
    )

    updated_plan = production_plan.model_copy(
        deep=True
    )
    for beat in updated_plan.beats:
        start_marker = re.escape(
            SCRIPT_START.format(beat=beat.beat)
        )

        end_marker = re.escape(
            SCRIPT_END.format(beat=beat.beat)
        )

        matches = re.findall(
            f"{start_marker}\\s*(.*?)\\s*{end_marker}",
            markdown,
            re.DOTALL,
        )
        if len(matches) != 1:
            raise ValueError(
                f"Could not read Beat {beat.beat} from {script_path}. "
                "Keep its script markers unchanged."
            )

        edited_script = matches[0].strip()

        if not edited_script:
            raise ValueError(
                f"Beat {beat.beat} has an empty script in {script_path}."
            )

        beat.script = edited_script

    return updated_plan


def wait_for_script_approval(
    production_plan: ProductionPlan,
    script_path: Path,
    *,
    input_fn: Callable[[str], str] = input,
) -> ProductionPlan:
    input_fn(
        f"\nReview and edit {script_path}, save it, "
        "then press Enter to approve the script "
        "and continue to images: "
    )

    return load_script_edits(
        production_plan,
        script_path,
    )
