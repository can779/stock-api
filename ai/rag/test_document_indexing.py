from ai.rag.vector_store import add_document_file


file_path = "ai/rag/documents/stok_politikasi.txt"


chunk_count = add_document_file(
    file_path
)


print(
    f"Doküman başarıyla indexlendi. "
    f"Chunk sayısı: {chunk_count}"
)