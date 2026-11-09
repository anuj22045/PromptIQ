from core.response_generator import generate_llm_response

prompt="Explain RAG in simple words"

response = generate_llm_response(prompt)

print("Generated Response:")
print(response)