def chunk_text(
    text: str,
    chunk_size: int = 300,
    overlap: int = 50
):
    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        chunk_words = words[
            start:start + chunk_size
        ]

        chunk = " ".join(chunk_words)

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks