from ai.rag.documents import load_text_file


text = load_text_file(
    "ai/rag/documents/stok_politikasi.txt"
)

print(text)