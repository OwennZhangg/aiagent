"""Use OpenAI to select the best candidate image."""

import base64
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from typing import Literal

from pydantic import BaseModel, Field


class ImageSelection(BaseModel):
    selected_number: int = Field(ge=1)


def image_to_data_url(image_path: Path) -> str:
    image_bytes = image_path.read_bytes()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    return f"data:image/jpeg;base64,{encoded_image}"


def select_best_image(prompt: str, image_paths: list[Path]) -> Path:
    load_dotenv()
    client = OpenAI()

    content = [
        {
            "type": "input_text",
            "text": (
                f'Choose the image that best matches "{prompt}". '
                f"Reply with only a number from 1 to {len(image_paths)}."
            ),
        }
    ]

    for index, image_path in enumerate(image_paths, start=1):
        content.append(
            {
                "type": "input_text",
                "text": f"Image {index}",
            }
        )

        content.append(
            {
                "type": "input_image",
                "image_url": image_to_data_url(image_path),
                "detail": "low",
            }
        )

    response = client.responses.parse(
        model="gpt-5-nano",
        input=[
            {
                "role": "user",
                "content": content,
            }
        ],
        text_format=ImageSelection,
    )

    selection = response.output_parsed

    if selection is None:
        raise ValueError("OpenAI didn't return an image selection.")

    if selection.selected_number > len(image_paths):
        raise ValueError("OpenAI returned an invalid image number.")

    return image_paths[selection.selected_number - 1]