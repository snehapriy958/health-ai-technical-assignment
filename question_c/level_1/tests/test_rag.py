"""Unit and integration tests for Question C Level 1 RAG pipeline."""

import os
import pytest
from fastapi.testclient import TestClient

from question_c.level_1.chunker import load_corpus
from question_c.level_1.retriever import LibraryTFIDFRetriever
from question_c.level_1.llm import (
    MockLLMClient,
    MissingAPIKeyError,
    LLMAPIError,
    get_llm_client,
)
from question_c.level_1.rag_pipeline import RAGPipeline
from question_c.level_1.app import app, get_pipeline


@pytest.fixture(scope="module")
def corpus_chunks():
    return load_corpus()


@pytest.fixture(scope="module")
def retriever(corpus_chunks):
    return LibraryTFIDFRetriever(corpus_chunks)


@pytest.fixture(scope="module")
def mock_pipeline(retriever):
    return RAGPipeline(
        retriever=retriever,
        llm_client=MockLLMClient(),
        top_k=3,
    )


def test_corpus_loading_and_chunking(corpus_chunks):
    """Ensure all 5 WHO documents are loaded and chunked with valid metadata."""
    assert len(corpus_chunks) >= 50
    source_ids = {c.source_id for c in corpus_chunks}
    expected_ids = {
        "who_diabetes",
        "who_hypertension",
        "who_physical_activity",
        "who_healthy_diet",
        "who_obesity",
    }
    assert expected_ids.issubset(source_ids)

    for chunk in corpus_chunks:
        assert chunk.chunk_id
        assert chunk.title
        assert chunk.organization == "World Health Organization"
        assert chunk.source_url.startswith("https://www.who.int/")
        assert len(chunk.text.strip()) > 0


def test_retriever_diabetes_query(retriever):
    """Verify retrieval returns relevant diabetes chunk for diabetes question."""
    results = retriever.retrieve("What are ways to prevent type 2 diabetes?", top_k=3)
    assert len(results) > 0
    top_chunk, score = results[0]
    assert score > 0.1
    # Check that diabetes document is in retrieved chunks
    retrieved_sources = [c.source_id for c, _ in results]
    assert "who_diabetes" in retrieved_sources


def test_retriever_hypertension_query(retriever):
    """Verify retrieval returns relevant hypertension chunk for blood pressure question."""
    results = retriever.retrieve("What blood pressure reading is considered hypertension?", top_k=3)
    assert len(results) > 0
    top_chunk, score = results[0]
    assert score > 0.2
    assert top_chunk.source_id == "who_hypertension"


def test_retriever_physical_activity_query(retriever):
    """Verify retrieval returns relevant physical activity chunk."""
    results = retriever.retrieve("How much moderate physical activity is recommended weekly?", top_k=3)
    assert len(results) > 0
    retrieved_sources = [c.source_id for c, _ in results]
    assert "who_physical_activity" in retrieved_sources


def test_retriever_out_of_domain_query(retriever):
    """Verify that an unrelated question returns no chunks."""
    results = retriever.retrieve("Who won the 1994 FIFA World Cup soccer championship?", top_k=3)
    assert len(results) == 0


def test_pipeline_empty_question(mock_pipeline):
    """Verify empty question raises ValueError."""
    with pytest.raises(ValueError, match="cannot be empty"):
        mock_pipeline.answer_question("")

    with pytest.raises(ValueError, match="cannot be empty"):
        mock_pipeline.answer_question("   ")


def test_pipeline_diabetes_question_with_sources(mock_pipeline):
    """Verify diabetes question returns factual answer and valid source metadata."""
    res = mock_pipeline.answer_question("What are some ways to reduce the risk of diabetes?")
    assert "answer" in res
    assert len(res["answer"]) > 20
    assert len(res["sources"]) > 0

    first_source = res["sources"][0]
    assert first_source["source_id"] == "who_diabetes"
    assert first_source["title"] == "Diabetes"
    assert first_source["organization"] == "World Health Organization"
    assert "https://www.who.int" in first_source["url"]
    assert "section" in first_source


def test_pipeline_hypertension_question_with_sources(mock_pipeline):
    """Verify hypertension question returns factual answer and valid source metadata."""
    res = mock_pipeline.answer_question("What blood pressure measurement confirms hypertension?")
    assert "answer" in res
    assert len(res["sources"]) > 0
    assert any(s["source_id"] == "who_hypertension" for s in res["sources"])


def test_pipeline_out_of_domain_refusal(mock_pipeline):
    """Verify that unrelated questions result in graceful refusal with no invented facts."""
    res = mock_pipeline.answer_question("What is the capital city of France?")
    assert "do not provide enough information" in res["answer"]
    assert res["sources"] == []


def test_missing_api_key_error(monkeypatch):
    """Verify clear error when no LLM API key or mock flag is set."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("MOCK_LLM", raising=False)

    with pytest.raises(MissingAPIKeyError, match="No LLM API key configured"):
        get_llm_client()


def test_fastapi_endpoints(monkeypatch):
    """Test FastAPI /ask, /, and /health endpoints."""
    # Force mock LLM for testing
    monkeypatch.setenv("MOCK_LLM", "1")

    client = TestClient(app)

    # Health check
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"
    assert resp.json()["corpus_chunks"] >= 50

    # Index page
    resp = client.get("/")
    assert resp.status_code == 200
    assert "WHO Grounded RAG" in resp.text

    # Empty question
    resp = client.post("/ask", json={"question": "   "})
    assert resp.status_code == 400
    assert "cannot be empty" in resp.json()["detail"]

    # Diabetes question
    resp = client.post(
        "/ask",
        json={"question": "What lifestyle changes help prevent type 2 diabetes?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert len(data["sources"]) > 0
    assert data["sources"][0]["organization"] == "World Health Organization"

    # Physical activity question
    resp = client.post(
        "/ask",
        json={"question": "How many minutes of physical activity are recommended per week?"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["sources"]) > 0
    assert any("physical_activity" in s["source_id"] for s in data["sources"])
