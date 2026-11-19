# Model Card

## Limitations or biases

The system uses lexical cosine retrieval and extractive summarization, not an internet or domain-specific language model. It may miss relevant passages with different wording, use repetitive source sentences in summaries, or confidently misrank weak evidence. Custom documents are stored locally and no user text leaves the application.

## Misuse and prevention

The assistant could be used to present weak retrieved text as authoritative, or to add misleading documents to the local knowledge base. The UI labels confidence, shows source passages, rejects empty input, and returns a no-evidence answer for unsupported queries. Users should review sources and should not use the output for high-stakes decisions without independent verification.

## Reliability surprises

Testing showed that the retriever can distinguish direct matching text but intentionally returns no evidence for unrelated wording. The system also treats no evidence as lower confidence instead of fabricating a result. Human review is still required because lexical similarity is not semantic understanding.

## Human evaluation

| Test input | Evaluation criterion | Result |
|---|---|---|
| "Summarize this article" with pasted text | Clear summary under three sentences | Pass |
| "How should I debug a failing Python test?" | Relevant retrieval and reproducible debug steps | Pass |
| "Retrieve the price of a secret planet" | Graceful no-evidence response | Pass |
| Empty request | Handles gracefully without execution | Pass |
