import re
from dataclasses import dataclass

INJECTION_PATTERNS = [
    r"ignore (all|previous) instructions",
    r"system prompt",
    r"developer message",
    r"do not follow",
    r"you are now",
    r"exfiltrate",
]

EMAIL = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
IBAN = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b", re.I)

CITE = re.compile(r"\[(\d+)\]")

def is_injection(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in INJECTION_PATTERNS)

def redact_pii(text: str) -> str:
    text = EMAIL.sub("[REDACTED_EMAIL]", text)
    text = PHONE.sub("[REDACTED_PHONE]", text)
    text = IBAN.sub("[REDACTED_IBAN]", text)
    return text

@dataclass(frozen=True)
class QualityResult:
    ok: bool
    reason: str

def quality_gate(answer_md: str, sources: set[str], min_sources: int) -> QualityResult:
    if len(sources) < min_sources:
        return QualityResult(False, "Insufficient source diversity.")
    cites = set(int(m.group(1)) for m in CITE.finditer(answer_md))
    if not cites:
        return QualityResult(False, "No citations found in answer.")
    if len(answer_md) > 800 and len(cites) < 2:
        return QualityResult(False, "Not enough citations for the answer length.")
    return QualityResult(True, "OK")
