import json
from core.llm_client import generate_chat_response
from ambiguity.schemas import AmbiguityResult

AMBIGUITY_SYSTEM_PROMPT="""
You are an expert Prompt Ambiguity Detection Engine.

Your task is to analyze the user's prompt and identify
whether it has multiple reasonable interpretations.

IMPORTANT RULES:

1. Identify genuinely ambiguous words, phrases,
    abbreviations and missing contextual meanings.

2. Generate up to 4 reasonable interpretations.

3. Do not invent unlikely or unrelated meanings.

4. Consider the surrounding context before deciding
    that a prompt is ambiguous.

5. Do not classify a prompt as ambiguous simply
    because it is short or lacks detailed instructions.

6. Distinguish between:
    - Ambiguity: Multiple possible meanings.
    - Underspecification: The meaning is clear, but
        some details are missing.
    - Unambiguous: The intended meaning is sufficiently clear.

7. Ask for clarification only when different reasonable
    interpretations would substantially change the answer.

8. If a reasonable default interpretation can answer
    the prompt, do not unnecessarily interrupt the user.

9. If the prompt is genuinely ambiguous:
    - Set is_ambiguous to true.
    - Set needs_clarification to true when clarification
        is necessary.
    - List the possible interpretations.
    - Generate a clear clarification question.

10. If clarification is not required:
    - Set needs_clarification to false.
    - Return an empty interpretations list unless
            mentioning alternatives is genuinely useful.
    - Set clarification_question to null.

11. Use the conversation context if it is supplied.
    Do not assume technical context without evidence.

12. Return ONLY valid JSON.

Use this exact JSON structure:

{
    "is_ambiguous": true,
    "needs_clarification": true,
    "ambiguity_level": "high",
    "possible_interpretations": [
        {
            "title": "Interpretation 1",
            "description": "Description of meaning"
        }
    ],
    "clarification_question": "What do you mean?",
    "reason": "Explanation of ambiguity"
}

For unambiguous prompts, use:

{
    "is_ambiguous": false,
    "needs_clarification": false,
    "ambiguity_level": "none",
    "possible_interpretations": [],
    "clarification_question": null,
    "reason": "The intended meaning is sufficiently clear."
}

Return a JSON object only.
"""


def detect_ambiguity(prompt:str, conversation_context: str=None)->AmbiguityResult:
    if not prompt or not prompt.strip():
        raise ValueError("prompt cannot be empty")

    input_data={
        "user_prompt":prompt,
        "conversation_context": conversation_context
    }

    messages = [
        {
            "role": "system",
            "content": AMBIGUITY_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": json.dumps(input_data)
        }
    ]


    detector_output = generate_chat_response(
        messages = messages,
        temperature=0,
        max_completion_tokens=1000,
        json_mode = True
    )

    try:
        result = AmbiguityResult.model_validate_json(
            detector_output
        )
        return result
    except Exception as e:
        raise ValueError(f"failed to process ambiguity detection {e}")



# The following happens:
# 1. The function receives the user's prompt.
# 2. It validates that the prompt isn't empty.
# 3. It prepares the system instructions.
# 4. It sends the prompt to Groq.
# 5. Groq identifies possible interpretations.
# 6. It returns JSON.
# 7. Pydantic validates the JSON.
# 8. We receive an AmbiguityResult object.