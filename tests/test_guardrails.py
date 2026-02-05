from core.guardrails import redact_pii, quality_gate

def test_pii_redaction():
    s = "email test@example.com phone +33 6 12 34 56 78"
    out = redact_pii(s)
    assert "test@example.com" not in out

def test_quality_gate():
    q = quality_gate("Claim [1].", {"a", "b"}, min_sources=2)
    assert q.ok is True
    q2 = quality_gate("No cite.", {"a", "b"}, min_sources=2)
    assert q2.ok is False
