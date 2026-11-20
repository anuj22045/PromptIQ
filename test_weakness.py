
from weakness.analyzer import analyze_weaknesses


# =====================================
# TEST 1: GOOD RESPONSE
# =====================================

good_evaluation = {

    "custom_judge": {

        "accuracy": {
            "score": 9.0,
            "reason": "Accurate explanation.",
            "weaknesses": []
        },

        "relevance": {
            "score": 10.0,
            "reason": "Directly answers the prompt.",
            "weaknesses": []
        },

        "faithfulness": {
            "score": 9.0,
            "reason": "Faithful to provided context.",
            "weaknesses": []
        },

        "clarity": {
            "score": 9.0,
            "reason": "Clear and understandable.",
            "weaknesses": []
        },

        "completeness": {
            "score": 9.0,
            "reason": "All requested points are covered.",
            "weaknesses": []
        },

        "overall_score": 9.2,
        "summary": "Good response."
    },

    "deepeval": {

        "Answer Relevancy": {
            "score": 0.95,
            "score_out_of_10": 9.5,
            "reason": "Highly relevant.",
            "passed": True
        },

        "Clarity": {
            "score": 0.90,
            "score_out_of_10": 9.0,
            "reason": "Clear explanation.",
            "passed": True
        },

        "completeness": {
            "score": 0.90,
            "score_out_of_10": 9.0,
            "reason": "Complete response.",
            "passed": True
        }
    },

    "errors": {}
}


# =====================================
# TEST 2: POOR RESPONSE
# =====================================

poor_evaluation = {

    "custom_judge": {

        "accuracy": {
            "score": 9.0,
            "reason": "Information is accurate.",
            "weaknesses": []
        },

        "relevance": {
            "score": 9.0,
            "reason": "Relevant response.",
            "weaknesses": []
        },

        "faithfulness": {
            "score": 8.0,
            "reason": "Mostly faithful.",
            "weaknesses": []
        },

        "clarity": {
            "score": 8.0,
            "reason": "Easy to understand.",
            "weaknesses": []
        },

        "completeness": {
            "score": 4.0,
            "reason": "Practical example is missing.",
            "weaknesses": [
                "No practical example provided.",
                "RAG workflow is not explained."
            ]
        },

        "overall_score": 7.6,
        "summary": "Response lacks completeness."
    },

    "deepeval": {

        "Answer Relevancy": {
            "score": 0.90,
            "score_out_of_10": 9.0,
            "reason": "Relevant answer.",
            "passed": True
        },

        "Clarity": {
            "score": 0.80,
            "score_out_of_10": 8.0,
            "reason": "Clear language.",
            "passed": True
        },

        "completeness": {
            "score": 0.40,
            "score_out_of_10": 4.0,
            "reason": "Important information is missing.",
            "passed": False
        }
    },

    "errors": {}
}


# =====================================
# RUN TESTS
# =====================================

def print_analysis(title, evaluation):

    print("\n====================================")
    print(title)
    print("====================================")

    result = analyze_weaknesses(evaluation)

    print("\nAnalysis Status:")
    print(result.analysis_status)

    print("\nHas Low Scoring Dimensions:")
    print(result.has_low_scoring_dimensions)

    print("\nNeeds Deeper Analysis:")
    print(result.needs_deeper_analysis)

    print("\nLow Scoring Dimensions:")

    for item in result.low_scoring_dimensions:

        print(
            f"- {item.evaluator}: "
            f"{item.metric} = {item.score_out_of_10}/10"
        )

    print("\nExisting Weaknesses:")

    for weakness in result.existing_weaknesses:

        print("-", weakness)

    print("\nSummary:")
    print(result.summary)

    print("====================================")

    return result


# Run good response test
good_result = print_analysis(
    "TEST 1: GOOD RESPONSE",
    good_evaluation
)

# Run poor response test
poor_result = print_analysis(
    "TEST 2: POOR RESPONSE",
    poor_evaluation
)


# =====================================
# ASSERTIONS
# =====================================

assert good_result.needs_deeper_analysis is False

assert good_result.analysis_status == "satisfactory"

assert poor_result.needs_deeper_analysis is True

assert poor_result.analysis_status == "needs_deeper_analysis"

print("\nAll Phase 5A tests passed!")
