"""Library-based TF-IDF retriever for Question C Level 1."""

from typing import List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from question_c.level_1.chunker import DocumentChunk


class LibraryTFIDFRetriever:
    """Retriever utilizing scikit-learn's TfidfVectorizer and cosine similarity.

    Level 1 uses this standard off-the-shelf library retriever.
    Level 2 will implement custom TF-IDF and cosine similarity from scratch.
    """

    def __init__(
        self,
        chunks: List[DocumentChunk],
        ngram_range: Tuple[int, int] = (1, 2),
        min_score_threshold: float = 0.12,
    ):
        if not chunks:
            raise ValueError("Retriever initialized with empty chunk corpus.")

        self.chunks = chunks
        self.min_score_threshold = min_score_threshold

        # Enrich chunk text with topic, title, and section heading for better matching
        self.corpus_texts = [
            f"{c.topic} - {c.title} - {c.section}\n{c.text}" for c in self.chunks
        ]

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=ngram_range,
            sublinear_tf=True,
            norm="l2",
        )
        self.chunk_matrix = self.vectorizer.fit_transform(self.corpus_texts)

    def retrieve(
        self, query: str, top_k: int = 3
    ) -> List[Tuple[DocumentChunk, float]]:
        """Retrieve top-k relevant document chunks for a given query.

        Returns:
            List of (DocumentChunk, similarity_score) tuples, sorted by score descending.
            Returns empty list if no chunks meet the minimum similarity threshold.
        """
        if not query or not query.strip():
            return []

        query_vec = self.vectorizer.transform([query.strip()])
        similarities = cosine_similarity(query_vec, self.chunk_matrix)[0]

        top_indices = np.argsort(similarities)[::-1]

        results: List[Tuple[DocumentChunk, float]] = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score < self.min_score_threshold:
                break
            results.append((self.chunks[idx], score))
            if len(results) >= top_k:
                break

        return results
