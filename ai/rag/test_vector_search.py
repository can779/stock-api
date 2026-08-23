from ai.rag.vector_store import search_documents


query = "Telefonlarda minimum stok seviyesi kaç?"


results = search_documents(
    query,
    n_results=2
)


print("Bulunan dokümanlar:\n")

for i, document in enumerate(
    results["documents"][0]
):

    metadata = results["metadatas"][0][i]

    print("METADATA:", metadata)

    print(f"--- SONUÇ {i + 1} ---")

    print("Doküman:")
    print(document)

    print("\nKaynak:")
    print(metadata["source"])

    print("Chunk ID:")
    print(metadata["chunk_id"])

    print()