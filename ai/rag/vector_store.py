import chromadb

from ai.rag.embeddings import create_embedding
from ai.rag.chunking import chunk_text
from ai.rag.documents import load_text_file
from ai.rag.pdf_loader import load_pdf_file

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="company_documents"
)


def add_document(
    document_id: str,
    text: str
):
    embedding = create_embedding(text)

    collection.add(
        ids=[document_id],
        embeddings=[embedding],
        documents=[text]
    )


def add_document_file(
    file_path: str
):
    text = load_text_file(file_path)

    chunks = chunk_text(
        text,
        chunk_size=50,
        overlap=10
    )

    for index, chunk in enumerate(chunks):

        embedding = create_embedding(chunk)

        collection.add(
            ids=[f"{file_path}_{index}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[
                {
                    "source": file_path,
                    "chunk_id": index
                }
            ]
        )

    return len(chunks)

def add_pdf_file(
    file_path: str
):
    text = load_pdf_file(file_path)

    chunks = chunk_text(
        text,
        chunk_size=50,
        overlap=10
    )

    for index, chunk in enumerate(chunks):

        embedding = create_embedding(chunk)

        collection.add(
            ids=[f"pdf_{file_path}_{index}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[
                {
                    "source": file_path,
                    "chunk_id": index,
                    "file_type": "pdf"
                }
            ]
        )

    return len(chunks)


def search_documents(
    query: str,
    n_results: int = 2
):
    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results