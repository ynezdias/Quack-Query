# Source and conversation handling

The synthetic folder contains fictional test data supplied with explicit provenance
labels. It is kept separate from the original five PDFs, whose authenticity has
not been verified. Adding a filename to the inventory does not certify its contents.
Do not move synthetic documents into the unverified corpus to imply authenticity.

Index metadata records source paths, SHA-256 hashes, source type, extraction
locations, and explicitly labeled publication dates. It does not infer academic
years or effective dates from publication dates. DOCX has no stable page locator.
The active manifest stores the inventory used for a snapshot. The checked-in CSV
is a point-in-time inventory and should be regenerated when source files change.

Queries, recent conversation turns, and selected excerpts are sent to Groq for
answer generation. Do not put private student records in this portfolio demo.
Conversation history is stored only in Streamlit session state, is separate per
corpus, and is not written to a conversation database. Clearing a conversation
clears that session's retained messages; it does not control provider-side data
retention. No question/answer text is intentionally included in application metrics.

The source download control verifies the current file's content hash against the
indexed metadata. If the file changed, the UI retains the indexed text for evidence
inspection but does not offer the mismatching file as the original source.

Index builds are published only on success. Previous collections are retained
for recovery and need explicit cleanup; source removal excludes a document from
the new active snapshot but does not erase prior snapshots or repository history.
