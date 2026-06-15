import sys
from app.rag.ingestion import ingest_folder

if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "docs"
    ingest_folder(folder)
