# Expanded university regression benchmark

## Scope and provenance

`expanded_questions.json` contains 75 cases: S001-S055 preserve the user's
55 questions; V001-V020 cover official-source facts. Each case specifies corpus,
category, expected status, labeled reference sources, and an answer-review rubric.
S008 and S042 intentionally overlap because both were supplied; counts are not
independent samples. These cases are regression checks, not an unseen test set.

The five files in `data/verified` are assistant-reviewed factual summaries from
four official pages, checked September 17, 2026:

- [Graduate application requirements](https://www.stevens.edu/application-requirements)
- [Tuition and fees](https://www.stevens.edu/page-chapter/tuition-and-fees), separate 2025-2026 and 2026-2027 graduate sections
- [Registrar important dates](https://www.stevens.edu/page-basic/registrar-important-dates), selected class-start/end dates only
- [Archived 2023-2024 CS 583](https://web.stevens.edu/catalog/archive/2023-2024/en/catalog/academic-catalog/courses/cs-computer-science/500/cs-583.html)

`sources.json` records URLs, review date, scope, verification method and local
summary hashes. Hashes detect local changes; they do not authenticate or snapshot
remote webpages. Summaries are not original documents or independently reviewed
gold labels. Unknown publication dates remain unknown. Archived requirements must
not be presented as current. Ingestion rejects changed hashes and non-allowlisted
source hosts. Application indexes keep reviewed, synthetic and unverified text separate.

Important label distinctions: CS 583 is mentioned in the synthetic 2025 handbook
but is not a sample core course; synthetic CS 583 allows an approved equivalent
to CS 559; eligibility never automatically guarantees an assistantship or housing.
The archived official prerequisite differs from the synthetic prerequisite.
S044 tests a request with unspecified conflicting documents; it does not prove
that the model resolves two contradictory same-year passages correctly.

## Reproduce

```powershell
$env:HF_HUB_OFFLINE='1' # after the embedding model has been cached
.venv/Scripts/python.exe -m unittest discover -s tests -q
.venv/Scripts/python.exe -m src.ingest --corpus verified
.venv/Scripts/python.exe -m src.evaluate_expanded --top-k 3 --output eval/expanded-retrieval-results.json
.venv/Scripts/python.exe -m src.evaluate_expanded --answers --ids S018,S025,S046,S052,V014,V018 --output eval/expanded-answer-smoke.json
.venv/Scripts/python.exe -m src.evaluate_expanded --answers --output eval/expanded-full-answers.json
```

Retrieval requires indexed corpora and the cached model, but no provider calls.
Answer runs require the configured Groq key, send public/synthetic excerpts, and
incur provider usage. Default pacing is 20 seconds between requests. Each completed
case saves an atomic report checkpoint. Reports include dataset/code hashes,
corpus inventories, actual top-k, model, per-category and per-corpus denominators.
A partial report has `completed_cases` below `case_count`; rerunning starts afresh.
Use `--ids` for targeted checks and a new output filename to retain prior reports.

## Retrieval measurements

All 75 cases ran with semantic and hybrid retrieval at k=3. Only cases with
labeled sources contribute to retrieval success metrics; unknown and clarification
cases do not receive free credit for an empty source set.

| Corpus | Answerable cases | Semantic all labeled sources | Hybrid all labeled sources |
|---|---:|---:|---:|
| Synthetic | 44 | 37/44 (84.1%) | 40/44 (90.9%) |
| Reviewed official summaries | 19 | 19/19 (100%) | 19/19 (100%) |

Synthetic average source recall: semantic 89.8%, hybrid 94.3%. Hybrid misses all-source
coverage on S011, S018, S022 and S042. In particular, the CS 583 question can retrieve
handbooks instead of the course catalog. These are findings for future retrieval work;
no labels or retrieval logic were changed to hide failures.

This measures presence of the chosen reference documents, not sufficient evidence
or answer correctness. Some questions have other valid supporting documents;
strict reference matching may penalize those. Duplicate chunks can occupy slots.
The reviewed corpus has only five chunks, making retrieval substantially easier
than a full university library. At the app's k=8 all five are available; perfect
source recall in that setting says little about ranking quality.

## Answer review

The six-case live smoke run uses k=8 and stores structured claims, quoted evidence,
and retrieved context for inspection. Status accuracy means only answered/unknown/
clarify matched the label. Quote validation checks source IDs and exact quote
existence, not whether the quote entails the claim. No automated factual-accuracy
percentage is claimed. Manual review should assess every factual clause, arithmetic,
units, year/program scope, omitted exceptions, and citation support.

The full 75-question live answer run is available through the command above but
is not implied by the full retrieval run. Next additions: independently review the
gold labels, ingest larger complete official documents with permission/provenance,
add controlled same-year contradictory evidence and adversarial instruction fixtures,
and score multi-turn answers and citation entailment. Official coverage currently
includes admissions, tuition, dates and one archived course, not housing/funding.

### Initial live findings

The initial six-case run produced three matching statuses, one incorrect status,
and two API connection errors. S018 correctly retained the approved-equivalent
exception; S025 calculated the $75 per-credit increase with quotations from both
years; S052 declined the absent CS 700 prerequisite. S046 returned `unknown`
instead of clarification, despite retrieving both calendars. This is a generation
failure, not a missing-calendar retrieval failure. V014 and V018 failed with
`APIConnectionError`; these are infrastructure failures, not factual answer errors.
A separate retry report retains the distinction from the initial run.

Both official-source cases succeeded on retry (2/2 expected statuses, zero API errors). Across the six selected questions using the retry for those two cases, five expected statuses matched and S046 still failed. This small smoke sample is not a 75-case answer-accuracy measurement. All 23 automated tests pass.
