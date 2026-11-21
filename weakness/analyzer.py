
from weakness.schemas import (
    LowScoreFinding,
    MetricFeedback,
    WeaknessAnalysisResult
)

import json
import os

from groq import Groq
from dotenv import load_dotenv
load_dotenv()

from weakness.schemas import DeeperWeaknessResult

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

    if not has_evaluation_data or errors:

        analysis_status = "insufficient_evaluation_data"

        summary = (
            "Evaluation data is incomplete or unavailable. "
            "The analysis cannot confidently classify "
            "the response as satisfactory."
        )

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



# =====================================
# PHASE 5B - DEEPER WEAKNESS ANALYSIS
# =====================================

def analyze_deeper_weaknesses(
    prompt,
    response,
    phase5a_result
):

    # Convert Phase 5A result into dictionary
    phase5a_data = convert_to_dict(phase5a_result)

    # Do not call Groq if Phase 5A found no weaknesses
    if phase5a_data.get("analysis_status") == "satisfactory":

        return DeeperWeaknessResult(
            needs_refinement=False,
            overall_status="satisfactory",
            requirement_checks=[],
            identified_weaknesses=[],
            missing_requirements=[],
            recommendations=[],
            summary=(
                "No significant weaknesses were detected "
                "during the initial evaluation."
            )
        )

    # Never classify incomplete evaluation data as satisfactory
    if phase5a_data.get("analysis_status") == "insufficient_evaluation_data":
        raise ValueError(
            "Phase 5A evaluation data is insufficient."
            "Deeper analysis cannot proceed reliably."
        )

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    if not response or not response.strip():
        raise ValueError("Generated response cannot be empty.")

    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    system_instruction = """
You are an expert LLM response quality analyst.

Your task is to compare the user's original or clarified
prompt with the generated response.

Follow these rules strictly:

1. Identify the actual requirements in the user's prompt.
2. Check whether each requirement is fulfilled.
3. Identify genuinely missing or incomplete information.
4. Validate weaknesses reported by previous evaluators.
5. Do not blindly accept previous evaluator weaknesses.
6. Do not invent additional requirements.
7. Do not recommend making the response longer unless needed.
8. Do not recommend unrelated examples, diagrams,
   advantages, disadvantages, or extra explanations.
9. If the response satisfies the prompt, return no weaknesses.
10. Recommend improvements only for genuine problems.
11. Distinguish response quality from prompt quality.
12. Set needs_refinement to true only when changing the
    prompt itself is justified. A missing response requirement
    does not automatically mean the prompt is defective.

Return only a valid JSON object with these fields:

{
    "needs_refinement": false,
    "overall_status": "satisfactory",
    "requirement_checks": [
        {
            "requirement": "string",
            "status": "fulfilled",
            "explanation": "string"
        }
    ],
    "identified_weaknesses": [],
    "missing_requirements": [],
    "recommendations": [],
    "summary": "string"
}

Allowed overall_status values:
- satisfactory
- needs_improvement

Allowed requirement status values:
- fulfilled
- partially_fulfilled
- missing

Use needs_improvement when the response has genuine problems.

Use satisfactory when the response fulfills the user's request.

Use needs_refinement only when improving the original prompt
would be justified, not merely because the response is poor.
"""

    user_content = (
        "USER PROMPT:\n"
        f"{prompt}\n\n"
        "GENERATED RESPONSE:\n"
        f"{response}\n\n"
        "PHASE 5A FINDINGS:\n"
        f"{json.dumps(phase5a_data, indent=2)}"
    )

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": system_instruction
            },
            {
                "role": "user",
                "content": user_content
            }
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )

    result_text = completion.choices[0].message.content

    if not result_text:
        raise ValueError("Groq returned an empty analysis.")

    result_data = json.loads(result_text)

    result = DeeperWeaknessResult.model_validate(result_data)

    return result