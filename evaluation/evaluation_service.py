# This file coordinates both evaluation engines.
# evaluate_response
# evaluate_with_deepeval


from evaluation.evaluator import evaluate_response
from evaluation.deepeval_evaluator import evaluate_with_deepeval


def run_full_evaluation(
    prompt: str,
    response: str,
    reference_answer: str = None,
    context: str = None
) -> dict:

    results = {
        "custom_judge": None,
        "deepeval": None,
        "errors": {}
    }

    # 1. Run Custom LLM-as-a-Judge
    try:
        results["custom_judge"] = evaluate_response(
            prompt=prompt,
            response=response,
            reference_answer=reference_answer,
            context=context
        )

    except Exception as e:
        results["errors"]["custom_judge"] = str(e)

    # 2. Run DeepEval
    try:
        results["deepeval"] = evaluate_with_deepeval(
            prompt=prompt,
            response=response
        )

    except Exception as e:
        results["errors"]["deepeval"] = str(e)

    return results
