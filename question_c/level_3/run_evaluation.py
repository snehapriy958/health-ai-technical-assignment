"""Evaluation script executing all 10 Level 3 questions against Level 1 RAG pipeline."""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure repository root is on sys.path
repo_root = Path(__file__).resolve().parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from question_c.level_1.rag_pipeline import RAGPipeline
from question_c.level_1.llm import MockLLMClient

QUESTIONS = [
    {
        "id": "Q01",
        "question": "How many minutes of moderate-intensity physical activity per week does WHO recommend for adults?",
        "expected_status": "Answerable",
        "expected_source": "who_physical_activity",
        "target_fact": "150",
    },
    {
        "id": "Q02",
        "question": "What blood pressure thresholds define hypertension according to WHO?",
        "expected_status": "Answerable",
        "expected_source": "who_hypertension",
        "target_fact": "140/90",
    },
    {
        "id": "Q03",
        "question": "What percentage of total daily energy intake should free sugars be limited to in a healthy diet?",
        "expected_status": "Answerable",
        "expected_source": "who_healthy_diet",
        "target_fact": "10%",
    },
    {
        "id": "Q04",
        "question": "What early warning signs might indicate someone is developing diabetes?",
        "expected_status": "Answerable",
        "expected_source": "who_diabetes",
        "target_fact": "thirsty",
    },
    {
        "id": "Q05",
        "question": "What BMI threshold classifies an adult as having obesity?",
        "expected_status": "Answerable",
        "expected_source": "who_obesity",
        "target_fact": "30",
    },
    {
        "id": "Q06",
        "question": "How does reducing daily salt intake impact high blood pressure and healthy diet?",
        "expected_status": "Answerable",
        "expected_source": "who_hypertension",
        "target_fact": "salt",
    },
    {
        "id": "Q07",
        "question": "What medications are commonly prescribed to lower blood glucose in people with type 2 diabetes?",
        "expected_status": "Answerable",
        "expected_source": "who_diabetes",
        "target_fact": "metformin",
    },
    {
        "id": "Q08",
        "question": "What is the primary mechanism of action of mRNA vaccines for infectious diseases?",
        "expected_status": "Unanswerable",
        "expected_source": None,
        "target_fact": None,
    },
    {
        "id": "Q09",
        "question": "Which country hosted the first Summer Olympic Games in the modern era?",
        "expected_status": "Unanswerable",
        "expected_source": None,
        "target_fact": None,
    },
    {
        "id": "Q10",
        "question": "What are the common symptoms and treatment options for malaria?",
        "expected_status": "Unanswerable",
        "expected_source": None,
        "target_fact": None,
    },
]

# Predictions recorded prior in predictions.md
PREDICTIONS = {
    "Q01": {"retrieval": True, "correct": True, "type": "No failure"},
    "Q02": {"retrieval": True, "correct": True, "type": "No failure"},
    "Q03": {"retrieval": True, "correct": True, "type": "No failure"},
    "Q04": {"retrieval": False, "correct": False, "type": "Retrieval failure"},
    "Q05": {"retrieval": True, "correct": True, "type": "No failure"},
    "Q06": {"retrieval": True, "correct": True, "type": "No failure"},
    "Q07": {"retrieval": True, "correct": True, "type": "No failure"},
    "Q08": {"retrieval": False, "correct": True, "type": "Expected refusal"},
    "Q09": {"retrieval": False, "correct": True, "type": "Expected refusal"},
    "Q10": {"retrieval": False, "correct": True, "type": "Expected refusal"},
}


