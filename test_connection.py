from core.llm_client import generate_response

prompt="Explain RAG in simple words?"

response = generate_response(prompt)

print("\n Promot: ")
print(prompt)

print("\n Response: ")
print(response)