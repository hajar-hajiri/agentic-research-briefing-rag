from __future__ import annotations
import json, re
from dataclasses import dataclass
from pathlib import Path

from core.engine import Engine

CITE = re.compile(r"\[(\d+)\]")

@dataclass(frozen=True)
class EvalCase:
    id: str
    topic: str
    mode: str = "offline"
    urls: list[str] | None = None
    min_sources: int = 2
    must_cite: bool = True

def _load_cases(path: str) -> list[EvalCase]:
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        out.append(EvalCase(**json.loads(line)))
    return out

def _score(answer_md: str, distinct_sources: int, min_sources: int):
    cites = set(int(m.group(1)) for m in CITE.finditer(answer_md))
    abstained = "**Abstained**" in answer_md or "Abstained:" in answer_md
    return {
        "has_citations": len(cites) > 0,
        "n_citations": len(cites),
        "source_diversity_ok": distinct_sources >= min_sources,
        "n_sources": distinct_sources,
        "abstained": abstained,
    }

def main():
    cases = _load_cases("core/dataset.jsonl")
    eng = Engine()

    results = []
    failed = 0

    for c in cases:
        run = eng.run(c.topic, mode=c.mode, urls=c.urls)
        n_sources = len({ch.source for ch in run.retrieved})
        sc = _score(run.answer, n_sources, c.min_sources)

        ok = True
        if c.must_cite and (not sc["has_citations"]) and (not sc["abstained"]):
            ok = False
        if (not sc["source_diversity_ok"]) and (not sc["abstained"]):
            ok = False

        results.append({"id": c.id, "topic": c.topic, "ok": ok, "scores": sc, "trace": run.trace_path})
        if not ok:
            failed += 1

    out_dir = Path("data/eval")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "latest.json"
    out_path.write_text(json.dumps({"failed": failed, "results": results}, indent=2), encoding="utf-8")
    print(f"Eval done. Failed: {failed}/{len(results)}. Report: {out_path}")

    if failed > 0:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
