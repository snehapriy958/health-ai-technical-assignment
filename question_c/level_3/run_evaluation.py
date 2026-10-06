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
        "expected_chunks": ["who_physical_activity_c006", "who_physical_activity_c002"],
        "target_facts": ["150"],
        "evidence_desc": "WHO Physical Activity fact sheet states at least 150 minutes of moderate-intensity physical activity per week.",
    },
    {
        "id": "Q02",
        "question": "What blood pressure thresholds define hypertension according to WHO?",
        "expected_status": "Answerable",
        "expected_source": "who_hypertension",
        "expected_chunks": ["who_hypertension_c001", "who_hypertension_c004"],
        "target_facts": ["140", "90"],
        "evidence_desc": "WHO Hypertension fact sheet defines hypertension as systolic >=140 and/or diastolic >=90 mmHg.",
    },
    {
        "id": "Q03",
        "question": "What percentage of total daily energy intake should free sugars be limited to in a healthy diet?",
        "expected_status": "Answerable",
        "expected_source": "who_healthy_diet",
        "expected_chunks": ["who_healthy_diet_c005"],
        "target_facts": ["10%"],
        "evidence_desc": "WHO Healthy Diet fact sheet limits free sugars to less than 10% of total daily energy intake.",
    },
    {
        "id": "Q04",
        "question": "What early warning signs might indicate someone is developing diabetes?",
        "expected_status": "Answerable",
        "expected_source": "who_diabetes",
        "expected_chunks": ["who_diabetes_c003"],
        "target_facts": ["thirst", "urination", "blurred vision", "tiredness", "weight loss"],
        "evidence_desc": "WHO Diabetes fact sheet section 'Symptoms' (chunk who_diabetes_c003) lists thirst, frequent urination, tiredness.",
    },
    {
        "id": "Q05",
        "question": "What BMI threshold classifies an adult as having obesity?",
        "expected_status": "Answerable",
        "expected_source": "who_obesity",
        "expected_chunks": ["who_obesity_c004"],
        "target_facts": ["30"],
        "evidence_desc": "WHO Obesity fact sheet defines adult obesity as BMI >= 30.",
    },
    {
        "id": "Q06",
        "question": "How does reducing daily salt intake impact high blood pressure and healthy diet?",
        "expected_status": "Answerable",
        "expected_source": "who_hypertension",
        "expected_chunks": ["who_healthy_diet_c008", "who_hypertension_c002", "who_hypertension_c005"],
        "target_facts": ["blood pressure", "salt", "sodium"],
        "evidence_desc": "WHO Healthy Diet and Hypertension fact sheets link salt reduction to lowering blood pressure.",
    },
    {
        "id": "Q07",
        "question": "What medications are commonly prescribed to lower blood glucose in people with type 2 diabetes?",
        "expected_status": "Answerable",
        "expected_source": "who_diabetes",
        "expected_chunks": ["who_diabetes_c010"],
        "target_facts": ["metformin", "sulfonylureas", "sglt-2", "insulin"],
        "evidence_desc": "WHO Diabetes fact sheet 'Diagnosis and treatment' lists metformin, sulfonylureas, SGLT-2 inhibitors, insulin.",
    },
    {
        "id": "Q08",
        "question": "What is the primary mechanism of action of mRNA vaccines for infectious diseases?",
        "expected_status": "Unanswerable",
        "expected_source": None,
        "expected_chunks": [],
        "target_facts": [],
        "evidence_desc": "Out-of-corpus biomedical topic; mRNA vaccines are completely absent from the 5-document NCD corpus.",
    },
    {
        "id": "Q09",
        "question": "Which country hosted the first Summer Olympic Games in the modern era?",
        "expected_status": "Unanswerable",
        "expected_source": None,
        "expected_chunks": [],
        "target_facts": [],
        "evidence_desc": "Out-of-corpus general trivia; sports history is completely absent from the 5-document NCD corpus.",
    },
    {
        "id": "Q10",
        "question": "What are the common symptoms and treatment options for malaria?",
        "expected_status": "Unanswerable",
        "expected_source": None,
        "expected_chunks": [],
        "target_facts": [],
        "evidence_desc": "Out-of-corpus communicable disease; malaria is completely absent from the 5-document NCD corpus.",
    },
]

