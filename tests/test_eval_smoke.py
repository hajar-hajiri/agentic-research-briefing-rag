from core.eval import _score

def test_eval_scoring_smoke():
    sc = _score("Hello [1].", distinct_sources=2, min_sources=2)
    assert sc["has_citations"] is True
    assert sc["source_diversity_ok"] is True
