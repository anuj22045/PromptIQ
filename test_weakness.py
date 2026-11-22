from weakness.analyzer import analyze_deeper_weaknesses
from weakness.analyzer import analyze_weaknesses

from weakness.analyzer import refine_prompt
from weakness.analyzer import regenerate_response


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




# =====================================
# PHASE 5B - TESTING
# =====================================

def test_deeper_analysis(title, prompt, response, evaluation):

    print("\n====================================")
    print(title)
    print("====================================")

    # Phase 5A: Identify potential weaknesses
    phase5a_result = analyze_weaknesses(evaluation)

    # Phase 5B: Verify weaknesses using Groq
    result = analyze_deeper_weaknesses(
        prompt=prompt,
        response=response,
        phase5a_result=phase5a_result
    )

    print("\nOverall Status:")
    print(result.overall_status)

    print("\nNeeds Refinement:")
    print(result.needs_refinement)

    print("\nRequirement Checks:")
    for item in result.requirement_checks:
        print(f"- {item.requirement}: {item.status}")
        print(f"  Reason: {item.explanation}")

    print("\nIdentified Weaknesses:")
    for weakness in result.identified_weaknesses:
        print("-", weakness)

    print("\nMissing Requirements:")
    for requirement in result.missing_requirements:
        print("-", requirement)

    print("\nRecommendations:")
    for recommendation in result.recommendations:
        print("-", recommendation)

    print("\nSummary:")
    print(result.summary)

    return result


# =====================================
# TEST 3: GOOD RESPONSE
# =====================================

good_prompt = "Explain RAG with a practical example."

good_response = """
RAG stands for Retrieval-Augmented Generation.

It retrieves relevant information from external
sources and uses that information to generate
a more informed response.

Example:
A student asks a university chatbot about
admission fees.

The chatbot retrieves the fee information
from university documents and generates
an answer using that information.
"""

good_5b_result = test_deeper_analysis(
    "TEST 3: GOOD RESPONSE",
    good_prompt,
    good_response,
    good_evaluation
)

assert good_5b_result.overall_status == "satisfactory"
assert good_5b_result.needs_refinement is False
assert good_5b_result.identified_weaknesses == []
assert good_5b_result.missing_requirements == []


# =====================================
# TEST 4: MISSING PRACTICAL EXAMPLE
# =====================================

poor_prompt = "Explain RAG with a practical example."

poor_response = """
RAG stands for Retrieval-Augmented Generation.

It combines information retrieval with
large language models to generate answers.
"""

poor_5b_result = test_deeper_analysis(
    "TEST 4: MISSING PRACTICAL EXAMPLE",
    poor_prompt,
    poor_response,
    poor_evaluation
)

assert poor_5b_result.overall_status == "needs_improvement"

assert len(poor_5b_result.missing_requirements) > 0

assert len(poor_5b_result.recommendations) > 0


# =====================================
# TEST 5: UNNECESSARY WEAKNESS
# =====================================

# The evaluators reported a missing example,
# but the user never requested an example.

simple_prompt = "What is RAG?"

simple_response = """
RAG stands for Retrieval-Augmented Generation.

It is an AI technique that retrieves relevant
information from external sources and uses
that information to help a language model
generate more informed answers.
"""

unnecessary_5b_result = test_deeper_analysis(
    "TEST 5: UNNECESSARY WEAKNESS",
    simple_prompt,
    simple_response,
    poor_evaluation
)

assert unnecessary_5b_result.overall_status == "satisfactory"

assert unnecessary_5b_result.needs_refinement is False

assert unnecessary_5b_result.missing_requirements == []

assert unnecessary_5b_result.recommendations == []


print("\nAll Phase 5B tests passed!")



# ==========================================
# PHASE 6A - TESTING
# ==========================================

# TEST 6: PROMPT DOES NOT NEED REFINEMENT

result = refine_prompt(
    prompt="What is RAG?",
    response="RAG stands for Retrieval-Augmented Generation.",
    deeper_result={
        "needs_refinement": False,
        "overall_status": "satisfactory",
        "identified_weaknesses": [],
        "missing_requirements": [],
        "recommendations": []
    }
)

print("\nTEST 6: NO REFINEMENT NEEDED")
print(result)

assert result["was_refined"] is False
assert result["refined_prompt"] == "What is RAG?"


# TEST 7: PROMPT REFINEMENT REQUIRED

result = refine_prompt(
    prompt="Explain Python for beginners.",
    response="Python is a programming language.",
    deeper_result={
        "needs_refinement": True,
        "overall_status": "needs_improvement",
        "identified_weaknesses": [
            "The prompt does not specify the intended scope."
        ],
        "missing_requirements": [],
        "recommendations": [
            "Clarify the intended scope without adding new topics."
        ]
    }
)

print("\nTEST 7: REFINEMENT REQUIRED")
print(result)

assert result["refined_prompt"].strip() != ""
assert result["reason"].strip() != ""

print("\nAll Phase 6A tests passed!")



# ==========================================
# PHASE 6B - TESTING
# ==========================================

# TEST 8: NO REGENERATION REQUIRED

no_regeneration = regenerate_response({
    "was_refined": False,
    "original_prompt": "What is Python?",
    "refined_prompt": "What is Python?",
    "reason": "Prompt is already clear."
})

print("\nTEST 8: NO REGENERATION REQUIRED")
print(no_regeneration)

assert no_regeneration["was_regenerated"] is False
assert no_regeneration["new_response"] is None


# ==========================================
# TEST 9: REGENERATE RESPONSE
# ==========================================

refinement_data = {
    "was_refined": True,
    "original_prompt": "Explain Python for beginners.",
    "refined_prompt": (
        "Explain Python for beginners, covering "
        "essential concepts and basic syntax."
    ),
    "reason": "Clarified the intended scope."
}

regeneration_result = regenerate_response(refinement_data)

print("\nTEST 9: REGENERATE RESPONSE")
print("Was Regenerated:", regeneration_result["was_regenerated"])
print("Original Prompt:", regeneration_result["original_prompt"])
print("Refined Prompt:", regeneration_result["refined_prompt"])
print("New Response:\n", regeneration_result["new_response"])

assert regeneration_result["was_regenerated"] is True
assert regeneration_result["new_response"] is not None
assert regeneration_result["new_response"].strip() != ""

print("\nAll Phase 6B tests passed!")
