# Defines the structure of evaluation results.
from pydantic import BaseModel, Field

class MetricResult(BaseModel):
    score: float | None=Field(
        default=None, ge=0, le=10

    )
    reason: str

    weaknesses : list[str] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    accuracy : MetricResult
    relevance: MetricResult
    faithfulness: MetricResult
    clarity: MetricResult
    completeness: MetricResult
    overall_score: float | None=None
    summary: str    
