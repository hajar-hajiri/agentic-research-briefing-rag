from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re

import fitz
import trafilatura
import requests

import numpy as np
import faiss
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder

from core.guardrails import is_injection, redact_pii

# ---------- data structures ----------

@dataclass(frozen=True)
class Doc:
    doc_id: str
    source: str
    title: str
    text: str
    kind: str  # pdf | page | web

@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    source: str
    title: str
    text: str

@dataclass(frozen=True)
class Citation:
    idx: int
    title: str
    source: str
    excerpt: str

# ---------- ingestion ----------

def load_pdfs(folder: str) -> list[Doc]:
    p = Path(folder)
    docs: list[Doc] = []
    for pdf in sorted(p.glob("*.pdf")):
        d = fitz.open(str(pdf))
        text = "\n".join(page.get_text("text") for page in d).strip()
        docs.append(Doc(
            doc_id=f"pdf::{pdf.name}", source=str(pdf), title=pdf.stem, text=text, kind="pdf"
        ))
    return docs

def load_local_pages(folder: str) -> list[Doc]:
    p = Path(folder)
    docs: list[Doc] = []
    for f in sorted(list(p.glob("*.txt")) + list(p.glob("*.md")) + list(p.glob("*.html"))):
        raw = f.read_text(encoding="utf-8", errors="ignore")
        extracted = trafilatura.extract(raw, include_tables=True) if f.suffix == ".html" else raw
        docs.append(Doc(
            doc_id=f"file::{f.name}", source=str(f), title=f.stem, text=(extracted or "").strip(), kind="page"
        ))
    return docs

def fetch_url(url: str, timeout: int = 20) -> Doc:
    r = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    extracted = trafilatura.extract(r.text, include_tables=True)
    return Doc(doc_id=f"url::{url}", source=url, title=url, text=(extracted or "").strip(), kind="web")

# ---------- chunking ----------

def chunk_doc(doc: Doc, size: int = 900, overlap: int = 120) -> list[Chunk]:
    t = re.sub(r"\s+", " ", doc.text).strip()
    if not t:
        return []
    out: list[Chunk] = []
    start, i = 0, 0
    while start < len(t):
        end = min(len(t), start + size)
        chunk_text = t[start:end].strip()
        if chunk_text:
            out.append(Chunk(
                chunk_id=f"{doc.doc_id}::chunk::{i}",
                doc_id=doc.doc_id,
                source=doc.source,
                title=doc.title,
                text=chunk_text,
            ))
            i += 1
        start = end - overlap if end - overlap > start else end
    return out

def make_citations(chunks: list[Chunk], max_citations: int) -> list[Citation]:
    cites: list[Citation] = []
    seen_sources = set()
    i = 1
    for ch in chunks:
        if ch.source in seen_sources:
            continue
        seen_sources.add(ch.source)
        excerpt = (ch.text[:260].strip() + "…") if len(ch.text) > 260 else ch.text
        cites.append(Citation(i, ch.title, ch.source, excerpt))
        i += 1
        if len(cites) >= max_citations:
            break
    return cites


# ---------- retrieval ----------

def rrf_fusion(a_ids: list[str], b_ids: list[str], k: int = 60) -> dict[str, float]:
    # Reciprocal Rank Fusion scores per id
    scores: dict[str, float] = {}
    for rank, cid in enumerate(a_ids, start=1):
        scores[cid] = scores.get(cid, 0.0) + (1.0 / (k + rank))
    for rank, cid in enumerate(b_ids, start=1):
        scores[cid] = scores.get(cid, 0.0) + (1.0 / (k + rank))
    return scores

class HybridRetriever:
    def __init__(
        self,
        chunks: list[Chunk],
        dense_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        rerank: bool = True,
        rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        self.chunks = chunks
        self.id2chunk = {c.chunk_id: c for c in chunks}

        # BM25
        self.tokens = [c.text.lower().split() for c in chunks]
        self.bm25 = BM25Okapi(self.tokens)

        # Dense
        self.embedder = SentenceTransformer(dense_model)
        emb = self.embedder.encode([c.text for c in chunks], normalize_embeddings=True, show_progress_bar=True)
        emb = np.asarray(emb, dtype="float32")
        self.faiss = faiss.IndexFlatIP(emb.shape[1])
        self.faiss.add(emb)

        # Rerank
        self.rerank_enabled = rerank
        self.reranker = CrossEncoder(rerank_model) if rerank else None

    def search(self, query: str, bm25_k: int, dense_k: int, top_k: int) -> list[Chunk]:
        # BM25
        bm_scores = self.bm25.get_scores(query.lower().split())
        bm_idx = sorted(range(len(bm_scores)), key=lambda i: bm_scores[i], reverse=True)[:bm25_k]
        bm_ids = [self.chunks[i].chunk_id for i in bm_idx]

        # Dense
        q = self.embedder.encode([query], normalize_embeddings=True)
        q = np.asarray(q, dtype="float32")
        d_scores, d_ids = self.faiss.search(q, dense_k)
        dense_ids = [self.chunks[int(i)].chunk_id for i in d_ids[0] if int(i) != -1]

        # Fusion
        fused_scores = rrf_fusion(bm_ids, dense_ids)
        fused = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)[: max(top_k * 2, 20)]
        fused_chunks = [self.id2chunk[cid] for cid, _ in fused]

        # Optional rerank
        if self.rerank_enabled and self.reranker and fused_chunks:
            pairs = [[query, c.text] for c in fused_chunks]
            rr = self.reranker.predict(pairs)
            ranked = sorted(zip(fused_chunks, rr), key=lambda x: float(x[1]), reverse=True)[:top_k]
            return [c for c, _ in ranked]

        return fused_chunks[:top_k]

# ---------- end-to-end build ----------

def build_chunks(pdfs_dir: str, pages_dir: str, mode: str, urls: list[str] | None) -> list[Chunk]:
    docs: list[Doc] = []
    docs += load_pdfs(pdfs_dir)
    docs += load_local_pages(pages_dir)
    if mode == "online" and urls:
        docs += [fetch_url(u) for u in urls]

    chunks: list[Chunk] = []
    for d in docs:
        if is_injection(d.text):
            continue
        cleaned = redact_pii(d.text)
        chunks.extend(chunk_doc(Doc(d.doc_id, d.source, d.title, cleaned, d.kind)))
    return chunks

def distinct_sources(chunks: list[Chunk]) -> set[str]:
    return {c.source for c in chunks}
