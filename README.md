# QuackQuery

A portfolio AI application for answering university-document questions with
inspectable evidence, isolated corpora, hybrid retrieval, and measured evaluation.

## Implemented

- Recursive PDF/DOCX ingestion with document hashes and atomic index publication.
- Separate synthetic-demo, original/unverified, and reviewed official-source knowledge bases.
- Shared semantic embeddings plus BM25 search combined with reciprocal-rank fusion.
- Structured answers, citation-ID validation, and matching evidence quotations.
- Expandable evidence panels and original-document downloads.
- Session conversation history, follow-up context, corpus isolation, and clear-history control.
- Bounded inputs/history, per-session request limits, provider timeouts, and safe error handling.
- The original 32-question benchmark plus a 75-question expanded regression suite, including 20 official-source cases.
- Docker/Compose deployment configuration, persistent index volume, health check, and CI.

## Run locally

Use Python 3.11 and a virtual environment. Install `requirements.txt`, configure
`GROQ_API_KEY` in `.env`, then run:

```powershell
python -m src.ingest --corpus synthetic
python -m src.ingest --corpus unverified
python -m streamlit run app.py
```

The default Groq model is `openai/gpt-oss-20b`; override it with `GROQ_MODEL`.
The first model load downloads `all-MiniLM-L6-v2` into `.cache/`.
Use `python -m src.ingest --dry-run` to inspect extraction without downloading weights.

The supplied 20 DOCX documents are fictional test data, not official university
policies. The five original PDFs are marked unverified. Same-name PDF/DOCX pairs
use the PDF. Synthetic files must stay under folders containing `synthetic`.

## Evaluate and test

```powershell
python -m unittest discover -s tests -v
python -m src.evaluate --split test --output eval/test-results.json
python -m src.evaluate --split test --answers --output eval/answer-results-paced.json
```

Answer evaluation calls Groq and uses 20-second pacing by default. Evaluation
measures retrieval at three chunks; the interactive app uses eight. Read the
[protocol](eval/README.md) and [results](docs/results.md) before interpreting scores.

## Deployment

```powershell
docker compose up --build -d
```

Compose requires `.env` and exposes http://localhost:8501. It persists the index
in a named volume. Read the [runbook](docs/deployment-runbook.md) before public hosting.
No public deployment or Git push has been performed.

## Design and limitations

See [architecture](docs/architecture.md). Citation checks prove that a quotation
exists in the selected source, not that the answer logically follows from it.
Conflict reasoning is model-based. Conversation references use a simple heuristic.
The small synthetic evaluation cannot establish real-world factual accuracy.
OCR, cross-encoder reranking, accounts, private student records, and multi-replica
operation are not implemented. Prior index snapshots are retained for recovery.

## License

See [LICENSE](LICENSE).

## Expanded university evaluation

The [expanded benchmark](eval/expanded_questions.json) includes all 55 proposed
questions and 20 cases grounded in five reviewed summaries of official Stevens
pages. Choose **Reviewed university sources** in the app to query these separately
from fictional policies. These are dated, assistant-reviewed factual summaries,
not independently verified copies of complete university documents.

```powershell
.venv/Scripts/python.exe -m src.ingest --corpus verified
.venv/Scripts/python.exe -m src.evaluate_expanded --top-k 3 --output eval/expanded-retrieval-results.json
.venv/Scripts/python.exe -m src.evaluate_expanded --answers --output eval/expanded-full-answers.json
```

The last command calls Groq for all 75 questions, paced 20 seconds apart, and
uses the app's eight-chunk context. See [the expanded evaluation report](eval/EXPANDED.md)
for measured results, source provenance and limits. Earlier benchmark results remain unchanged.
