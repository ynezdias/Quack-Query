"""Start QuackQuery with the current interpreter and ready document indexes."""
import argparse
import os
import subprocess
import sys

from dotenv import load_dotenv
from src.ingest import prepare_corpus, ingest_documents
from src.knowledge import CORPORA, ROOT, CHROMA_DIR, read_manifest
from src.embeddings import MODEL_NAME


def ensure_index(corpus):
    current = read_manifest().get(corpus, {})
    inventory = prepare_corpus(corpus)[3]
    ready = current.get("embedding_model") == MODEL_NAME and current.get("documents") == inventory
    if ready:
        import chromadb
        from chromadb.errors import InvalidCollectionException
        try:
            collection = chromadb.PersistentClient(path=str(CHROMA_DIR)).get_collection(current["collection"])
            ready = collection.count() == current.get("chunks") and collection.count() > 0
        except (InvalidCollectionException, KeyError):
            ready = False
    if not ready:
        ingest_documents(corpus)


def main():
    load_dotenv(ROOT / ".env")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535")
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key or key == "replace-with-your-key":
        raise SystemExit("Set GROQ_API_KEY in the project's .env before starting QuackQuery.")
    selected = os.getenv("QUACKQUERY_CORPUS", "").strip()
    if selected and selected not in CORPORA:
        raise SystemExit("Invalid QUACKQUERY_CORPUS")
    for corpus in (selected,) if selected else CORPORA:
        ensure_index(corpus)
        print(f"Ready: {corpus}", flush=True)
    command = [sys.executable, "-m", "streamlit", "run", str(ROOT / "app.py"),
               f"--server.address={args.host}", f"--server.port={args.port}",
               "--server.headless=true", "--browser.gatherUsageStats=false"]
    try:
        return subprocess.run(command, cwd=str(ROOT)).returncode
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
