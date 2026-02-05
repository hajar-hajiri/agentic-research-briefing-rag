from core.rag import Chunk, HybridRetriever

def test_hybrid_retriever_smoke():
    chunks = [
        Chunk("c1","d1","s1","t1","agentic ai enterprise trends"),
        Chunk("c2","d2","s2","t2","cyber resilience and incident response"),
        Chunk("c3","d3","s3","t3","product metrics north star framework"),
    ]
    r = HybridRetriever(chunks, rerank=False)
    out = r.search("agentic ai", bm25_k=3, dense_k=3, top_k=2)
    assert len(out) == 2
