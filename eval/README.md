# Evaluation protocol

`questions.json` contains 32 manually specified cases grounded in the supplied
synthetic documents: 9 development cases and 23 held-out test cases (17 answerable,
4 unsupported, 2 ambiguous). Expected sources are filenames; required facts are
literal evidence fragments. These labels should receive independent review
before making any broader accuracy claim.

```powershell
python -m src.evaluate --split development --output eval/development-results.json
python -m src.evaluate --split test --output eval/test-results.json
python -m src.evaluate --split test --answers --output eval/answer-results.json
```

Retrieval evaluation requires the synthetic index and downloaded embedding model,
but no Groq key. `--answers` additionally sends synthetic excerpts to Groq and
incurs API usage, paced at 20-second intervals by default (`--delay` overrides this). It evaluates hybrid answers only, while still comparing both
retrieval methods. The evaluation uses three chunks; the interactive app uses
eight. The reports are an experiment at k=3, not a claim about all app answers.

Metrics:
- Source recall@3: fraction of expected source documents retrieved.
- All-sources@3: fraction of questions retrieving every labeled source.
- MRR@3: reciprocal rank of the first expected source.
- Evidence coverage@3: fraction of literal required evidence fragments present.
- Retrieval latency: warmed model/database; local wall-clock measurements.
- Status accuracy: generated answered/unknown/clarify matches expected behavior.
- Required-fact match: strict substring check on answers; not semantic correctness.

Unsupported and ambiguous cases have no positive retrieval label and are excluded
from retrieval metric denominators. They are included in generation status accuracy.
Provider errors and validation failures count against status accuracy. Citation
validation verifies IDs and verbatim quotes, not whether the claim follows logically.
No LLM judge is used. Model nondeterminism and provider changes can alter results.

Hybrid search was implemented before looking at the held-out results and was not
tuned on them. The small, synthetic, author-labeled set is a portfolio demonstration;
add independently reviewed real-document cases before asserting production quality.

The first live generation run is retained in `answer-results.json`, including rate-limit errors. `answer-results-paced.json` records a subsequent run with strict schemas and pacing; because these reliability changes followed inspection of the test failures, that run is a regression measurement, not a fresh unseen benchmark. Retrieval was not retuned.

`answer-results-final.json` is the final regression run after making missing-information handling take priority over clarification. It records the hash of `src/rag.py`. Treat it as a regression run on previously inspected questions, not an independent test of generalization. The original held-out retrieval comparison remains separate.

## Expanded benchmark

See [EXPANDED.md](EXPANDED.md) for the separate 75-case regression suite, reviewed official-source corpus, reproduction commands and limitations. The original reports above remain historical baselines.
