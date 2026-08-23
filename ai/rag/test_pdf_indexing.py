from ai.rag.vector_store import add_pdf_file


file_path = "ai/rag/documents/stok_politikasi.pdf"


chunk_count = add_pdf_file(
    file_path
)


print(
    f"PDF başarıyla indexlendi. "
    f"Chunk sayısı: {chunk_count}"
)