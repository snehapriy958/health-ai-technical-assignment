"""Custom retriever implementation using from-scratch TF-IDF and NumPy cosine similarity."""

from typing import Any, Dict, List, Tuple
import numpy as np

from question_c.level_1.chunker import DocumentChunk, load_corpus
from question_c.level_2.custom_tfidf import (
    CustomTfidfVectorizer,
    batch_cosine_similarity,
)


class CustomNumPyRetriever:
    """Retriever operating entirely on custom TF-IDF matrices and NumPy cosine similarity.

    Zero third-party retrieval libraries or vector databases are utilized.
    """

    def __init__(
        self,
        chunks: List[DocumentChunk] | None = None,
        min_score_threshold: float = 0.0,
    ):
        if chunks is None:
            self.chunks = load_corpus()
        else:
            self.chunks = chunks

        if not self.chunks:
            raise ValueError("Retriever initialized with empty chunk corpus.")

        self.min_score_threshold = min_score_threshold

        # Enrich chunk text with topic, title, and section heading for fair comparison with Level 1
        self.corpus_texts = [
            f"{c.topic} - {c.title} - {c.section}\n{c.text}" for c in self.chunks
        ]

        # Fit custom TF-IDF vectorizer and build document matrix of shape (N, |V|)
        self.vectorizer = CustomTfidfVectorizer()
        self.doc_matrix = self.vectorizer.fit_transform(self.corpus_texts)

    def retrieve(
        self, query: str, top_k: int = 3
    ) -> List[Tuple[DocumentChunk, float]]:
        """Retrieve top-k relevant document chunks for a query.

        Process:
        1. Tokenize query and compute query TF-IDF vector of shape (|V|,).
        2. Compute cosine similarity against all N document chunk vectors using NumPy dot products.
        3. Rank descending by similarity score.
        4. Return top-k (DocumentChunk, score) pairs.
        """
        if not query or not query.strip():
            return []

        # Vectorize query
        query_vec = self.vectorizer.transform([query.strip()])[0]

        # NumPy cosine similarity against all chunks: shape (N,)
        similarities = batch_cosine_similarity(query_vec, self.doc_matrix)

        # Sort descending
        ranked_indices = np.argsort(similarities)[::-1]

        results: List[Tuple[DocumentChunk, float]] = []
        for idx in ranked_indices:
            score = float(similarities[idx])
            if score < self.min_score_threshold:
                break
            results.append((self.chunks[idx], score))
            if len(results) >= top_k:
                break

        return results

    def retrieve_formatted(
        self, query: str, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Retrieve top-k chunks formatted as dictionaries for inspection and reporting."""
        raw_results = self.retrieve(query, top_k=top_k)
        formatted: List[Dict[str, Any]] = []
        for chunk, score in raw_results:
            formatted.append({
                "chunk_id": chunk.chunk_id,
                "source_id": chunk.source_id,
                "title": chunk.title,
                "organization": chunk.organization,
                "section": chunk.section,
                "url": chunk.source_url,
                "score": round(score, 4),
                "text_snippet": chunk.text[:200] + ("..." if len(chunk.text) > 200 else ""),
            })
        return formatted
