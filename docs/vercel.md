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
