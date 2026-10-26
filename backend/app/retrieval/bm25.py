"""
BM25 Keyword Retrieval Engine
Pure-Python, zero-dependency BM25Okapi implementation tailored for IT runbooks and documentation.
"""
import math
import re
from typing import Any, Dict, List, Tuple

# Common English stopwords to ignore in IT search queries
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
    "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "me", "more",
    "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other",
    "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so",
    "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then",
    "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why",
    "with", "would", "you", "your", "yours", "yourself", "yourselves"
}

def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text into lowercase alphanumeric terms."""
    terms = re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", text.lower())
    return [t for t in terms if t not in STOPWORDS]

class BM25Retriever:
    """
    BM25Okapi ranker for IT incident runbooks.
    k1 controls term frequency saturation; b controls document length normalization.
    """
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.docs: List[Dict[str, Any]] = []
        self.corpus_size: int = 0
        self.avg_dl: float = 0.0
        self.doc_lengths: List[int] = []
        self.doc_freqs: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

    def index(self, documents: List[Dict[str, Any]]):
        """
        Index a collection of documents.
        Each document must contain 'id', 'title', 'content', and optional metadata.
        """
        self.docs = documents
        self.corpus_size = len(documents)
        if self.corpus_size == 0:
            return

        total_length = 0
        self.doc_lengths = []
        self.doc_freqs = {}

        tokenized_corpus = []
        for doc in documents:
            combined_text = f"{doc.get('title', '')} {doc.get('content', '')}"
            tokens = tokenize(combined_text)
            tokenized_corpus.append(tokens)
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_length += doc_len

            # Track unique terms in this document for document frequency
            unique_terms = set(tokens)
            for term in unique_terms:
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        self.avg_dl = total_length / self.corpus_size if self.corpus_size > 0 else 1.0

        # Calculate IDF with standard smoothing
        for term, freq in self.doc_freqs.items():
            self.idf[term] = math.log(1.0 + (self.corpus_size - freq + 0.5) / (freq + 0.5))

        self.tokenized_corpus = tokenized_corpus

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search indexed runbooks using BM25 scoring.
        Returns top_k tuples of (document, score).
        """
        if not self.docs or self.corpus_size == 0:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores: List[float] = [0.0] * self.corpus_size

        for term in query_tokens:
            if term not in self.idf:
                continue
            idf = self.idf[term]

            for i, doc_tokens in enumerate(self.tokenized_corpus):
                # Count term frequency in doc
                tf = doc_tokens.count(term)
                if tf == 0:
                    continue

                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (self.doc_lengths[i] / self.avg_dl))
                scores[i] += idf * (numerator / denominator)

        # Pair scores with documents
        results = [(self.docs[i], scores[i]) for i in range(self.corpus_size)]
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
