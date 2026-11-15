from pydantic import BaseModel, Field
from typing import Optional, Literal

class Interperation(BaseModel):
    title: str
    description  :str


class AmbiguityResult(BaseModel):
    is_ambiguity: bool
    need_clarification: bool
    ambiguity_level: Literal[
        "None",
        "Low",
        "Medium",
        "high"
    ]

    possible_interperation : list[Interperation] = Field(
        default_factory = list
    )
    clarification_questions: optional[str] = None

    reason : str