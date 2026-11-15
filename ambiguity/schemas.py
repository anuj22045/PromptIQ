from pydantic import BaseModel, Field
from typing import Optional, Literal

class Interpretation(BaseModel):
    title: str
    description  :str


class AmbiguityResult(BaseModel):
    is_ambiguous: bool

    needs_clarification: bool

    ambiguity_level: Literal[
        "none",
        "low",
        "medium",
        "high"
    ]

    possible_interpretations : list[Interpretation] = Field(
        default_factory = list
    )

    clarification_question: Optional[str] = None

    reason : str


class ClarificationResolution(BaseModel):
    original_prompt:str
    selected_intent: str
    intent_description: str
    clarified_prompt: str