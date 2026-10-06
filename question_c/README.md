# Question C — Trusted Health QA Assistant

## Objective

Build a document-grounded health question-answering assistant that
answers using a small collection of public health documents and shows
the source used for each answer.

## Level 1

Requirements:

1. Collect 5–10 public health documents.
2. Build a RAG + LLM question-answering pipeline.
3. Display the source for every answer.

## Level 2

Implement retrieval yourself:

1. Chunk the documents.
2. Generate TF-IDF representations.
3. Calculate cosine similarity using NumPy.
4. Retrieve the most relevant chunks.
5. Compare the custom top-3 retrieval with a library retriever
   using three questions.

A vector database or retriever library must not replace the required
manual retrieval implementation.

## Level 3

Requirements:

1. Create 10 evaluation questions.
2. Include at least 3 questions that cannot be answered from the
   collected documents.
3. Write predictions before running the evaluation.
4. Report the actual results.
5. Analyze one incorrect answer.
6. Determine whether the failure came from retrieval or the LLM.

## Personal Seed

`S = 48`

## Run Instructions

### Level 1: Start RAG Assistant API & Frontend
```bash
# Run FastAPI server on port 8012
uvicorn question_c.level_1.app:app --host 127.0.0.1 --port 8012
```
Open `http://127.0.0.1:8012` in a web browser to test the interactive question-answering interface.

### Level 2: Custom TF-IDF Retrieval vs Library Comparison
```bash
# Run unit tests verifying custom TF-IDF implementation from scratch
pytest question_c/level_2/test_custom_retriever.py -v

# Run 3-query retrieval comparison (custom NumPy vs scikit-learn)
python question_c/level_2/compare_retrievers.py
```

### Level 3: Evaluator and Failure Analysis
```bash
# Execute 10-query test evaluation suite
python question_c/level_3/run_evaluation.py

# Run diagnostic failure analysis script
python question_c/level_3/analyze_failure.py
```

## Results

### Level 2 Retriever Comparison
- **Implementation**: Custom tokenization, unigram vocabulary ($|V| = 1{,}544$), smoothed IDF ($\ln((1+N)/(1+\text{df})) + 1.0$), and pure NumPy dot-product cosine similarity.
- **Comparison Findings**:
  - Q02 and Q03 achieved 100% Top-1 exact chunk match between custom and scikit-learn retrievers.
  - Custom cosine scores are numerically higher ($\sim 0.40\text{--}0.52$) than scikit-learn ($\sim 0.20\text{--}0.35$) because the library retriever includes bigrams ($|V| \approx 3{,}700$), distributing vector weights across a wider feature space.

### Level 3 Evaluation Summary
- **Evaluation Cycle**: Strict PREDICTION COMMIT (`c9b7f0f`) $\rightarrow$ EVALUATION EXECUTION $\rightarrow$ RESULTS COMMIT (`458e89d`).
- **Prediction Accuracy**: **9 / 10 (90.0%)** (9 of 10 pre-test predictions matched empirical outcomes).
- **QA Correctness**: **8 / 10 (80.0%)** (5 correct answers, 3 correct refusals).
- **Failure Taxonomy**:
  - **Retrieval Failure (1)**: Q04 (*"early warning signs of diabetes"*) failed because lay terminology had zero overlap with the document heading *"Symptoms"*; target chunk ranked #11 (score 0.0583).
  - **Generation Failure (1)**: Q02 (*"blood pressure thresholds"*) retrieved the target chunk at rank #2 (score 0.2805), but extractive generation selected prevention sentences omitting the 140/90 figures.
  - **Correct Answers (5)**: Q01, Q03, Q05, Q06, Q07.
  - **Correct Refusals (3)**: Q08 (mRNA vaccines), Q09 (Olympic games), Q10 (malaria) correctly refused with 0.0000 similarity score.
  - **Hallucinations (0)**: Zero false positives across all queries.

## Sources

The question-answering corpus is drawn directly from official World Health Organization (WHO) fact sheets:
1. **Diabetes**: [https://www.who.int/news-room/fact-sheets/detail/diabetes](https://www.who.int/news-room/fact-sheets/detail/diabetes)
2. **Hypertension**: [https://www.who.int/news-room/fact-sheets/detail/hypertension](https://www.who.int/news-room/fact-sheets/detail/hypertension)
3. **Physical Activity**: [https://www.who.int/news-room/fact-sheets/detail/physical-activity](https://www.who.int/news-room/fact-sheets/detail/physical-activity)
4. **Healthy Diet**: [https://www.who.int/news-room/fact-sheets/detail/healthy-diet](https://www.who.int/news-room/fact-sheets/detail/healthy-diet)
5. **Obesity and Overweight**: [https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight](https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight)