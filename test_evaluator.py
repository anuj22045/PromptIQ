from evaluation.evaluator import evaluate_response

prompt="Explain RAG in AI with a practical Example"

response = """
RAG stands for Retrieval-Augmented Generation.
It combines information retrieval with text generation.

It retrieves relevant information from external sources
and uses that information to generate responses.
"""

context = """
RAG retrieves relevant information from an external
knowledge source and provides that information to an
LLM as context before generating an answer.
"""


reference_answer = """
RAG combines information retrieval and text generation.
It retrieves relevant information from an external
knowledge source and uses it to generate grounded answers.
"""

result = evaluate_response(
    prompt=prompt,
    response = response,
    reference_answer = reference_answer,
    context = context

)

# Display evaluation results
print("\n========== PROMPTIQ EVALUATION ==========\n")

print(result.model_dump_json(indent=4))

print("\nOverall Score:", result.overall_score)

print("\nEvaluation Summary:")
print(result.summary)