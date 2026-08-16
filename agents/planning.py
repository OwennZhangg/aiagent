"""Turn a video topic into a structured video plan."""

from dotenv import load_dotenv
from openai import OpenAI

from config import PLANNING_MODEL
from models import VideoPlan


SYSTEM_PROMPT = """You are the Planning Agent for short-form talking-head videos.

Your job is to turn a topic into a fast, clear video structure made of short script beats.

Planning rules:
- Start immediately with a strong hook.
- Do not use greetings, introductions, or slow setup.
- The hook should use curiosity, surprise, a problem, or a contradiction.
- Structure the video as connected beats, not traditional scenes.
- Each beat should communicate one clear idea.
- Each beat should be suitable for roughly 1–3 seconds of speech.
- Create between 6 and 10 beats. Aim for 8 unless the topic needs fewer or more.
- Keep the structure concise and conversational.
- Make every beat naturally lead into the next.
- End with a clear payoff or conclusion.
- Add a short CTA only when appropriate.
- Assume the creator remains on camera for most of the video.
- Do not search for images.
- Do not choose supporting visuals.
- Do not write editing instructions.

Return:
- title
- hook
- overall angle
- an ordered list of beats
- one clear purpose for each beat

The hook should also be the purpose of the first beat.
Return only the required structured output.
"""


def _validate_beat_order(plan: VideoPlan) -> None:
    if not 6 <= len(plan.beats) <= 10:
        raise ValueError("The planning agent must return between 6 and 10 beats.")

    beat_numbers = [beat.beat for beat in plan.beats]
    expected_numbers = list(range(1, len(plan.beats) + 1))

    if beat_numbers != expected_numbers:
        raise ValueError("The planning agent returned invalid beat numbering.")


def planning_agent(
    topic: str,
    *,
    client: OpenAI | None = None,
    model: str = PLANNING_MODEL,
) -> VideoPlan:
    """Generate and validate a rough video plan for ``topic``."""
    cleaned_topic = topic.strip()

    if not cleaned_topic:
        raise ValueError("Video topic cannot be empty.")

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
                "content": f"Create a video plan for this topic: {cleaned_topic}",
            },
        ],
        text_format=VideoPlan,
    )

    plan = response.output_parsed

    if plan is None:
        raise ValueError("OpenAI did not return a video plan.")

    _validate_beat_order(plan)
    return plan
