"""
Hybrid RAG Retriever
Combines BM25 lexical keyword matching with Dense Semantic retrieval
using Reciprocal Rank Fusion (RRF) and linear score normalization.
"""
import glob
import os
from typing import Any, Dict, List

from app.retrieval.bm25 import BM25Retriever
from app.retrieval.embeddings import SemanticRetriever


class HybridRetriever:
    """
    Enterprise hybrid retrieval pipeline for IT runbooks and documentation.
    Balances precise keyword hits (error codes, exceptions) with conceptual semantic understanding.
    """
    def __init__(self, rrf_k: int = 60, alpha: float = 0.5):
        self.bm25 = BM25Retriever()
        self.semantic = SemanticRetriever()
        self.rrf_k = rrf_k
        self.alpha = alpha  # Weight for BM25 vs Semantic
        self.documents: List[Dict[str, Any]] = []

    def load_from_directory(self, dir_path: str):
        """
        Loads markdown runbooks from the knowledge base directory,
        extracts document IDs, titles, and content.
        """
        docs = []
        md_files = glob.glob(os.path.join(dir_path, "*.md"))
        for file_path in md_files:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            filename = os.path.basename(file_path)
            lines = content.strip().split("\n")
            title = filename
            doc_id = filename.replace(".md", "").upper()

            # Extract title and ID from first header if present (e.g. # RB-5XX-001: Investigating High HTTP 5xx...)
            if lines and lines[0].startswith("# "):
                header = lines[0].replace("# ", "").strip()
                if ":" in header:
                    parts = header.split(":", 1)
                    doc_id = parts[0].strip()
                    title = parts[1].strip()
                else:
                    title = header

            category = "RUNBOOK"
            if "escalation" in filename.lower():
                category = "ESCALATION"
            elif "rollback" in filename.lower():
                category = "SOP"

            docs.append({
                "id": doc_id,
                "title": title,
                "category": category,
                "content": content,
                "source": file_path,
                "version": "1.0",
            })

        self.index_documents(docs)
        return docs

    def index_documents(self, documents: List[Dict[str, Any]]):
        """Indexes documents in both lexical and semantic vector indices."""
        self.documents = documents
        self.bm25.index(documents)
        self.semantic.index(documents)

    def search(
        self,
        query: str,
        top_k: int = 3,
        method: str = "HYBRID"
    ) -> List[Dict[str, Any]]:
        """
        Executes search using requested retrieval strategy:
        - BM25: Pure lexical keyword retrieval
        - SEMANTIC: Pure dense semantic vector retrieval
        - HYBRID: Combined Reciprocal Rank Fusion + Normalized Score
        """
        if not self.documents:
            return []

        # 1. BM25 results
        bm25_results = self.bm25.search(query, top_k=len(self.documents))
        if method.upper() == "BM25":
            return [
                {
                    **doc,
                    "relevance_score": round(score, 4),
                    "retrieval_method": "BM25",
                    "snippet": self._extract_snippet(doc["content"], query),
                }
                for doc, score in bm25_results[:top_k]
            ]

        # 2. Semantic results
        semantic_results = self.semantic.search(query, top_k=len(self.documents))
        if method.upper() == "SEMANTIC":
            return [
                {
                    **doc,
                    "relevance_score": round(score, 4),
                    "retrieval_method": "SEMANTIC",
                    "snippet": self._extract_snippet(doc["content"], query),
                }
                for doc, score in semantic_results[:top_k]
            ]

        # 3. Hybrid Reciprocal Rank Fusion (RRF)
        # RRF Score = 1 / (k + rank_bm25) + 1 / (k + rank_semantic)
        rrf_scores: Dict[str, float] = {}
        doc_map: Dict[str, Dict[str, Any]] = {}

        for rank, (doc, _) in enumerate(bm25_results):
            d_id = doc["id"]
            doc_map[d_id] = doc
            rrf_scores[d_id] = rrf_scores.get(d_id, 0.0) + (1.0 / (self.rrf_k + rank + 1))

        for rank, (doc, _) in enumerate(semantic_results):
            d_id = doc["id"]
            doc_map[d_id] = doc
            rrf_scores[d_id] = rrf_scores.get(d_id, 0.0) + (1.0 / (self.rrf_k + rank + 1))

        # Sort by RRF score descending
        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

        final_results = []
        for d_id in sorted_ids[:top_k]:
            doc = doc_map[d_id]
            final_results.append({
                **doc,
                "relevance_score": round(rrf_scores[d_id] * 100, 4),  # Scale for display
                "retrieval_method": "HYBRID_RRF",
                "snippet": self._extract_snippet(doc["content"], query),
            })

        return final_results

    def _extract_snippet(self, content: str, query: str, max_chars: int = 240) -> str:
        """Extracts a relevant passage snippet containing query terms or the document summary."""
        lines = [line.strip() for line in content.split("\n") if line.strip() and not line.startswith("#")]
        query_words = set(query.lower().split())

        # Prefer line with maximum query word overlap
        best_line = ""
        best_count = -1
        for line in lines:
            lower_line = line.lower()
            match_count = sum(1 for w in query_words if w in lower_line)
            if match_count > best_count:
                best_count = match_count
                best_line = line

        snippet = best_line if best_line else (lines[0] if lines else "")
        if len(snippet) > max_chars:
            snippet = snippet[:max_chars] + "..."
        return snippet
