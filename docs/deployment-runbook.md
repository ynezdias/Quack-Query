# Deployment runbook

## Local development

Use Python 3.11. Create a virtual environment, install `requirements.txt`, and
copy `.env.example` to `.env` only if no `.env` exists. Set your own Groq key.
Never commit `.env`. `GROQ_MODEL` can override the default model.

```powershell
python -m pip install -r requirements.txt
python -m src.ingest --corpus synthetic
python -m src.ingest --corpus unverified
.\run.ps1
# Alternatively: python -m src.serve --host 127.0.0.1 --port 8502
```

The launcher uses the project virtual environment, loads .env from the project root,
and checks or rebuilds each exposed document index. Open http://localhost:8502.
Run it from a normal terminal with internet access: a restricted runner can serve
the UI while blocking outbound Groq requests.

The first model load downloads weights into `.cache/`. After downloading,
set `HF_HUB_OFFLINE=1` when you need to run without Hugging Face network access.
Groq access is still required to generate answers.

## Container

```powershell
docker compose up --build -d
docker compose ps
docker compose logs --tail 100
```

Open http://localhost:8501. Compose binds to localhost by default and requires
a local `.env`. The image excludes secrets, virtual environments, Git metadata,
and local indexes. It runs as an unprivileged user, downloads a CPU embedding
model at build time, and indexes the selected corpus at startup. The named
volume preserves the manifest and Chroma data across container replacement.

`QUACKQUERY_CORPUS` selects the single corpus exposed by the container UI.
The default is the synthetic demo. Change it to `unverified` to use the original
PDFs; neither corpus is verified official guidance.

Health: `/_stcore/health` checks the Streamlit server. Startup indexing must
succeed before the server starts. Health does not check Groq availability.

For public hosting, use a single container with a persistent volume behind
HTTPS and an ingress rate limit. The in-app allowance defaults to 30 completed questions per minute per browser
session (configure QUACKQUERY_REQUESTS_PER_MINUTE from 1 to 600). Failed provider
requests and citation-validation failures do not consume this allowance. Provider
rate limits are separate; the app honors Retry-After and preserves conversation
history. The session allowance is not an abuse-prevention boundary. Configure provider
spending limits. The app has no user accounts and must not host private student
records. Choose a hosting provider and domain separately; this repository does
not create or publish cloud resources.

## Update and recover

Replace or add documents, rebuild the image, and recreate the container.
Startup compares source inventories and rebuilds when they change. Back up the
named volume before a release. Retain the prior image tag for rollback; restore
the volume backup and prior image together if necessary. Old collections remain
available until explicitly cleaned up. Do not run two ingestion writers at once.

## Troubleshooting

- Model-not-found: choose an available model in Groq and set `GROQ_MODEL`.
- Missing API key: set `GROQ_API_KEY` at runtime, never in the Dockerfile.
- Index not ready: run ingestion for the selected corpus and inspect logs.
- Verification failure: the app makes one correction attempt with the same
  retrieved sources. If citations still fail validation, it withholds the claims;
  inspect the source and try a more specific question.
- Empty scanned PDF: OCR is not implemented; provide a text-based source.

## Git hygiene

`.venv`, `venv`, `.cache`, `chroma_db`, and `.env` are ignored. The formerly
tracked `.venv` files were removed from the Git index with `git rm --cached`;
local environment files remain. This stages their removal for the next commit.
It does not rewrite prior Git history. No commit or push is performed automatically.

## Verification record

Local Streamlit startup and the HTTP health endpoint passed. Unit/UI tests and
dependency consistency checks passed. The initial Docker build was interrupted
when the local Docker engine disconnected during dependency installation. A
second build attempt failed the same way, so the image build and container
runtime remain unverified on this machine. Restore a stable Docker engine, then
run `docker compose up --build -d` and check its health. CI configuration is present but has not been run
on GitHub because these changes have not been pushed by this assistant.

CI runs unit/UI tests, indexes the synthetic corpus, and checks that hybrid
all-sources@3 remains at least 95% on the regression set. It uploads the evaluation
report as an artifact. CI does not call Groq or require an API key.

## Docker storage blocker found during retry

C: had no free space, and Docker returned filesystem I/O errors while reading
its image store and installing dependencies. Clearing approximately 1.1 GB of
pip download cache left only 0.97 GB free; Docker continued returning HTTP 500
errors while restarting. Free several more GB on C: (aim for 5-10 GB of headroom),
then restart Docker Desktop and retry the Compose command. D: had 32.27 GB free,
so relocating Docker storage is another option requiring a deliberate migration.
Do not factory-reset Docker or delete its disk image as a routine fix: that can
remove existing images and volumes. No reset or storage migration was performed.

## Backend recovery verification (2026-10-02)

The failing local server was running with outbound sockets restricted (WinError
10013), even though its HTTP health endpoint worked. Restarting it with network
access restored Groq-backed answers. Failed requests now leave the session
allowance unchanged; the default allowance is 30 completed questions per minute.
Provider Retry-After cooldowns and one bounded evidence-correction attempt are
covered by regression tests. Citation checks still reject unsupported quotations.

All 44 unit/UI/startup tests passed, pip check reported no broken requirements,
and the running HTTP health endpoint returned 200. Live browser checks confirmed
answers with citations from synthetic, reviewed-source, and original PDF
collections, an international-applicant follow-up, refusal of a personal student
ID question, original-file download controls, and official-source links. A broad
PDF question initially failed quotation checks and then safely returned unknown
on correction. These are smoke checks, not a complete answer-quality benchmark.
Docker packaging now includes presentation.py; the container build remains
unverified as described above.
