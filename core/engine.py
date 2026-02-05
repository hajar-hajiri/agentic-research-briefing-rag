from __future__ import annotations
from dataclasses import dataclass

from core.config import Settings
from core.observability import Tracer, write_run
from core.guardrails import quality_gate
from core.llm import (
    LLMRequest, NoLLM, OpenAIResponsesLLM, OllamaLLM,
    BRIEFING_SYSTEM, BRIEFING_TEMPLATE
)
from core.rag import build_chunks, HybridRetriever, make_citations, distinct_sources, Chunk

@dataclass
class RunResult:
    answer: str
    retrieved: list[Chunk]
    trace_path: str | None = None

def _build_llm(s: Settings):
    if s.llm_provider == "openai":
        if not s.openai_api_key:
            return NoLLM()
        return OpenAIResponsesLLM(s.openai_api_key, s.openai_model)
    if s.llm_provider == "ollama":
        return OllamaLLM(s.ollama_base_url, s.ollama_model)
    return NoLLM()

class Engine:
    def __init__(self, settings: Settings | None = None):
        self.s = settings or Settings()
        self.llm = _build_llm(self.s)

    def run(self, topic: str, mode: str = "offline", urls: list[str] | None = None) -> RunResult:
        tracer = Tracer(topic)

        with tracer.span("collect"):
            chunks = build_chunks(self.s.data_raw_pdfs, self.s.data_raw_pages, mode, urls)
            tracer.meta["num_chunks"] = len(chunks)

        with tracer.span("retrieve"):
            retriever = HybridRetriever(chunks, rerank=self.s.rerank)
            retrieved = retriever.search(topic, bm25_k=self.s.bm25_k, dense_k=self.s.dense_k, top_k=self.s.top_k)
            tracer.meta["distinct_sources"] = len(distinct_sources(retrieved))

        with tracer.span("write"):
            cites = make_citations(retrieved, max_citations=self.s.max_citations)
            evidence = "\n".join(
                f"[{c.idx}] {c.title} — {c.source}\nExcerpt: {c.excerpt}\n" for c in cites
            )
            req = LLMRequest(system=BRIEFING_SYSTEM, prompt=BRIEFING_TEMPLATE.format(topic=topic, evidence=evidence))
            answer = self.llm.generate(req)

        with tracer.span("quality_gate"):
            sources = distinct_sources(retrieved)
            q = quality_gate(answer, sources, min_sources=self.s.min_distinct_sources)
            tracer.meta["quality_ok"] = q.ok
            tracer.meta["quality_reason"] = q.reason
            if not q.ok:
                answer = (
                    f"# Briefing — {topic}\n\n"
                    f"**Abstained**: {q.reason}\n\n"
                    f"Try adding more sources or switching to online mode.\n"
                )

        trace = tracer.finish()
        trace_path = write_run(trace, self.s.data_runs)
        return RunResult(answer=answer, retrieved=retrieved, trace_path=trace_path)
