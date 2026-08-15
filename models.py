"""Structured data passed between the video-production agents."""

from pydantic import BaseModel, Field


class PlannedScene(BaseModel):
    scene: int = Field(ge=1)
    purpose: str


class VideoPlan(BaseModel):
    title: str
    hook: str
    angle: str
    scenes: list[PlannedScene]


class ProductionScene(BaseModel):
    scene: int = Field(ge=1)
    purpose: str
    script: str
    picture_description: str
    search_query: str


class FinalScene(BaseModel):
    scene: int = Field(ge=1)
    script: str
    picture: str | None
    on_screen_text: str
    editing_note: str
    estimated_duration: float = Field(ge=0)
