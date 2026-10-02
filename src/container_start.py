"""Copy the baked document index into writable storage and start Streamlit."""
import os
from pathlib import Path
import shutil
import sys


def main():
    target = Path(os.environ.get("QUACKQUERY_INDEX_DIR", "/tmp/quackquery-index"))
    if not (target / "quackquery.json").exists():
        shutil.copytree("/app/chroma_db", target, dirs_exist_ok=True)
    port = int(os.environ.get("PORT", "8501"))
    if not 1 <= port <= 65535:
        raise ValueError("PORT must be between 1 and 65535")
    os.execv(sys.executable, [sys.executable, "-m", "src.serve", "--port", str(port)])


if __name__ == "__main__":
    main()
