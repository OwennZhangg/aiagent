"""Turn a video topic into a structured video plan."""

from dotenv import load_dotenv
from openai import OpenAI

from config import PLANNING_MODEL
from models import VideoPlan


SYSTEM_PROMPT = """You are the planning agent for a short-form video producer.

Turn the user's topic into a focused, engaging video plan with 4 to 7 scenes.

Requirements:
- Create a concise, compelling, non-misleading title.
- Write a one-sentence hook that creates immediate curiosity.
- State the central storytelling angle in one sentence.
- Give every scene one distinct purpose.
- Number scenes sequentially starting at 1.
- Make the first scene deliver the hook and the last scene conclude the story.
- Keep each purpose short and specific enough for a production writer to use.
- Do not write scene scripts, image queries, or editing instructions.
- Do not invent precise factual claims that are not provided in the topic.
"""


def _validate_scene_order(plan: VideoPlan) -> None:
    if not 4 <= len(plan.scenes) <= 7:
        raise ValueError("The planning agent must return between 4 and 7 scenes.")

    scene_numbers = [scene.scene for scene in plan.scenes]
    expected_numbers = list(range(1, len(plan.scenes) + 1))

    if scene_numbers != expected_numbers:
        raise ValueError("The planning agent returned invalid scene numbering.")


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

    _validate_scene_order(plan)
    return plan
