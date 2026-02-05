# Evaluation Metrics for RAG / Agentic RAG

## Why evaluation is necessary
RAG systems can regress easily:
- chunking changes
- retriever changes
- embeddings model changes
- prompt changes
A small evaluation harness protects your system.

## Practical metrics (lightweight)
### 1) Citation coverage
Does the answer include citations [1], [2], ... for important claims?

### 2) Source diversity
Is the answer grounded in multiple distinct sources?
A simple gate: >= 2 distinct sources unless abstained.

### 3) Abstention correctness
If evidence is weak or missing, does the system abstain?
You want “safe failures”.

### 4) Retrieval diagnostics
- number of retrieved chunks
- overlap / redundancy
- top source dominance (one source used too much)

### 5) Latency and cost (optional)
Track time per stage: collect, retrieve, rerank, write, verify.

## “Good enough” eval for a PFE
- 30–100 topics/questions in JSONL
- automatic checks: citations present, diversity ok
- store report to JSON
- run in CI so regressions fail the build
