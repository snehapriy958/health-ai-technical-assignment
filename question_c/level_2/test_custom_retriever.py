"""Unit and algorithmic tests for Custom TF-IDF and NumPy Cosine Similarity."""

import math
import numpy as np
import pytest

from question_c.level_2.custom_tfidf import (
    tokenize,
    compute_tf,
    compute_idf,
    cosine_similarity,
    batch_cosine_similarity,
    CustomTfidfVectorizer,
)
from question_c.level_2.custom_retriever import CustomNumPyRetriever
from question_c.level_1.chunker import load_corpus, DocumentChunk


def test_tokenizer_behavior():
    """Verify lowercasing, punctuation stripping, digits stripping, and stopword removal."""
    sample_text = "Diabetes, type-2 & physical activity in 2026! What is the recommendation?"
    tokens = tokenize(sample_text)
    
    # 'in', 'what', 'is', 'the' are stopwords and should be removed.
    # '2026' is a digit string and should be removed.
    # 'diabetes', 'type', 'physical', 'activity', 'recommendation' should remain.
    expected = ["diabetes", "type", "physical", "activity", "recommendation"]
    assert tokens == expected

    # Empty text
    assert tokenize("") == []
    assert tokenize("   ") == []


def test_tf_hand_calculation():
    """Verify exact hand-calculated relative term frequencies."""
    # Document has 4 total terms: 'apple' twice, 'banana' once, 'orange' once
    tokens = ["apple", "banana", "apple", "orange"]
    tf = compute_tf(tokens)

    assert tf["apple"] == pytest.approx(2.0 / 4.0)  # 0.5
    assert tf["banana"] == pytest.approx(1.0 / 4.0)  # 0.25
    assert tf["orange"] == pytest.approx(1.0 / 4.0)  # 0.25
    assert sum(tf.values()) == pytest.approx(1.0)

    # Empty tokens
    assert compute_tf([]) == {}


def test_idf_hand_calculation():
    """Verify exact smoothed IDF values calculated by hand."""
    # 3 documents:
    # Doc 0: ['cat', 'dog']
    # Doc 1: ['cat', 'mouse']
    # Doc 2: ['cat', 'bird']
    # N = 3
    corpus_tokens = [
        ["cat", "dog"],
        ["cat", "mouse"],
        ["cat", "bird"],
    ]

    idf = compute_idf(corpus_tokens)

    # df('cat') = 3
    # idf('cat') = ln((1 + 3) / (1 + 3)) + 1.0 = ln(1.0) + 1.0 = 1.0
    assert idf["cat"] == pytest.approx(1.0)

    # df('dog') = 1
    # idf('dog') = ln((1 + 3) / (1 + 1)) + 1.0 = ln(4 / 2) + 1.0 = ln(2.0) + 1.0
    expected_dog_idf = math.log(2.0) + 1.0  # approx 1.693147
    assert idf["dog"] == pytest.approx(expected_dog_idf)
    assert idf["mouse"] == pytest.approx(expected_dog_idf)
    assert idf["bird"] == pytest.approx(expected_dog_idf)


def test_tfidf_vector_construction():
    """Verify matrix dimensions and computed TF-IDF values."""
    docs = [
        "cat dog",
        "cat mouse",
        "cat bird",
    ]
    vectorizer = CustomTfidfVectorizer()
    matrix = vectorizer.fit_transform(docs)

    # 3 documents, 4 unique terms: 'bird', 'cat', 'dog', 'mouse'
    assert matrix.shape == (3, 4)
    assert vectorizer.feature_names_ == ["bird", "cat", "dog", "mouse"]

    cat_idx = vectorizer.vocabulary_["cat"]
    dog_idx = vectorizer.vocabulary_["dog"]

    # In Doc 0 ("cat dog"), tokens = ['cat', 'dog'], total terms = 2
    # tf('cat') = 0.5, idf('cat') = 1.0 => tfidf = 0.5
    assert matrix[0, cat_idx] == pytest.approx(0.5 * 1.0)

    # tf('dog') = 0.5, idf('dog') = ln(2) + 1 => tfidf = 0.5 * (ln(2) + 1)
    expected_dog_tfidf = 0.5 * (math.log(2.0) + 1.0)
    assert matrix[0, dog_idx] == pytest.approx(expected_dog_tfidf)

    # 'mouse' does not appear in Doc 0
    mouse_idx = vectorizer.vocabulary_["mouse"]
    assert matrix[0, mouse_idx] == 0.0


