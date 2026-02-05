from fastapi import FastAPI
from pydantic import BaseModel
from core.engine import Engine

app = FastAPI(title="Agentic Research Briefing RAG")
engine = Engine()

class BriefingRequest(BaseModel):
    topic: str
    mode: str = "offline"
    urls: list[str] = []

@app.post("/briefing")
def briefing(req: BriefingRequest):
    run = engine.run(req.topic, mode=req.mode, urls=req.urls or None)
    return {
        "topic": req.topic,
        "mode": req.mode,
        "answer_md": run.answer,
        "trace_path": run.trace_path,
    }
