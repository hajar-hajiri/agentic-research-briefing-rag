# RAG Overview (Retrieval-Augmented Generation)

## What RAG is
Retrieval-Augmented Generation (RAG) is a pattern where a language model answers using external knowledge retrieved at query time. Instead of relying only on model parameters, a RAG system:
1) retrieves relevant passages from a knowledge base
2) provides those passages as evidence to the model
3) generates an answer grounded in the evidence

## Typical pipeline
- Ingest documents (PDF, HTML, Markdown, etc.)
- Chunk into passages (with overlap)
- Build indexes:
  - Sparse (BM25 / lexical)
  - Dense (embeddings / vector search)
- Retrieve top candidates (hybrid is common)
- Rerank candidates (cross-encoder or LLM-based)
- Generate answer with citations and a refusal policy when evidence is missing

## Failure modes
- Hallucinations (claims with no evidence)
- Retrieval misses (wrong chunks, bad chunking, weak query formulation)
- Prompt injection (malicious instructions inside documents)
- Stale data (for time-sensitive topics)
- Overconfident answers (no abstention/uncertainty)

## Why citations matter
Citations make a RAG system auditable. A strong rule is:
- “No evidence → no claim”
- “No citations → abstain”

## What “good” looks like in production
- Measured quality (eval + regression tests)
- Observability (traces, latency, cost)
- Guardrails (injection, PII, refusals)
- Robust retrieval (hybrid + rerank)
