from ai.rag.embeddings import create_embedding
from ai.rag.similarity import cosine_similarity


text_a = "Telefon ürünlerinin minimum stok seviyesi 15 adettir."

text_b = "Telefonların stok seviyesi en az 15 olmalıdır."

text_c = "Bugün hava sıcaklığı 30 derece."


embedding_a = create_embedding(text_a)
embedding_b = create_embedding(text_b)
embedding_c = create_embedding(text_c)


similarity_ab = cosine_similarity(
    embedding_a,
    embedding_b
)

similarity_ac = cosine_similarity(
    embedding_a,
    embedding_c
)


print("A ↔ B benzerliği:")
print(similarity_ab)

print("\nA ↔ C benzerliği:")
print(similarity_ac)