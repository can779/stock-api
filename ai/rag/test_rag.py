from ai.rag.rag_service import answer_with_rag


question = "Telefonlarda minimum stok seviyesi kaç?"


answer = answer_with_rag(
    question
)


print("SORU:")
print(question)

print("\nRAG CEVABI:")
print(answer)