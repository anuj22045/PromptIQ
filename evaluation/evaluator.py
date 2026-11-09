# Contains our custom LLM-as-a-Judge logic.

import json
from core.llm_client import generate_chat_response
from evaluation.schemas import EvaluationResult

JUDGE_SYSTEM_PROMPT="""
Yo u are an expert LLM evaluator.

Your task is to evaluate an AI-generated response
using five evaluation dimensions.

Evaluate each dimension on a scale of 0 to 10.

1. Accuracy:
Check whether the information is factually correct.
If a reference answer is provided, use it as the
primary comparison source.
Without a reference, assess factual plausibility
but do not claim independent verification.

2. Relevance:
Check whether the response directly answers
the user's original prompt.

3. Faithfulness:
Check whether the response is supported by
the supplied context.
If no context is supplied, return a null score.
Do not invent a faithfulness score.

4. Clarity:
Check whether the response is understandable,
well-structured and easy to follow.

5. Completeness:
Check whether the response covers all the
requirements mentioned in the original prompt.

Scoring guide:
0-2: Very poor
3-4: Poor
5-6: Average
7-8: Good
9-10: Excellent

Be objective and strict.

Return ONLY valid JSON in the following structure:

{
    "accuracy": {
        "score": 0,
        "reason": "Explanation",
        "weaknesses": []
    },
    "relevance": {
        "score": 0,
        "reason": "Explanation",
        "weaknesses": []
    },
    "faithfulness": {
        "score": null,
        "reason": "Explanation",
        "weaknesses": []
    },
    "clarity": {
        "score": 0,
        "reason": "Explanation",
        "weaknesses": []
    },
    "completeness": {
        "score": 0,
        "reason": "Explanation",
        "weaknesses": []
    },
    "summary": "Overall evaluation summary"
}

Use null for faithfulness when no supporting
context is provided.
"""


def evaluate_response(prompt:str, response:str, reference_answer:str=None, context:str=None)-> EvaluationResult:
    if not prompt or not prompt.strip():
        raise ValueError("prompt cannot be empty")

    if not response or not response.strip():
        raise ValueError("Response cannot be empty")

    evaluation_data={
        "user_prompt": prompt,
        "generated_response":response,
        "reference_answer": reference_answer,
        "supporting_context": context
    }

    messages=[
        {
            "role":"system",
            "content": JUDGE_SYSTEM_PROMPT
        },
        {
            "role":"user",
            "content":json.dumps(evaluation_data)

        }
    ]
    #Ask judge LLM to evaluate
    judge_output = generate_chat_response(
        messages, temperature=0, max_completion_tokens=1500 
    )

    try:
        evaluation_data = json.loads(judge_output)

        result = EvaluationResult.model_validate(
            evaluation_data
        )
        scores=[
            result.accuracy.score,
            result.relevance.score,
            result.faithfulness.score,
            result.clarity.score,
            result.completeness.score
        ]

        valid_scores=[
            score for score in scores
            if score is not None
        ]

        if valid_scores:
            result.overall_score = round(
                sum(valid_scores) / len(valid_scores), 2
            )

        return result

    except Exception as e:
        raise ValueError(
            f"Failed to process evaluation result: {e}"
        )

