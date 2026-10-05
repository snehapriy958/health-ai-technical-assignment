"""Custom TF-IDF implementation from scratch using Python and NumPy.

No sklearn or third-party retriever libraries are used in this module.
"""

import math
import re
from typing import Dict, List, Set
import numpy as np

# Standard documented set of English stop words
ENGLISH_STOP_WORDS: Set[str] = frozenset({
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's",
    "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
    "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my",
    "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd",
    "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll",
    "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
    "where", "where's", "which", "while", "who", "who's", "whom", "why",
    "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
    "you're", "you've", "your", "yours", "yourself", "yourselves"
})


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric terms with punctuation and stop words removed.

    Steps:
    1. Lowercase text.
    2. Extract alphanumeric word tokens using regex word boundaries.
    3. Filter out tokens that belong to the documented English stop words set.
    """
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
    return [w for w in words if w not in ENGLISH_STOP_WORDS and not w.isdigit()]


def compute_tf(tokens: List[str]) -> Dict[str, float]:
    """Compute term frequency (TF) for a tokenized document.

    Formula:
        tf(term, doc) = count(term in doc) / total_terms_in_doc

    Returns:
        Dictionary mapping term -> relative frequency.
    """
    if not tokens:
        return {}
    total_terms = float(len(tokens))
    counts: Dict[str, int] = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    return {term: count / total_terms for term, count in counts.items()}


def compute_idf(doc_token_lists: List[List[str]]) -> Dict[str, float]:
    """Compute smoothed inverse document frequency (IDF) for all terms in the corpus.

    Formula:
        idf(term) = log((1 + N) / (1 + df(term))) + 1.0

    Where:
        N = total number of documents/chunks in corpus
        df(term) = number of documents containing the term

    Smoothing prevents division by zero and ensures that terms appearing in all
    documents still retain a positive weight (+1.0) rather than collapsing to zero.
    """
    n_docs = len(doc_token_lists)
    if n_docs == 0:
        return {}

    # Count document frequency for each unique term
    df: Dict[str, int] = {}
    for doc_tokens in doc_token_lists:
        unique_terms = set(doc_tokens)
        for term in unique_terms:
            df[term] = df.get(term, 0) + 1

    idf: Dict[str, float] = {}
    for term, doc_freq in df.items():
        # Smoothed natural logarithm
        idf[term] = math.log((1.0 + n_docs) / (1.0 + doc_freq)) + 1.0

    return idf


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Compute cosine similarity between two 1D NumPy vectors.

    Formula:
        cosine_similarity(A, B) = dot(A, B) / (||A||_2 * ||B||_2)

    Safe handling:
        If ||A|| == 0 or ||B|| == 0, returns 0.0 to prevent division by zero.
    """
    norm_a = float(np.linalg.norm(vec_a))
    norm_b = float(np.linalg.norm(vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    dot_product = float(np.dot(vec_a, vec_b))
    sim = dot_product / (norm_a * norm_b)
    # Clamp to [-1.0, 1.0] to guard against floating-point inaccuracy
    return float(np.clip(sim, -1.0, 1.0))


def batch_cosine_similarity(query_vec: np.ndarray, doc_matrix: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between a 1D query vector and a 2D document matrix.

    Args:
        query_vec: 1D array of shape (V,)
        doc_matrix: 2D array of shape (N, V)

    Returns:
        1D array of shape (N,) containing similarity scores.
    """
    norm_q = float(np.linalg.norm(query_vec))
    if norm_q == 0.0:
        return np.zeros(doc_matrix.shape[0], dtype=float)

    # Compute L2 norms for all document vectors: shape (N,)
    doc_norms = np.linalg.norm(doc_matrix, axis=1)

    # Dot products: shape (N,)
    dot_products = np.dot(doc_matrix, query_vec)

    # Avoid division by zero where doc_norm == 0
    with np.errstate(divide="ignore", invalid="ignore"):
        similarities = np.where(
            doc_norms > 0.0,
            dot_products / (doc_norms * norm_q),
            0.0
        )

    return np.clip(similarities, -1.0, 1.0)


class CustomTfidfVectorizer:
    """TF-IDF vectorizer constructed from scratch using Python and NumPy."""

    def __init__(self):
        self.vocabulary_: Dict[str, int] = {}
        self.idf_: np.ndarray = np.array([])
        self.feature_names_: List[str] = []

    def fit(self, raw_documents: List[str]) -> "CustomTfidfVectorizer":
        """Learn vocabulary and IDF weights from corpus documents."""
        doc_tokens = [tokenize(doc) for doc in raw_documents]
        idf_dict = compute_idf(doc_tokens)

        # Deterministic sorting of vocabulary for reproducible vector indices
        self.feature_names_ = sorted(idf_dict.keys())
        self.vocabulary_ = {term: idx for idx, term in enumerate(self.feature_names_)}

        # Build dense IDF array of shape (|V|,)
        idf_values = [idf_dict[term] for term in self.feature_names_]
        self.idf_ = np.array(idf_values, dtype=float)

        return self

    def transform(self, raw_documents: List[str]) -> np.ndarray:
        """Transform raw documents into a 2D NumPy array of TF-IDF vectors (M, |V|)."""
        if len(self.vocabulary_) == 0:
            raise ValueError("CustomTfidfVectorizer must be fitted before transform.")

        vocab_size = len(self.feature_names_)
        n_docs = len(raw_documents)
        matrix = np.zeros((n_docs, vocab_size), dtype=float)

        for i, doc in enumerate(raw_documents):
            tokens = tokenize(doc)
            tf_dict = compute_tf(tokens)
            for term, tf_val in tf_dict.items():
                if term in self.vocabulary_:
                    idx = self.vocabulary_[term]
                    matrix[i, idx] = tf_val * self.idf_[idx]

        return matrix

    def fit_transform(self, raw_documents: List[str]) -> np.ndarray:
        """Fit vocabulary and return transformed document matrix."""
        return self.fit(raw_documents).transform(raw_documents)
