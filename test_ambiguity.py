
from ambiguity.detector import detect_ambiguity


# Test prompts
test_prompts = [
    "What is ML?",
    "What is DL",
    "What is Java?"
]


for prompt in test_prompts:

    print("\n====================================")
    print("USER PROMPT:", prompt)

    result = detect_ambiguity(prompt)

    print("\nAMBIGUITY DETECTED:", result.is_ambiguous)

    print("NEEDS CLARIFICATION:", result.needs_clarification)

    print("AMBIGUITY LEVEL:", result.ambiguity_level)

    print("\nPOSSIBLE INTERPRETATIONS:")

    for interpretation in result.possible_interpretations:

        print("-", interpretation.title)
        print("  ", interpretation.description)

    print("\nCLARIFICATION QUESTION:")
    print(result.clarification_question)

    print("\nREASON:")
    print(result.reason)

    print("====================================")
