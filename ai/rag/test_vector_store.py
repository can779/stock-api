from ai.rag.vector_store import add_document


add_document(
    "doc_1",
    "Telefon kategorisindeki ürünlerin minimum stok seviyesi 15 adettir."
)

add_document(
    "doc_2",
    "Bilgisayar kategorisindeki ürünlerin minimum stok seviyesi 5 adettir."
)

add_document(
    "doc_3",
    "Kırtasiye ürünlerinde minimum stok seviyesi 20 adettir."
)

print("Dokümanlar ChromaDB'ye eklendi.")