# Predictions frozen in predictions.md
FROZEN_PREDICTIONS = {
    "Q01": {"retrieval": "YES", "outcome": "Correct", "confidence": "High"},
    "Q02": {"retrieval": "YES", "outcome": "Correct", "confidence": "High"},
    "Q03": {"retrieval": "YES", "outcome": "Correct", "confidence": "High"},
    "Q04": {"retrieval": "NO / likely failure", "outcome": "Incorrect/incomplete", "confidence": "Medium"},
    "Q05": {"retrieval": "YES", "outcome": "Correct", "confidence": "High"},
    "Q06": {"retrieval": "YES", "outcome": "Correct", "confidence": "High"},
    "Q07": {"retrieval": "YES", "outcome": "Correct", "confidence": "High"},
    "Q08": {"retrieval": "NO", "outcome": "Correct refusal", "confidence": "High"},
    "Q09": {"retrieval": "NO", "outcome": "Correct refusal", "confidence": "High"},
    "Q10": {"retrieval": "NO", "outcome": "Correct refusal", "confidence": "Medium-High"},
}


def run_evaluation() -> Dict[str, Any]:
    """Execute the Level 1 RAG pipeline across all 10 Level 3 questions."""
    pipeline = RAGPipeline(llm_client=MockLLMClient(), top_k=3)
    results: List[Dict[str, Any]] = []

    for item in QUESTIONS:
        q_id = item["id"]
        q_text = item["question"]
        expected_status = item["expected_status"]

        # 1. Retrieve raw chunks
        raw_retrieved = pipeline.retriever.retrieve(q_text, top_k=3)
        top_score = float(raw_retrieved[0][1]) if raw_retrieved else 0.0
        retrieved_chunk_ids = [c.chunk_id for c, _ in raw_retrieved]
        retrieved_source_ids = [c.source_id for c, _ in raw_retrieved]
        retrieved_sections = [c.section for c, _ in raw_retrieved]

        # 2. Execute RAG pipeline
        qa_output = pipeline.answer_question(q_text)
        answer = qa_output["answer"]
        sources = qa_output["sources"]

        # 3. Determine failure taxonomy
        is_refusal = "do not provide enough information" in answer.lower()

        if expected_status == "Unanswerable":
            actual_retrieval_str = "NO" if not retrieved_chunk_ids else "YES (False positive)"
            if is_refusal:
                actual_correct = True
                actual_outcome = "Correct refusal"
            else:
                actual_correct = False
                actual_outcome = "Hallucination / False positive"
        else:
            # Answerable question
            expected_chunks = item.get("expected_chunks", [])
            supporting_chunk_retrieved = any(cid in retrieved_chunk_ids for cid in expected_chunks)

            # Check if required factual answer is contained
            target_facts = item.get("target_facts", [])
            fact_present = any(fact.lower() in answer.lower() for fact in target_facts) if target_facts else True

            actual_retrieval_str = "YES" if supporting_chunk_retrieved else "NO"

            if not supporting_chunk_retrieved:
                actual_correct = False
                actual_outcome = "Retrieval failure"
            elif not fact_present:
                actual_correct = False
                actual_outcome = "Generation failure"
            else:
                actual_correct = True
                actual_outcome = "Correct"

        # 4. Evaluate against frozen prediction
        pred = FROZEN_PREDICTIONS[q_id]
        pred_outcome = pred["outcome"].lower()

        if pred_outcome in ("correct", "no failure"):
            prediction_match = actual_correct and (actual_outcome == "Correct")
        elif "refusal" in pred_outcome:
            prediction_match = (actual_outcome == "Correct refusal")
        elif "incorrect" in pred_outcome or "failure" in pred_outcome:
            prediction_match = (not actual_correct) or (actual_outcome in ("Retrieval failure", "Generation failure"))
        else:
            prediction_match = False

        results.append({
            "id": q_id,
            "question": q_text,
            "expected_status": expected_status,
            "expected_source": item["expected_source"],
            "expected_chunks": item.get("expected_chunks", []),
            "target_facts": item.get("target_facts", []),
            "evidence_desc": item["evidence_desc"],
            "top_score": round(top_score, 4),
            "retrieved_chunk_ids": retrieved_chunk_ids,
            "retrieved_source_ids": list(dict.fromkeys(retrieved_source_ids)),
            "retrieved_sections": list(dict.fromkeys(retrieved_sections)),
            "sources": sources,
            "answer": answer,
            "actual_retrieval": actual_retrieval_str,
            "actual_outcome": actual_outcome,
            "actual_correct": actual_correct,
            "my_prediction": pred["outcome"],
            "my_retrieval_pred": pred["retrieval"],
            "prediction_match": prediction_match,
        })

    return {"results": results}


