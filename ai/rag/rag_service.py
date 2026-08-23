from ai.rag.vector_store import search_documents
from ai.llm_service import ask_llm


def answer_with_rag(
    question: str
):
    results = search_documents(
        question,
        n_results=2
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context_parts = []

    for document, metadata in zip(
        documents,
        metadatas
    ):
        context_parts.append(
            f"""
KAYNAK: {metadata["source"]}
CHUNK: {metadata["chunk_id"]}

İÇERİK:
{document}
"""
        )

    context = "\n\n".join(
        context_parts
    )

    prompt = f"""
Aşağıdaki dokümanları kullanarak soruyu cevapla.

DOKÜMANLAR:
{context}

SORU:
{question}

Eğer cevap dokümanlarda varsa sadece dokümanlardaki
bilgileri kullan.

Eğer cevap dokümanlarda yoksa:
"Bu bilgi dokümanda bulunmamaktadır."
de.

Cevabı Türkçe ver.
"""

    return ask_llm(prompt)