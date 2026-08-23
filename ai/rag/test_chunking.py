from ai.rag.chunking import chunk_text


text = """
Şirketimiz stok yönetiminde üç temel prensip kullanır.

Minimum stok seviyesi ürün kategorisine göre belirlenir.

Telefon ürünlerinde minimum stok seviyesi 15 adettir.

Bilgisayar ürünlerinde minimum stok seviyesi 5 adettir.

Yeniden sipariş süreci minimum seviyenin altına
düşüldüğünde başlatılır.
"""


chunks = chunk_text(
    text,
    chunk_size=20,
    overlap=5
)


print("Chunk sayısı:")
print(len(chunks))


for i, chunk in enumerate(chunks, start=1):

    print(f"\n--- CHUNK {i} ---")
    print(chunk)