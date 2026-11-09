from groq import Groq
from config.settings import GROQ_API_KEY, GROQ_MODEL

client = Groq(api_key = GROQ_API_KEY)


def generate_chat_response(messages:list, temperature: float=0.2, max_completion_tokens: int=1200, json_mode: bool = False) ->str:

    request_args = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_completion_tokens": max_completion_tokens
    }

    if json_mode:
        request_args["response_format"] = {
            "type" : "json_object"
        }

    response = client.chat.completions.create(**request_args)

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("LLM returned an empty response")

    return content


def generate_response(prompt: str)->str:
    messages=[
        {
            "role":"user",
            "content":prompt
        }
    ]

    return generate_chat_response(
        messages, 
        temperature=0.7,
        max_completion_tokens=1500
    )


# generate_chat_response().

# accepts a list of messages rather than just a single prompt. 
# We also added JSON response mode, which will help our evaluator receive structured results.