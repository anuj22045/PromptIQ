
from evaluation.deepeval_evaluator import evaluate_with_deepeval


# prompt = """
# Explain Retrieval-Augmented Generation (RAG)
# in AI with a practical example.
# """
prompt = """
Explain photosynthesis to a 10-year-old student.

Include:
1. What photosynthesis means.
2. Why sunlight is required.
3. How plants use water and carbon dioxide.
4. The main steps involved.
5. A simple real-world example.
"""
response = """
Plants do food. Sun is there and green things happen.
Water maybe goes inside and air is used somehow.

Photosynthesis is something plants do.
It is important because plants are plants.
"""
# response = """
# RAG stands for Retrieval-Augmented Generation.

# It combines information retrieval with text generation.

# It retrieves relevant information from an external
# knowledge source and provides that information to
# an LLM to generate an answer.

# For example, a user can upload a company policy PDF
# and ask questions about its leave policy. RAG retrieves
# the relevant information from the PDF and uses it
# to generate an answer.
# """


# Evaluate response using DeepEval
results = evaluate_with_deepeval(
    prompt=prompt,
    response=response
)


print("\n========== DEEPEVAL RESULTS ==========\n")

for metric, details in results.items():

    print(f"\nMetric: {metric}")
    print(f"Score: {details['score']}")
    print(f"Score out of 10: {details['score_out_of_10']}")
    print(f"Reason: {details['reason']}")
    print(f"Passed: {details['passed']}")

print("\n======================================")
