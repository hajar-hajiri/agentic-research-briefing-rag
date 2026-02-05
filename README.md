# Agentic Research & Briefing RAG (Compact, Reproducible)

A clean, reproducible **agentic RAG** system that produces a 1-page research briefing grounded in evidence.
It is designed as an engineering project (not a chatbot wrapper): clear separation of concerns, guardrails,
structured traces, and an evaluation harness that can run in CI.

---

## Installation guide

### 1) Create venv and install
```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -U pip
pip install -e ".[dev]"
```
### 2) Configuration .env (local)
Create your local configuration file:
```bat
copy .env.example .env
```
### 3) LLM Setup (No OpenAI Key)

If you don't have an OpenAI API key, you can still run this project in two clean ways:


#### Option 1 — No LLM (runs the full pipeline, but no real generation)

This mode still runs the full engineering pipeline:
**ingestion → chunking → retrieval → citations → guardrails → traces → eval**  
but the “briefing generation” step will run in **evidence-only mode** (no real LLM output).

In your `.env`:
```txt
LLM_PROVIDER=none
```
#### Option 2 — Local LLM with Ollama (recommended for real generation)

This option enables real text generation entirely locally (no cloud key required).

a) Install Ollama (Windows)

Install Ollama on Windows (desktop app).

b) Download a model

Open a terminal and run:
```bat
ollama pull llama3.1
```

c) Configure the project

In your .env:
```txt
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```
### 4) Add documents (offline knowledge base)

Put your files here:

- **PDFs:** `data\raw\pdfs\`
- **Local pages:** `data\raw\pages\` (`.md`, `.txt`, `.html`)

Check that the folders are not empty:

```bat
dir data\raw\pdfs
dir data\raw\pages
```
If these folders are empty, the system may abstain or run with very limited output.

### 5) Run the Streamlit UI

Start the Streamlit app:

```bat
streamlit run app\streamlit_app.py
```
Open the URL printed in the terminal (usually):

- http://localhost:8501
### 6) Run tests and evaluation harness 
```bat
pytest -q
python -m core.eval
```
Output report:

- `data\eval\latest.json`


---

## What this project does

Given a **topic** (e.g., *“Agentic AI Trends”*), the system:

1. **Collects knowledge** from local sources:
   - PDFs in `data/raw/pdfs/`
   - local pages (`.md`, `.txt`, `.html`) in `data/raw/pages/`
   - optionally: seed URLs in “online mode” (fetch → parse → index)
2. **Chunks** documents into passages.
3. **Retrieves evidence** using **hybrid retrieval**:
   - **BM25** (lexical matching)
   - **Dense retrieval** (embeddings + FAISS)
   - **Fusion** (Reciprocal Rank Fusion)
   - Optional **reranking** (cross-encoder)
4. **Generates a briefing** using an LLM (OpenAI or Ollama), with **citations** `[1] [2] ...`.
5. Applies a **quality gate**:
   - If citations are missing or evidence diversity is insufficient → the system **abstains**.
6. Saves **run artifacts** (traces) to disk for auditability and debugging.

---

## Why “Agentic” here?

In this repo, “agentic” is not marketing: the system is built as a deterministic pipeline that orchestrates tools:

- Collect → Retrieve → Write → Verify
- Each stage is isolated and traced (latency + metadata)
- Guardrails enforce “evidence-first” behavior

This provides the same *engineering benefits* you expect from agent systems:
reproducibility, debuggability, safe failure modes, and modular upgrades.

---

## Repository layout (compact core)

The project is intentionally compact while keeping strong boundaries:

- `core/engine.py`  
  Orchestrates the end-to-end run (collect → retrieve → write → verify), produces run artifacts.
- `core/rag.py`  
  Ingestion + chunking + hybrid retrieval (BM25 + dense + fusion) + optional rerank + citations.
- `core/llm.py`  
  LLM providers (OpenAI / Ollama / none) and prompts.
- `core/guardrails.py`  
  Prompt-injection filtering, PII redaction, and the quality gate.
- `core/observability.py`  
  Structured tracing (spans) + JSON/JSONL run logging.
- `core/eval.py` + `core/dataset.jsonl`  
  Lightweight evaluation harness to prevent regressions (also runs in CI).

UI and API:
- `app/streamlit_app.py` → Streamlit demo UI  
- `api/main.py` → FastAPI endpoint (`/briefing`)

---

## Data (Offline mode)

This repo is designed to run offline against local documents:

- Put PDFs in: `data/raw/pdfs/`
- Put local pages in: `data/raw/pages/` (`.md`, `.txt`, `.html`)

This repository can ship with a few small open-access PDFs so it runs out of the box.
You can replace them with your own local documents at any time.

> Tip: keep PDFs reasonably small for faster indexing on CPU.

---

## Guardrails (safety & reliability)

### 1) Prompt injection filtering
Documents containing typical instruction-hijacking patterns are filtered out before indexing.

### 2) PII redaction
Simple redaction is applied to emails / phone numbers / IBAN-like strings to avoid leakage into outputs.

### 3) Quality gate (“no evidence → no claim”)
After generation, the output must satisfy:
- citations exist (`[1]`, `[2]`, …)
- minimum distinct sources is met (configurable)
- otherwise the system returns an **abstention** response

This is crucial in real-world RAG deployments where hallucinations are unacceptable.

---

## Observability (run artifacts)

Each run writes a trace file to `data/runs/`:

- `data/runs/<run_id>.json` : detailed spans, timings, metadata
- `data/runs/runs.jsonl` : append-only log for quick analysis

This makes your system auditable and easy to debug.

---

## Evaluation harness (CI-ready)

`core/eval.py` runs a small dataset of topics defined in `core/dataset.jsonl`.
It checks:
- citation presence (unless abstained)
- source diversity (unless abstained)

Output:
- `data/eval/latest.json`

GitHub Actions CI runs:
- lint (ruff)
- tests (pytest)
- eval (`python -m core.eval`)

---

