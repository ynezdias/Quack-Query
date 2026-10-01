"""One embedding configuration for both indexing and retrieval."""
import os
from functools import lru_cache
from pathlib import Path

for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(name, "1")

os.environ.setdefault("HF_HOME", str(Path(__file__).resolve().parents[1] / ".cache" / "huggingface"))

os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_encoder():
    from sentence_transformers import SentenceTransformer
    cache_folder = str(Path(__file__).resolve().parents[1] / ".cache" / "models")
    try:
        # A warm installation must not wait on Hub update checks or retries.
        return SentenceTransformer(MODEL_NAME, cache_folder=cache_folder, local_files_only=True)
    except OSError:
        # First-time setup can still download a model that is not cached yet.
        return SentenceTransformer(MODEL_NAME, cache_folder=cache_folder)


def embed_batch(texts):
    return get_encoder().encode(texts, normalize_embeddings=True, batch_size=8).tolist()


def embed(text):
    return embed_batch([text])[0]
