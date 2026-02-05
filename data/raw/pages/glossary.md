# Glossary (RAG & Agentic AI)

- **Chunking**: splitting long docs into smaller passages for retrieval.
- **Overlap**: repeated tokens between chunks to avoid cutting facts in half.
- **BM25**: classic lexical retrieval ranking based on term matches.
- **Dense retrieval**: semantic retrieval using embeddings and vector search.
- **Hybrid retrieval**: combining BM25 + dense retrieval to improve recall.
- **Reranking**: re-ordering candidates with a stronger model (e.g., cross-encoder).
- **Citations**: references to evidence passages used to justify claims.
- **Abstention**: refusing to answer when evidence is insufficient.
- **Prompt injection**: malicious text inside docs trying to hijack the model.
- **Guardrails**: safety checks (PII redaction, injection filtering, refusal policy).
- **Observability**: traces/logs/metrics to debug and monitor the pipeline.
- **Agentic**: a system that plans and calls tools to complete multi-step tasks.
