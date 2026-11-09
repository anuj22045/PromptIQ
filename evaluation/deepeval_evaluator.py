# GroqDeepEvalModel is an adapter that connects your Groq LLM with DeepEval so DeepEval can use Groq to evaluate responses.
# it will communicate with Groq to evaluate the prompt and response

import json
import asyncio

from groq import Groq
from pydantic import BaseModel
from deepeval.models import DeepEvalBaseLLM
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from config.settings import GROQ_API_KEY, GROQ_MODEL

class GroqDeepEvalModel(DeepEvalBaseLLM):

    def __init__(self):
        self.client = Groq(api_key = GROQ_API_KEY)
        self.model_name = GROQ_MODEL

    def load_model(self):
        return self.client

    def get_model_name(self):
        return self.model_name

    def generate(self, prompt:str, schema: BaseModel=None):
        client = self.load_model()

        request_args = {
            "model" : self.model_name,
            "messages": [
                {
                    "role":"user",
                    "content":prompt
                }
            ],
            "temperature":0
        }

        if schema is not None:
            request_args["response_format"] = {
                "type" : "json_object"
            }

        response = client.chat.completions.create(
            **request_args
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError("Groq returned an empty response")

        if schema is None:
            return content

        try:
            data = json.loads(content)  #json into pydantic object 
            return schema.model_validate(data)

        except Exception as e:
            raise ValueError(f"DeepEval structured output error: {e}")

    async def a_generate(self, prompt:str, schema : BaseModel=None):
        return await asyncio.to_thread(
            self.generate, prompt, schema
        )

groq_judge = GroqDeepEvalModel()

answer_relevancy = GEval(
    name="Answer Relevancy",

    criteria="""
    Evaluate whether the generated response
    directly addresses the user's original prompt.

    Reward responses that stay focused on the question.
    Penalize unrelated or irrelevant information.
    """,

    evaluation_params=[
        SingleTurnParams.INPUT,
        SingleTurnParams.ACTUAL_OUTPUT
    ],

    model = groq_judge,
    threshold=0.7,
    async_mode = False
)


clarity = GEval(
    name="Clarity",

    criteria="""
        Evaluate whether the generated response is clear,
        understandable and well-structured.

        Check:
        1. Language simplicity.
        2. Logical flow.
        3. Readability.
        4. Proper sentence construction.
        5. Clear transitions between ideas.
        6. Whether the response ends naturally.

        Penalize unfinished sentences, abrupt cutoffs
        and confusing explanations.

        Do not penalize missing subject matter details
        under clarity; evaluate those under completeness.
    """,

    evaluation_params=[
        SingleTurnParams.ACTUAL_OUTPUT
    ],
    model = groq_judge,
    threshold=0.7,
    async_mode=False
)


completeness = GEval(
    name="completeness",

    criteria="""
    Evaluate whether the generated response covers
    all the important requirements of the user's prompt.

    Identify missing information, missing examples,
    and unexpected concepts requested by the user.
    """,

    evaluation_params=[
        SingleTurnParams.INPUT,
        SingleTurnParams.ACTUAL_OUTPUT
    ],

    model = groq_judge,
    threshold=0.7,  #specifies the passing score.
    async_mode=False #keeps our first implementation sequential and easier to debug.
)

DEEPEVAL_METRICS = [
    answer_relevancy,
    clarity,
    completeness

]

# Create the evaluation function

def evaluate_with_deepeval(prompt:str, response:str)->str:
    if not prompt or not prompt.strip():
        raise ValueError("prompt cannot be empty")

    if not response or not response.strip():
        raise ValueError("response cannot be empty")

    test_case = LLMTestCase(
        input= prompt,
        actual_output = response
    )

    results= {}

    for metric in DEEPEVAL_METRICS:
        metric.measure(test_case)

        results[metric.name] = {
            "score":round(metric.score, 4),
            "score_out_of_10": round(metric.score * 10, 2),
            "reason": metric.reason,
            "passed": metric.is_successful()
        }

    return results