def run_evaluation() -> Dict[str, Any]:
    # Use Level 1 RAG pipeline with deterministic MockLLMClient for consistent, reproducible evaluation
    pipeline = RAGPipeline(llm_client=MockLLMClient(), top_k=3)

    results: List[Dict[str, Any]] = []

    for item in QUESTIONS:
        q_id = item["id"]
        q_text = item["question"]
        expected_status = item["expected_status"]

        # 1. Inspect raw retrieval
        raw_retrieved = pipeline.retriever.retrieve(q_text, top_k=3)
        top_score = float(raw_retrieved[0][1]) if raw_retrieved else 0.0
        retrieved_chunk_ids = [c.chunk_id for c, _ in raw_retrieved]
        retrieved_source_ids = [c.source_id for c, _ in raw_retrieved]
        retrieved_sections = [c.section for c, _ in raw_retrieved]

        # 2. Execute full RAG pipeline
        qa_output = pipeline.answer_question(q_text)
        answer = qa_output["answer"]
        sources = qa_output["sources"]

        # 3. Determine correctness & failure type
        is_refusal = "do not provide enough information" in answer

        if expected_status == "Unanswerable":
            if is_refusal:
                actual_correct = True
                actual_failure_type = "Expected refusal"
                actual_retrieval_success = False
            else:
                actual_correct = False
                actual_failure_type = "Hallucination / False positive"
                actual_retrieval_success = True
        else:
            # Answerable question
            expected_src = item["expected_source"]
            has_expected_source = expected_src in retrieved_source_ids
            target_fact_present = (
                item["target_fact"].lower() in answer.lower()
                if item["target_fact"]
                else True
            )

            actual_retrieval_success = has_expected_source and not is_refusal

            if is_refusal:
                actual_correct = False
                actual_failure_type = "Retrieval failure (Premature refusal)"
            elif not has_expected_source:
                actual_correct = False
                actual_failure_type = "Retrieval failure (Wrong document)"
            elif not target_fact_present:
                actual_correct = False
                actual_failure_type = "Retrieval failure (Missing target passage)"
            else:
                actual_correct = True
                actual_failure_type = "No failure"

        pred = PREDICTIONS[q_id]
        pred_match = (
            (pred["correct"] == actual_correct)
            and (
                pred["type"] == actual_failure_type
                or (pred["type"] == "Retrieval failure" and "Retrieval failure" in actual_failure_type)
            )
        )

        results.append({
            "id": q_id,
            "question": q_text,
            "expected_status": expected_status,
            "expected_source": item["expected_source"],
            "top_score": round(top_score, 4),
            "retrieved_chunk_ids": retrieved_chunk_ids,
            "retrieved_source_ids": list(dict.fromkeys(retrieved_source_ids)),
            "retrieved_sections": list(dict.fromkeys(retrieved_sections)),
            "answer": answer,
            "actual_retrieval_success": actual_retrieval_success,
            "actual_correct": actual_correct,
            "actual_failure_type": actual_failure_type,
            "predicted_correct": pred["correct"],
            "predicted_type": pred["type"],
            "prediction_match": pred_match,
        })

    return {
        "results": results,
    }


def write_results_markdown(data: Dict[str, Any], filepath: Path) -> None:
    results = data["results"]
    lines = [
        "# Level 3 Evaluation Results",
        "",
        "This document contains the empirical evaluation results of running all 10 test questions through the Level 1 RAG pipeline.",
        "",
        "## 1. Comprehensive Results Table",
        "",
        "| ID | Question | Expected Status | Top Score | Retrieved Source(s) | Top Section | Correct? | Outcome / Failure Type |",
        "|---|---|---|:---:|---|---|:---:|---|",
    ]

    for r in results:
        srcs = ", ".join(f"`{s}`" for s in r["retrieved_source_ids"]) if r["retrieved_source_ids"] else "None (Filtered)"
        sec = r["retrieved_sections"][0] if r["retrieved_sections"] else "N/A"
        corr_mark = "✅ YES" if r["actual_correct"] else "❌ NO"
        lines.append(
            f"| {r['id']} | \"{r['question']}\" | {r['expected_status']} | {r['top_score']:.4f} | {srcs} | {sec} | {corr_mark} | {r['actual_failure_type']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 2. Comparison: Predictions vs. Actual Results",
        "",
        "| ID | Predicted Outcome | Actual Outcome | Predicted Correctness | Actual Correctness | Prediction Match? |",
        "|---|---|---|:---:|:---:|:---:|",
    ])

    correct_predictions = 0
    for r in results:
        match_str = "✅ Correct" if r["prediction_match"] else "❌ Incorrect"
        if r["prediction_match"]:
            correct_predictions += 1
        lines.append(
            f"| {r['id']} | {r['predicted_type']} | {r['actual_failure_type']} | {'YES' if r['predicted_correct'] else 'NO'} | {'YES' if r['actual_correct'] else 'NO'} | {match_str} |"
        )

    accuracy_pct = (correct_predictions / len(results)) * 100
    lines.extend([
        "",
        f"**Prediction Accuracy**: **{correct_predictions} / {len(results)} ({accuracy_pct:.1f}%)**",
        "",
        "---",
        "",
        "## 3. Detailed Per-Question Outputs",
        "",
    ])

    for r in results:
        lines.extend([
            f"### Question {r['id']}: \"{r['question']}\"",
            f"- **Expected Status**: {r['expected_status']}  ",
            f"- **Top Similarity Score**: `{r['top_score']:.4f}`  ",
            f"- **Retrieved Chunks**: `{', '.join(r['retrieved_chunk_ids']) if r['retrieved_chunk_ids'] else 'None'}`  ",
            f"- **Retrieved Sections**: `{', '.join(r['retrieved_sections']) if r['retrieved_sections'] else 'None'}`  ",
            f"- **Generated Answer**:",
            f"> {r['answer'].replace(chr(10), chr(10) + '> ')}",
            f"- **Outcome Classification**: **{r['actual_failure_type']}**  ",
            f"- **Prediction Was**: {'Accurate' if r['prediction_match'] else 'Inaccurate'}",
            "",
        ])

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    data = run_evaluation()
    out_file = Path(__file__).resolve().parent / "results.md"
    write_results_markdown(data, out_file)
    print(f"Evaluation complete. Results written to {out_file}")
    for r in data["results"]:
        status_sym = "PASS" if r["actual_correct"] else "FAIL"
        print(f"[{r['id']}] {status_sym} | Score: {r['top_score']:.4f} | Outcome: {r['actual_failure_type']}")
