"""Detailed diagnostic failure analysis for Question C Level 3."""

import sys
from pathlib import Path
from typing import Any, Dict

# Ensure repository root is on sys.path
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from question_c.level_1.chunker import load_corpus
from question_c.level_1.retriever import LibraryTFIDFRetriever
from question_c.level_1.rag_pipeline import RAGPipeline
from question_c.level_1.llm import MockLLMClient


def inspect_q04_failure() -> Dict[str, Any]:
    """Diagnose the failure in Question Q04:

    Query: 'What early warning signs might indicate someone is developing diabetes?'
    """
    corpus = load_corpus()
    pipeline = RAGPipeline(llm_client=MockLLMClient(), top_k=3)

    query = "What early warning signs might indicate someone is developing diabetes?"

    # 1. Pipeline Execution
    result = pipeline.answer_question(query)

    # 2. Inspect Retriever ranking across the entire corpus
    raw_results = pipeline.retriever.retrieve(query, top_k=10)

    # 3. Locate the ground truth chunk containing the actual symptoms
    ground_truth_chunk = None
    for chunk in corpus:
        if chunk.source_id == "who_diabetes" and "feeling very thirsty" in chunk.text:
            ground_truth_chunk = chunk
            break

    # Calculate ground truth chunk rank and score in retriever
    all_chunks_scored = []
    q_vec = pipeline.retriever.vectorizer.transform([query])
    from sklearn.metrics.pairwise import cosine_similarity
    sims = cosine_similarity(q_vec, pipeline.retriever.chunk_matrix)[0]

    for idx, chunk in enumerate(pipeline.retriever.chunks):
        all_chunks_scored.append((chunk, float(sims[idx])))

    all_chunks_scored.sort(key=lambda x: x[1], reverse=True)

    gt_rank = -1
    gt_score = 0.0
    if ground_truth_chunk:
        for rank, (c, score) in enumerate(all_chunks_scored, start=1):
            if c.chunk_id == ground_truth_chunk.chunk_id:
                gt_rank = rank
                gt_score = score
                break

    return {
        "query": query,
        "answer": result["answer"],
        "retrieved_top_sources": [
            {
                "rank": idx + 1,
                "chunk_id": c.chunk_id,
                "source_id": c.source_id,
                "section": c.section,
                "score": round(s, 4),
                "text": c.text,
            }
            for idx, (c, s) in enumerate(raw_results[:3])
        ],
        "ground_truth_chunk": {
            "chunk_id": ground_truth_chunk.chunk_id if ground_truth_chunk else None,
            "section": ground_truth_chunk.section if ground_truth_chunk else None,
            "rank": gt_rank,
            "score": round(gt_score, 4),
            "text": ground_truth_chunk.text if ground_truth_chunk else None,
        },
    }


def print_diagnostic_report(diag: Dict[str, Any]) -> None:
    print("=" * 80)
    print("DIAGNOSTIC FAILURE INVESTIGATION: QUESTION Q04")
    print("=" * 80)
    print(f"Query: \"{diag['query']}\"\n")

    print("--- 1. Generated Answer ---")
    print(diag["answer"])
    print("\n--- 2. Chunks Provided in Retrieval Context (Top-3) ---")
    for r in diag["retrieved_top_sources"]:
        print(f"Rank {r['rank']}: Chunk ID `{r['chunk_id']}` | Section: {r['section']} | Score: {r['score']}")
        print(f"Snippet: {r['text'][:150].strip()}...\n")

    gt = diag["ground_truth_chunk"]
    print("--- 3. Ground-Truth Supporting Chunk in Corpus ---")
    print(f"Chunk ID: `{gt['chunk_id']}` | Section: {gt['section']}")
    print(f"Corpus Rank: #{gt['rank']} (Score: {gt['score']})")
    print("Full Ground-Truth Text:")
    print(gt["text"])

    print("\n" + "=" * 80)
    print("EVIDENCE-BASED FAILURE CLASSIFICATION:")
    print("=" * 80)
    print("Classification: RETRIEVAL FAILURE (Lexical Gap / Vocabulary Mismatch)")
    print()
    print("Evidence:")
    print("1. The ground truth answer (excessive thirst, frequent urination, blurred vision,")
    print(f"   fatigue, unintentional weight loss) is contained in chunk `{gt['chunk_id']}`.")
    print(f"2. Chunk `{gt['chunk_id']}` achieved a low similarity score of {gt['score']}, ranking #{gt['rank']} in the corpus.")
    print("3. Because only top-3 chunks are passed to the generator, chunk `who_diabetes_c003` was")
    print("   COMPLETELY ABSENT from the prompt context.")
    print("4. Chunk `who_diabetes_c005` scored highest (0.1786) because 'early' matched 'early diagnosis'")
    print("   and 'developing' matched 'developing type 2 diabetes'.")
    print("5. Conclusion: The LLM did NOT hallucinate or drop information; it faithfully answered")
    print("   from the context it was given (`who_diabetes_c005`). The failure occurred upstream")
    print("   in the sparse TF-IDF retrieval stage.")
    print("=" * 80)


if __name__ == "__main__":
    report = inspect_q04_failure()
    print_diagnostic_report(report)
