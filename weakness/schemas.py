from pydantic import BaseModel, Field
from typing import Literal

class LowScoreFinding(BaseModel):
    evaluator :str
    metric: str
    score_out_of_10 : float
    threshold:float
    reason:str

class metricFeedbaack(BaseModel):
    evaluator: str
    metric: str
    score_out_of_10: float | None=None
    reason: str=""
    weaknesses: list[str] = Field(default_factory=list)

class WeaknessAnalysisResult(BaseModel):
    has_low_scoring_dimensions:bool
    needs_deeper_analysis:bool
    analysis_status: Literal[
        "satisfactory",
        "needs_deeper_analysis",
        "insufficient_evaluation_data"
    ]
    low_scoring_dimensions: list[LowScoreFinding] = Field(
        default_factory=list
    )
    existing_weaknesses: list[str] = Field(
        default_factory=list
    )
    metric_feedback: list[MetricFeedback] =Field(
        default_factory=list
    )
    summary:str

