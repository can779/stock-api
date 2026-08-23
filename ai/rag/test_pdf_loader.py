from ai.rag.pdf_loader import load_pdf_file


file_path = "ai/rag/documents/stok_politikasi.pdf"


text = load_pdf_file(file_path)


print("PDF'DEN OKUNAN METİN:")
print(text)