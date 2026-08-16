"""Turn an approved video plan into scripts and image requirements.

Implement this module test-first using ``tests/test_production.py``.
"""
from dotenv import load_dotenv
from openai import OpenAI

from config import PRODUCTION_MODEL
from models import ProductionPlan, VideoPlan

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



def save_script_for_review(*args, **kwargs):
    raise NotImplementedError


def load_script_edits(*args, **kwargs):
    raise NotImplementedError


def wait_for_script_approval(*args, **kwargs):
    raise NotImplementedError
