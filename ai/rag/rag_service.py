from ai.rag.vector_store import search_documents
from ai.llm_service import ask_llm


def answer_with_rag(
    question: str
):

    try:

        results = search_documents(
            question,
            n_results=2
        )

    except Exception as e:

        print(
            "RAG search hatası:",
            e
        )

        return (
            "Bilgi arama sistemi şu anda "
            "kullanılamıyor."
        )

    # -----------------------------------------------------
    # SEARCH SONUCU KONTROLÜ
    # -----------------------------------------------------

    if not results:
        return (
            "Bu bilgi dokümanda bulunmamaktadır."
        )

    documents = results.get(
        "documents",
        [[]]
    )

    metadatas = results.get(
        "metadatas",
        [[]]
    )

    if not documents or not documents[0]:
        return (
            "Bu bilgi dokümanda bulunmamaktadır."
        )

    documents = documents[0]

    if metadatas and metadatas[0]:
        metadatas = metadatas[0]
    else:
        metadatas = [{} for _ in documents]

    # -----------------------------------------------------
    # CONTEXT OLUŞTUR
    # -----------------------------------------------------

    context_parts = []

    for document, metadata in zip(
        documents,
        metadatas
    ):

        context_parts.append(
            f"""
KAYNAK: {metadata.get("source", "Bilinmiyor")}
CHUNK: {metadata.get("chunk_id", "Bilinmiyor")}

İÇERİK:
{document}
"""
        )

    context = "\n\n".join(
        context_parts
    )

    # -----------------------------------------------------
    # LLM PROMPT
    # -----------------------------------------------------

    prompt = f"""
Aşağıdaki dokümanları kullanarak soruyu cevapla.

DOKÜMANLAR:

{context}

SORU:

{question}

Kurallar:

1. Cevap dokümanlarda varsa sadece
   dokümanlardaki bilgileri kullan.

2. Cevap dokümanlarda yoksa:

"Bu bilgi dokümanda bulunmamaktadır."

de.

3. Bilgi uydurma.

4. Cevabı Türkçe ver.
"""

    try:

        return ask_llm(
            prompt
        )

    except Exception as e:

        print(
            "RAG LLM hatası:",
            e
        )

        return (
            "Dokümanlardan cevap oluşturulurken "
            "bir hata oluştu."
        )