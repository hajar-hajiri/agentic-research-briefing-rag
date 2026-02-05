from __future__ import annotations
from dataclasses import dataclass, asdict
from time import perf_counter
from typing import Any, Dict, Optional, List
import json, os, time, uuid

@dataclass
class Span:
    name: str
    t0: float
    t1: float | None = None
    meta: Dict[str, Any] | None = None

@dataclass
class RunTrace:
    run_id: str
    topic: str
    spans: List[Span]
    meta: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class Tracer:
    def __init__(self, topic: str):
        self.run_id = str(uuid.uuid4())
        self.topic = topic
        self.spans: list[Span] = []
        self.meta: dict[str, Any] = {}

    def span(self, name: str, meta: Optional[dict[str, Any]] = None):
        tracer = self
        class _Ctx:
            def __enter__(self_inner):
                t0 = perf_counter()
                tracer.spans.append(Span(name=name, t0=t0, meta=meta or {}))
                return self_inner
            def __exit__(self_inner, exc_type, exc, tb):
                tracer.spans[-1].t1 = perf_counter()
                if exc:
                    tracer.spans[-1].meta = {**(tracer.spans[-1].meta or {}), "error": str(exc)}
        return _Ctx()

    def finish(self) -> RunTrace:
        return RunTrace(run_id=self.run_id, topic=self.topic, spans=self.spans, meta=self.meta)

def write_run(trace: RunTrace, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{trace.run_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trace.to_dict(), f, ensure_ascii=False, indent=2)

    jl = os.path.join(out_dir, "runs.jsonl")
    with open(jl, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": int(time.time()), **trace.to_dict()}, ensure_ascii=False) + "\n")
    return path
