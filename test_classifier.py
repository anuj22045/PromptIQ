
from ambiguity.schemas import (
    AmbiguityResult,
    Interpretation
)

from ambiguity.clarifier import resolve_intent


# Simulated Phase 4A output
ambiguity_result = AmbiguityResult(

    is_ambiguous=True,

    needs_clarification=True,

    ambiguity_level="high",

    possible_interpretations=[

        Interpretation(
            title="Machine Learning",
            description=(
                "A subfield of AI where algorithms "
                "learn patterns from data."
            )
        ),

        Interpretation(
            title="Milliliter",
            description=(
                "A unit of volume equal to one "
                "thousandth of a liter."
            )
        ),

        Interpretation(
            title="Maximum Likelihood",
            description=(
                "A statistical method for estimating "
                "model parameters."
            )
        )
    ],

    clarification_question=(
        "Which meaning of ML are you referring to?"
    ),

    reason=(
        "ML has multiple possible meanings."
    )
)


# Original user prompt
original_prompt = "What is ML?"


# Simulate user's selection
selected_interpretation = "Machine Learning"


# Resolve user intent
result = resolve_intent(
    original_prompt=original_prompt,
    ambiguity_result=ambiguity_result,
    selected_interpretation=selected_interpretation
)


# Display results
print("\n========== INTENT RESOLUTION ==========\n")

print("Original Prompt:")
print(result.original_prompt)

print("\nSelected Intent:")
print(result.selected_intent)

print("\nIntent Description:")
print(result.intent_description)

print("\nClarified Prompt:")
print(result.clarified_prompt)

print("\n=======================================")
