# Agentic Workflows for Research & Briefing

## What makes a system "agentic"
A classic RAG answers in one shot: retrieve → generate.
An agentic system goes further: it plans and orchestrates multiple steps (tools) to reach a goal.

## Research briefing as an agentic task
Goal: produce a 1-page briefing grounded in sources.
A robust plan often looks like:
1) Collect sources (local docs, seed URLs, or web search)
2) Extract content (PDF parsing, HTML to text)
3) Filter & clean (dedup, injection filtering, PII redaction)
4) Index/Upsert (chunks + metadata)
5) Retrieve (hybrid + rerank)
6) Draft briefing (with citations)
7) Verify (quality gate: citation coverage, diversity)
8) Export artifacts (Markdown, PDF, JSON trace)

## Tooling philosophy
Tools should be small, deterministic, and testable:
- fetch_url(url) -> raw content
- parse_pdf(path) -> text
- upsert(docs) -> stored chunks
- retrieve(query) -> evidence chunks
- generate(topic, evidence) -> draft
- verify(draft, evidence) -> pass/fail

## Memory (optional but useful)
Memory is not “chat history”; it’s structured state:
- preferred briefing format
- tracked entities/topics
- glossary
- past briefings + diffs (“what changed since last week?”)

## Why enterprises like this
- Repeatable outputs
- Auditability (traces + citations)
- Ability to plug into workflows (alerts, tickets, dashboards)
