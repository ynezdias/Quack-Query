# Measured results

Recorded on 2026-09-16 using the supplied synthetic corpus (20 documents).
Raw reports preserve the corpus hashes and active index snapshot. The final
answer run also records the model, pacing, and `src/rag.py` hash.

## Held-out retrieval comparison

Seventeen answerable questions; six unsupported/ambiguous questions have no
positive source labels and are excluded from retrieval denominators.
Both methods use the same index and embedding model.

| Metric | Semantic | Hybrid (BM25 + semantic RRF) |
|---|---:|---:|
| All expected sources in top 3 | 16/17 (94.1%) | 17/17 (100%) |
| Mean source recall@3 | 97.1% | 100% |
| MRR@3 | 0.775 | 0.873 |
| Literal evidence coverage@3 | 100% | 100% |
| Mean warmed retrieval latency | 28.0 ms | 26.5 ms |

See [raw retrieval results](../eval/test-results.json). Latencies are local
measurements and depend on hardware and concurrent load.

## Live answer regression

Default model: `openai/gpt-oss-20b` through Groq. Twenty-three questions:
17 answerable, four unsupported, two ambiguous. Generation receives three
retrieved chunks in this evaluation; the UI currently retrieves eight.

| Run | Expected response type matched | Provider errors |
|---|---:|---:|
| Initial JSON-object run | 13/23 (56.5%) | 6 rate-limit errors |
| Strict schema, paced requests | 18/23 (78.3%) | 0 |
| Final missing-information policy | 23/23 (100%) | 0 |

Final literal required-fact match: **13/17** answerable questions.
This substring metric can reject correct paraphrases and cannot establish
semantic correctness. All final answered responses passed citation-ID and
verbatim-quotation checks; that does not prove that every claim follows from
its quote. Status accuracy measures whether the app answers, abstains, or asks
for clarification as labeled, not whether every answer is factually correct.

The schema and missing-information policy were revised after inspecting the
initial failures. The final generation result is therefore a regression result
on inspected questions, not an independent held-out generalization score.
Retrieval was not retuned on the held-out questions. The labels were authored
from the synthetic documents and still need independent review and expansion
with real, verified sources.

Raw reports:
- [Initial run](../eval/answer-results.json)
- [Paced schema run](../eval/answer-results-paced.json)
- [Final regression run](../eval/answer-results-final.json)
- [Evaluation protocol](../eval/README.md)

## Engineering verification

- 18 unit and Streamlit UI tests passed.
- Python compilation and dependency consistency checks passed.
- Local Streamlit HTTP health endpoint returned `ok`.
- Startup reused the unchanged synthetic index.
- Git no longer tracks `.venv`; local environment files remain. Removals are staged.
- Compose and CI YAML parsed successfully. CI has not been executed on GitHub.
- Docker build verification is **blocked**: the retry exposed filesystem I/O
  errors in both package installation and Docker's image store. Windows C: had
  zero free bytes. Clearing 1.1 GB of disposable pip downloads left about 0.97 GB
  free, but Docker continued returning HTTP 500 errors during restart. No images,
  volumes, installed packages, or project files were deleted. More host disk space
  and a healthy Docker engine are needed before retrying. No completed image,
  container health result, or public deployment is claimed.

The portfolio implementation is ready for local review. Restore a stable Docker
engine and complete a container smoke test before deploying it publicly.
