from ai.rag.embeddings import create_embedding


text = "Telefon ürünlerinin minimum stok seviyesi 15 adettir."

embedding = create_embedding(text)

print("Embedding boyutu:")
print(len(embedding))

print("\nİlk 10 değer:")
print(embedding[:10])