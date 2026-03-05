from app.rag.retriever import ingest_chunks, make_chunks_from_text

TEXT = """
A data warehouse is a central repository of integrated data from various sources.
It stores current and historical data used for reporting and analysis.
The warehouse typically includes fact tables and dimension tables.
"""

if __name__ == "__main__":
    chunks = make_chunks_from_text(TEXT, source="sample_docs")
    ingest_chunks(chunks)
    print(f"Ingested {len(chunks)} chunks into Qdrant.")