def write_results_markdown(data: Dict[str, Any], filepath: Path, pred_commit: str = "TBD", eval_commit: str = "TBD") -> None:
    results = data["results"]
    lines = [
        "# Question C — Level 3 Final Results",
        "",
        "**Seed**: `S = 48`  ",
        f"**Prediction commit**: `{pred_commit}`  ",
        f"**Evaluation commit**: `{eval_commit}`  ",
        "",
        "> [!NOTE]",
        "> These results were produced by running the final evaluation runner script strictly *after*",
        "> committing and pushing the pre-evaluation predictions to GitHub.",
        "",
        "---",
        "",
        "## 1. Final Results Table",
        "",
        "| ID | My Prediction | Actual Retrieval | Actual Outcome | Prediction Match | Evidence |",
        "|---|---|:---:|---|:---:|---|",
    ]

    correct_predictions = 0
    qa_correct = 0

    for r in results:
        match_str = "✅ Match" if r["prediction_match"] else "❌ Mismatch"
        if r["prediction_match"]:
            correct_predictions += 1
        if r["actual_correct"]:
            qa_correct += 1

        top_chunk = r["retrieved_chunk_ids"][0] if r["retrieved_chunk_ids"] else "None (Filtered)"
        evidence_snippet = f"Top: `{top_chunk}` (score: {r['top_score']:.4f})"

        lines.append(
            f"| **{r['id']}** | {r['my_prediction']} | {r['actual_retrieval']} | {r['actual_outcome']} | {match_str} | {evidence_snippet} |"
        )

    pred_accuracy_pct = (correct_predictions / len(results)) * 100
    qa_correctness_pct = (qa_correct / len(results)) * 100

    lines.extend([
        "",
        "---",
        "",
        "## 2. Evaluation Metrics Summary",
        "",
        f"- **Prediction Accuracy**: **{correct_predictions} / {len(results)} ({pred_accuracy_pct:.1f}%)**  ",
        "  *(Proportion of pre-test predictions that correctly anticipated the actual system outcome)*",
        f"- **QA Correctness**: **{qa_correct} / {len(results)} ({qa_correctness_pct:.1f}%)**  ",
        "  *(Proportion of questions where the RAG assistant delivered an authoritative factual answer or correct refusal)*",
        "",
        "> [!IMPORTANT]",
        "> **Metric Distinction Notice**: Prediction accuracy measures pre-experiment hypothesis quality, whereas QA correctness measures the operational performance of the RAG assistant. They are distinct metrics.",
        "",
        "---",
        "",
        "## 3. Failure Taxonomy Breakdown",
        "",
        f"- **Retrieval Failures**: {sum(1 for r in results if r['actual_outcome'] == 'Retrieval failure')}",
        f"- **Generation Failures**: {sum(1 for r in results if r['actual_outcome'] == 'Generation failure')}",
        f"- **Correct Answers**: {sum(1 for r in results if r['actual_outcome'] == 'Correct')}",
        f"- **Correct Refusals**: {sum(1 for r in results if r['actual_outcome'] == 'Correct refusal')}",
        f"- **Hallucinations / False Positives**: {sum(1 for r in results if r['actual_outcome'] == 'Hallucination / False positive')}",
        "",
        "---",
        "",
        "## 4. Detailed Per-Question Outputs and Source Attribution",
        "",
    ])

    for r in results:
        lines.extend([
            f"### Question {r['id']}: \"{r['question']}\"",
            f"- **Expected Status**: {r['expected_status']}  ",
            f"- **Target Evidence Requirement**: {r['evidence_desc']}  ",
            f"- **My Pre-Test Prediction**: {r['my_prediction']} (Retrieval: {r['my_retrieval_pred']})  ",
            f"- **Actual Retrieval**: {r['actual_retrieval']} (Top score: `{r['top_score']:.4f}`)  ",
            f"- **Actual Outcome**: **{r['actual_outcome']}** (Prediction Match: {'✅ Match' if r['prediction_match'] else '❌ Mismatch'})  ",
            f"- **Retrieved Chunks**: `{', '.join(r['retrieved_chunk_ids']) if r['retrieved_chunk_ids'] else 'None (Below threshold 0.12)'}`  ",
            f"- **Generated Answer**:",
            f"> {r['answer'].replace(chr(10), chr(10) + '> ')}",
            "",
            "- **Verified Source Attribution**:",
        ])
        if r["sources"]:
            for s in r["sources"]:
                lines.append(
                    f"  - `{s['source_id']}` ({s['title']} — *{s['section']}*): relevance `{s['relevance_score']:.4f}`, [WHO Source URL]({s['url']})"
                )
        else:
            lines.append("  - *No sources attributed (Clean out-of-corpus refusal)*")
        lines.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    data = run_evaluation()
    out_file = Path(__file__).resolve().parent / "results.md"
    write_results_markdown(data, out_file)
    print(f"Evaluation complete. Results written to {out_file}")
