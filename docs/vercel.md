# Vercel deployment

QuackQuery uses Vercel's beta container runtime and WebSocket support to preserve its Streamlit interface and retrieval pipeline. Vercel detects `Dockerfile.vercel` at the repository root.

The image installs CPU-only PyTorch, downloads the embedding model, and builds all three document collections. No Groq credential is needed during the build. At startup, `src.container_start` copies the baked Chroma index into `/tmp/quackquery-index`, then starts the existing server. The local index location remains unchanged unless `QUACKQUERY_INDEX_DIR` is set.

Set these project environment variables for production and preview:

- `PORT=8501`
- `GROQ_API_KEY`: an encrypted secret supplied by the account owner

Deploy with `vercel deploy --prod` after linking the project. `.vercelignore` and `.dockerignore` exclude credentials, local environments, cached authentication, and the local database from deployment uploads.

The Vercel image uses inline source downloads so document links do not depend on another container instance's in-memory Streamlit media registry. Source path containment and content-hash checks still apply.

Streamlit conversation history and throttling are per session, not durable account storage. Vercel can terminate or reconnect WebSockets at the plan's function-duration limit; a new instance may start a fresh conversation. Container indexes are disposable copies of the built snapshot, not an upload database. Updating documents requires rebuilding the deployment.

Verify a deployment's health endpoint (`/_stcore/health`), browser connection, supported answer with citations, unknown-answer behavior, source downloads, and mobile layout before reporting it ready.

Platform references: [container images](https://vercel.com/docs/functions/container-images), [WebSockets](https://vercel.com/docs/functions/websockets).

## Production verification — October 2, 2026

Production URL: https://quackquery-seven.vercel.app

The deployed application returned HTTP 200 from its health endpoint and connected successfully in Microsoft Edge. Live checks passed for synthetic admissions answers with citations, unknown personal information, the reviewed CS 583 prerequisite with its official source link, and an answer from the original International Students FAQ PDF. DOCX and PDF source downloads succeeded. The mobile layout at 390 pixels had no horizontal overflow. Local checks passed: 46 tests.

The Groq key was configured as an encrypted production/preview environment variable with the account owner's explicit permission. It is excluded from source uploads and container images. Git-based automatic deployment is not connected; Vercel requested a GitHub login connection. CLI production deployment works independently.
