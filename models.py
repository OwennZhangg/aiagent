"""Structured data passed between the video-production agents."""

from pydantic import BaseModel, Field


class PlannedBeat(BaseModel):
    beat: int = Field(ge=1)
    purpose: str


class VideoPlan(BaseModel):
    title: str
    hook: str
    angle: str
    beats: list[PlannedBeat]


class ProductionBeat(BaseModel):
    beat: int = Field(ge=1)
    purpose: str
    script: str
    visual_needed: bool
    visual_type: str | None = None
    picture_description: str | None = None
    search_query: str | None = None


class ProductionPlan(BaseModel):
    title: str
    beats: list[ProductionBeat]


class FinalBeat(BaseModel):
    beat: int = Field(ge=1)
    script: str
    picture: str | None
    on_screen_text: str
    editing_note: str
    estimated_duration: float = Field(ge=0)
