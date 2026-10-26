"""
Local Dense Semantic Vector Engine
Generates local dense embeddings and computes cosine similarity for IT documents and queries.
Works 100% locally and deterministically with zero network calls or external API keys.
"""
import hashlib
from typing import Any, Dict, List, Tuple

import numpy as np

EMBEDDING_DIM = 256

def hash_feature(token: str, seed: int = 0) -> int:
    """Computes a deterministic feature bucket index."""
    h = hashlib.md5(f"{token}_{seed}".encode("utf-8")).hexdigest()
    return int(h, 16) % EMBEDDING_DIM

def extract_dense_vector(text: str) -> np.ndarray:
    """
    Produces a normalized 256-dimensional semantic vector using term frequency
    and character n-gram hashing (subword embeddings).
    Captures morphological variations (e.g., 'connect', 'connections', 'connection_pool').
    """
    vec = np.zeros(EMBEDDING_DIM, dtype=np.float32)
    words = text.lower().split()
    if not words:
        return vec

    for word in words:
        # Word-level embedding feature
        idx = hash_feature(word, seed=42)
        vec[idx] += 1.0

        # Subword 3-gram and 4-gram features for semantic robustness
        if len(word) >= 3:
            for n in (3, 4):
                for i in range(len(word) - n + 1):
                    ngram = word[i:i+n]
                    idx_ng = hash_feature(ngram, seed=101)
                    vec[idx_ng] += 0.5

    # L2 normalize
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec

class SemanticRetriever:
    """
    Lightweight vector store for fast, deterministic semantic similarity search.
    """
    def __init__(self):
        self.docs: List[Dict[str, Any]] = []
        self.doc_vectors: np.ndarray = np.empty((0, EMBEDDING_DIM), dtype=np.float32)

    def index(self, documents: List[Dict[str, Any]]):
        """Builds semantic vectors for all documents in the corpus."""
        self.docs = documents
        if not documents:
            self.doc_vectors = np.empty((0, EMBEDDING_DIM), dtype=np.float32)
            return

        vectors = []
        for doc in documents:
            combined = f"{doc.get('title', '')} {doc.get('category', '')} {doc.get('content', '')}"
            vec = extract_dense_vector(combined)
            vectors.append(vec)

        self.doc_vectors = np.array(vectors, dtype=np.float32)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Computes cosine similarity between query embedding and all indexed document vectors.
        """
        if len(self.docs) == 0 or self.doc_vectors.shape[0] == 0:
            return []

        q_vec = extract_dense_vector(query)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []

        # Cosine similarity is dot product of normalized vectors
        scores = np.dot(self.doc_vectors, q_vec)

        # Pair documents with similarity scores
        results = [(self.docs[i], float(scores[i])) for i in range(len(self.docs))]
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
