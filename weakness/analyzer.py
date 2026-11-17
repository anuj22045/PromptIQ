
from weakness.schemas import (
    LowScoreFinding,
    MetricFeedback,
    WeaknessAnalysisResult
)


# ---------------------------------------
# CONFIGURATION
# ---------------------------------------

LOW_SCORE_THRESHOLD = 7.0


# ---------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------

def convert_to_dict(result):

    if result is None:
        return {}

    if hasattr(result, "model_dump"):
        return result.model_dump()

    if isinstance(result, dict):
        return result

    raise TypeError("Unsupported evaluation result format.")


def normalize_score(value):

    if value is None:
        return None

    return round(float(value), 2)


# ---------------------------------------
# MAIN WEAKNESS ANALYZER
# ---------------------------------------

def analyze_weaknesses(evaluation_results):

    custom_results = convert_to_dict(
        evaluation_results.get("custom_judge")
    )

    deepeval_results = evaluation_results.get(
        "deepeval"
    ) or {}

    errors = evaluation_results.get("errors", {})

    low_scoring_dimensions = []

    existing_weaknesses = []

    metric_feedback = []

    # =====================================
    # 1. CUSTOM LLM-AS-A-JUDGE ANALYSIS
    # =====================================

    custom_metrics = [
        "accuracy",
        "relevance",
        "faithfulness",
        "clarity",
        "completeness"
    ]

    for metric_name in custom_metrics:

        metric = custom_results.get(metric_name)

        if not isinstance(metric, dict):
            continue

        score = normalize_score(metric.get("score"))

        reason = metric.get("reason") or ""

        weaknesses = metric.get("weaknesses") or []

        # Store evaluator feedback
        metric_feedback.append(
            MetricFeedback(
                evaluator="Custom LLM-as-a-Judge",
                metric=metric_name,
                score_out_of_10=score,
                reason=reason,
                weaknesses=weaknesses
            )
        )

        # Collect explicitly identified weaknesses
        for weakness in weaknesses:

            if weakness and weakness not in existing_weaknesses:

                existing_weaknesses.append(weakness)

        # Identify low scores
        if score is not None and score < LOW_SCORE_THRESHOLD:

            low_scoring_dimensions.append(
                LowScoreFinding(
                    evaluator="Custom LLM-as-a-Judge",
                    metric=metric_name,
                    score_out_of_10=score,
                    threshold=LOW_SCORE_THRESHOLD,
                    reason=reason
                )
            )

    # =====================================
    # 2. DEEPEVAL ANALYSIS
    # =====================================

    for metric_name, metric in deepeval_results.items():

        if not isinstance(metric, dict):
            continue

        # DeepEval score is available in 0-1 format
        score = metric.get("score")

        # Prefer the existing 0-10 conversion
        score_out_of_10 = metric.get("score_out_of_10")

        if score_out_of_10 is None and score is not None:

            score_out_of_10 = float(score) * 10

        score_out_of_10 = normalize_score(
            score_out_of_10
        )

        reason = metric.get("reason") or ""

        metric_feedback.append(
            MetricFeedback(
                evaluator="DeepEval",
                metric=metric_name,
                score_out_of_10=score_out_of_10,
                reason=reason
            )
        )

        # Identify low scores
        if (
            score_out_of_10 is not None
            and score_out_of_10 < LOW_SCORE_THRESHOLD
        ):

            low_scoring_dimensions.append(
                LowScoreFinding(
                    evaluator="DeepEval",
                    metric=metric_name,
                    score_out_of_10=score_out_of_10,
                    threshold=LOW_SCORE_THRESHOLD,
                    reason=reason
                )
            )

    # =====================================
    # 3. CONDITIONAL ANALYSIS DECISION
    # =====================================

    has_low_scores = bool(low_scoring_dimensions)

    has_explicit_weaknesses = bool(existing_weaknesses)

    needs_deeper_analysis = (
        has_low_scores or has_explicit_weaknesses
    )

    # =====================================
    # 4. DETERMINE ANALYSIS STATUS
    # =====================================

    has_evaluation_data = bool(metric_feedback)

    if not has_evaluation_data:

        analysis_status = "insufficient_evaluation_data"

        summary = (
            "Evaluation data is unavailable. "
            "Weakness analysis cannot be completed."
        )

        needs_deeper_analysis = False

    elif needs_deeper_analysis:

        analysis_status = "needs_deeper_analysis"

        summary = (
            "Potential weaknesses were identified "
            "by the evaluation engines. Further "
            "analysis is required to verify them."
        )

    else:

        analysis_status = "satisfactory"

        summary = (
            "No significant weaknesses were identified "
            "by the evaluation engines. The response "
            "appears satisfactory at this stage."
        )

    # =====================================
    # 5. RETURN STRUCTURED RESULT
    # =====================================

    return WeaknessAnalysisResult(

        has_low_scoring_dimensions=has_low_scores,

        needs_deeper_analysis=needs_deeper_analysis,

        analysis_status=analysis_status,

        low_scoring_dimensions=low_scoring_dimensions,

        existing_weaknesses=existing_weaknesses,

        metric_feedback=metric_feedback,

        summary=summary
    )
