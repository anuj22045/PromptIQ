from ambiguity.schemas import AmbiguityResult, ClarificationResolution

def resolve_intent(original_prompt: str, ambiguity_result: AmbiguityResult, selected_interpretation: str, custom_intent: str = None)-> ClarificationResolution:
    if not original_prompt or not original_prompt.strip():
        raise ValueError("prompt cannot be empty")

    if not ambiguity_result.needs_clarification:
        raise ValueError("this prompt does not need clarification")

    if selected_interpretation == "something else":
        if not custom_intent or not custom_intent.strip():
            raise ValueError("please specify your intended meaning")
        selected_intent = custom_intent.strip()
        intent_description = (
            "Meaning specified directly by the user"
        )
    else:
        selected_option = next(
            (
                option
                for option in ambiguity_result.possible_interpretations
                if option.title == selected_interpretation
            ),
        None
    )

    if selected_option is None:
        raise ValueError("Invalid Interpretation selected.")
    selected_intent = selected_option.title
    intent_description = selected_option.description

    clarified_prompt = f"""
    Original User prompt :{original_prompt.strip()}

    Clarification Provided By User: 
    The intended meaning is: {selected_intent}.

    Meaning:
    {intent_description}

    Instructions:
    Answer the original user request using the selected
    interpretation. Do not change the original user's
    requirements or introduce unrelated assumptions.

    """
    return ClarificationResolution(
        original_prompt=original_prompt.strip(),
        selected_intent=selected_intent,
        intent_description=intent_description,
        clarified_prompt=clarified_prompt.strip()
    )