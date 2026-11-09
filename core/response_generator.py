from core.llm_client import generate_response


def generate_llm_response(prompt: str) ->str:
    """
    Generates a LLM response for the given user prompt
    """

    if not prompt or not prompt.strip():
        raise ValueError("prompt cannot be empty")

    try:
        response = generate_response(prompt)
        return response

    except Exception as e:
        raise RuntimeError(f"Failed to generate response: {str(e)}")


#ye application layer pe kaam krta h jaise 
# Validates the user prompt.
# Calls generate_response().
# Handles generation-related errors.
# Returns the final response to the application.