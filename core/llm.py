from __future__ import annotations
from dataclasses import dataclass
import json, requests

BRIEFING_SYSTEM = """You are a research assistant that produces short, evidence-grounded briefings.
Rules:
- Do not claim facts not supported by provided evidence snippets.
- Every important statement must include citations like [1], [2].
- If evidence is insufficient, say what is missing and abstain.
"""

BRIEFING_TEMPLATE = """Topic: {topic}

Evidence snippets:
{evidence}

Write a 1-page briefing in Markdown with:
# Briefing — {topic}
## Executive summary
## Key points
## Metrics / signals (only if present)
## Risks & uncertainties
## Opportunities / next actions
## Sources
"""

@dataclass(frozen=True)
class LLMRequest:
    system: str
    prompt: str

class LLM:
    def generate(self, req: LLMRequest) -> str:
        raise NotImplementedError

class NoLLM(LLM):
    def generate(self, req: LLMRequest) -> str:
        return (
            "# Briefing\n\n"
            "Evidence-only mode (no LLM configured).\n"
            "Set LLM_PROVIDER and credentials in .env.\n\n"
            + req.prompt
        )

class OpenAIResponsesLLM(LLM):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate(self, req: LLMRequest) -> str:
        payload = {"model": self.model, "input": f"{req.system}\n\n{req.prompt}"}
        r = requests.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=90,
        )
        r.raise_for_status()
        data = r.json()
        out = ""
        for item in data.get("output", []):
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    out += c.get("text", "")
        return out.strip()

class OllamaLLM(LLM):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(self, req: LLMRequest) -> str:
        r = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": f"{req.system}\n\n{req.prompt}", "stream": False},
            timeout=120,
        )
        r.raise_for_status()
        return r.json().get("response", "").strip()