def test_cosine_similarity_calculation():
    """Verify manual cosine similarity against geometric and trigonometric truths."""
    # 1. Collinear vectors: cosine = 1.0
    v1 = np.array([3.0, 4.0])
    v2 = np.array([6.0, 8.0])
    assert cosine_similarity(v1, v2) == pytest.approx(1.0)

    # 2. Orthogonal vectors: cosine = 0.0
    v_x = np.array([1.0, 0.0])
    v_y = np.array([0.0, 1.0])
    assert cosine_similarity(v_x, v_y) == pytest.approx(0.0)

    # 3. 45-degree angle: cosine = 1 / sqrt(2) ≈ 0.70710678
    v_diag = np.array([1.0, 1.0])
    assert cosine_similarity(v_x, v_diag) == pytest.approx(1.0 / math.sqrt(2.0))


def test_zero_vector_handling():
    """Verify safe zero handling without division-by-zero errors or warnings."""
    zero_vec = np.array([0.0, 0.0, 0.0])
    non_zero = np.array([1.0, 2.0, 3.0])

    # 1D cosine
    assert cosine_similarity(zero_vec, non_zero) == 0.0
    assert cosine_similarity(non_zero, zero_vec) == 0.0
    assert cosine_similarity(zero_vec, zero_vec) == 0.0

    # Batch cosine
    matrix = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 2.0, 3.0],
    ])
    scores = batch_cosine_similarity(zero_vec, matrix)
    assert np.all(scores == 0.0)

    scores2 = batch_cosine_similarity(non_zero, matrix)
    assert scores2[0] == 0.0
    assert scores2[1] == pytest.approx(1.0)


def test_top_k_ranking_and_deterministic_order():
    """Verify top-k descending ranking order."""
    chunks = [
        DocumentChunk(
            chunk_id="c1",
            source_id="s1",
            title="Cardio",
            organization="WHO",
            source_url="http://example.com/1",
            topic="Exercise",
            section="Running",
            text="Running and jogging improve cardiovascular health and aerobic stamina.",
        ),
        DocumentChunk(
            chunk_id="c2",
            source_id="s2",
            title="Nutrition",
            organization="WHO",
            source_url="http://example.com/2",
            topic="Diet",
            section="Greens",
            text="Vegetables and fruits deliver essential vitamins and minerals for diet.",
        ),
        DocumentChunk(
            chunk_id="c3",
            source_id="s3",
            title="Sleep",
            organization="WHO",
            source_url="http://example.com/3",
            topic="Rest",
            section="Night",
            text="Adequate nighttime sleep restores cognitive alertness.",
        ),
    ]

    retriever = CustomNumPyRetriever(chunks=chunks)

    # Query about aerobic jogging should rank chunk c1 first
    res = retriever.retrieve("aerobic jogging cardiovascular", top_k=2)
    assert len(res) == 2
    assert res[0][0].chunk_id == "c1"
    assert res[0][1] > res[1][1]  # descending scores


def test_who_corpus_integration():
    """Verify custom retriever operates correctly over the real 71 WHO chunks."""
    retriever = CustomNumPyRetriever()
    assert len(retriever.chunks) >= 70

    # Query about hypertension
    results = retriever.retrieve("What blood pressure measurement confirms hypertension?", top_k=3)
    assert len(results) == 3
    top_chunk, top_score = results[0]
    assert top_score > 0.15
    assert top_chunk.source_id == "who_hypertension"
