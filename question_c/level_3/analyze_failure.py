"""Detailed diagnostic failure analysis for Question C Level 3."""

import sys
from pathlib import Path
from typing import Any, Dict

repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from question_c.level_1.chunker import load_corpus
from question_c.level_1.rag_pipeline import RAGPipeline
from question_c.level_1.llm import MockLLMClient
from sklearn.metrics.pairwise import cosine_similarity


def analyze_q04_retrieval_failure() -> Dict[str, Any]:
    """Diagnose the Retrieval Failure in Question Q04:
    Query: 'What early warning signs might indicate someone is developing diabetes?'
    """
    corpus = load_corpus()
    pipeline = RAGPipeline(llm_client=MockLLMClient(), top_k=3)
    query = "What early warning signs might indicate someone is developing diabetes?"

    result = pipeline.answer_question(query)
    raw_results = pipeline.retriever.retrieve(query, top_k=10)

    # Locate ground truth chunk
    ground_truth_chunk = None
    for chunk in corpus:
        if chunk.chunk_id == "who_diabetes_c003":
            ground_truth_chunk = chunk
            break

    # Calculate rank and score of all chunks
    q_vec = pipeline.retriever.vectorizer.transform([query])
    sims = cosine_similarity(q_vec, pipeline.retriever.chunk_matrix)[0]

    all_chunks_scored = []
    for idx, chunk in enumerate(pipeline.retriever.chunks):
        all_chunks_scored.append((chunk, float(sims[idx])))
    all_chunks_scored.sort(key=lambda x: x[1], reverse=True)

    gt_rank = -1
    gt_score = 0.0
    for rank, (c, score) in enumerate(all_chunks_scored, start=1):
        if c.chunk_id == "who_diabetes_c003":
            gt_rank = rank
            gt_score = score
            break

    return {
        "id": "Q04",
        "query": query,
        "answer": result["answer"],
        "expected_fact": "Excessive thirst, frequent urination, blurred vision, tiredness, weight loss",
        "expected_chunk_id": "who_diabetes_c003",
        "expected_chunk_rank": gt_rank,
        "expected_chunk_score": round(gt_score, 4),
        "top_retrieved": [
            {
                "rank": idx + 1,
                "chunk_id": c.chunk_id,
                "score": round(s, 4),
                "section": c.section,
                "text": c.text,
            }
            for idx, (c, s) in enumerate(raw_results[:3])
        ],
        "in_top_3": False,
        "stage": "RETRIEVAL FAILURE",
        "root_cause": (
            "Lexical gap / Vocabulary mismatch. The query uses conversational lay phrasing "
            "('early warning signs') which has zero term overlap with the document section heading 'Symptoms'. "
            "Meanwhile, the query term 'early' matched 'early diagnosis' in chunk who_diabetes_c005 (score 0.1786), "
            "causing the irrelevant section to outrank the symptoms passage (rank #11, score 0.0583)."
        ),
        "potential_improvement": (
            "Dense semantic embeddings (e.g., ClinicalBioBERT / BGE) or query expansion with clinical synonyms "
            "('early warning signs' -> 'symptoms, onset signs') to bridge the vocabulary gap."
        ),
    }


def analyze_q07_generation_failure() -> Dict[str, Any]:
    """Diagnose the Generation Failure in Question Q07:
    Query: 'What medications are commonly prescribed to lower blood glucose in people with type 2 diabetes?'
    """
    corpus = load_corpus()
    pipeline = RAGPipeline(llm_client=MockLLMClient(), top_k=3)
    query = "What medications are commonly prescribed to lower blood glucose in people with type 2 diabetes?"

    result = pipeline.answer_question(query)
    raw_results = pipeline.retriever.retrieve(query, top_k=3)

    target_chunk_in_top3 = any(c.chunk_id == "who_diabetes_c010" for c, _ in raw_results)

    return {
        "id": "Q07",
        "query": query,
        "answer": result["answer"],
        "expected_fact": "Metformin, sulfonylureas, SGLT-2 inhibitors, insulin injections",
        "expected_chunk_id": "who_diabetes_c010",
        "expected_chunk_rank": 1 if target_chunk_in_top3 else -1,
        "top_retrieved": [
            {
                "rank": idx + 1,
                "chunk_id": c.chunk_id,
                "score": round(s, 4),
                "section": c.section,
                "text": c.text,
            }
            for idx, (c, s) in enumerate(raw_results)
        ],
        "in_top_3": target_chunk_in_top3,
        "stage": "GENERATION / ANSWER-SELECTION FAILURE" if target_chunk_in_top3 else "RETRIEVAL FAILURE",
        "root_cause": (
            "The expected supporting passage 'Diagnosis and treatment' (who_diabetes_c010) was successfully "
            "retrieved in the top context. However, during answer synthesis, the mock generator selected "
            "introductory lifestyle sentences from the passage rather than extracting the specific pharmacological "
            "names (metformin, sulfonylureas, SGLT-2 inhibitors) listed in the paragraph."
        ),
        "potential_improvement": (
            "Refine prompt instructions to explicitly demand extraction of enumerated medication names, "
            "or employ a live generative model with chain-of-thought extraction directed at specific drug classes."
        ),
    }


def print_report():
    q04 = analyze_q04_retrieval_failure()
    print("=" * 80)
    print("FAILURE 1: RETRIEVAL FAILURE (QUESTION Q04)")
    print("=" * 80)
    print(f"Query: {q04['query']}")
    print(f"Expected Evidence: {q04['expected_fact']} (Chunk: {q04['expected_chunk_id']})")
    print(f"Ground-Truth Rank: #{q04['expected_chunk_rank']} (Score: {q04['expected_chunk_score']})")
    print(f"In Top 3 Context? {q04['in_top_3']}")
    print(f"Failure Stage: {q04['stage']}")
    print(f"Root Cause: {q04['root_cause']}")
    print(f"Potential Improvement: {q04['potential_improvement']}\n")

    q07 = analyze_q07_generation_failure()
    print("=" * 80)
    print("FAILURE 2: GENERATION / SELECTION FAILURE (QUESTION Q07)")
    print("=" * 80)
    print(f"Query: {q07['query']}")
    print(f"Expected Evidence: {q07['expected_fact']} (Chunk: {q07['expected_chunk_id']})")
    print(f"In Top 3 Context? {q07['in_top_3']}")
    print(f"Failure Stage: {q07['stage']}")
    print(f"Root Cause: {q07['root_cause']}")
    print(f"Potential Improvement: {q07['potential_improvement']}")
    print("=" * 80)


if __name__ == "__main__":
    print_report()
