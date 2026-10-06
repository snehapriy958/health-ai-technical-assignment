# Question C — Level 3: RAG System Evaluation & Failure Analysis

This directory implements **Level 3** of Question C, providing a systematic evaluation of our RAG question-answering assistant over 10 test questions (7 answerable, 3 unanswerable), prior predictions, empirical benchmarking, and an evidence-based failure investigation.

---

## 1. Why These 10 Questions Were Selected

To rigorously evaluate the Level 1 RAG pipeline, the 10 questions test diverse retrieval scenarios rather than only trivial exact keyword matches:
- **Numerical Guidelines (Q01, Q03, Q05)**: Test retrieval of quantitative clinical thresholds (150 minutes of exercise, <10% sugar intake, BMI $\ge$ 30).
- **Clinical Definitions (Q02)**: Tests diagnostic cutoffs (hypertension $\ge 140/90\text{ mmHg}$).
- **Lexical Paraphrase (Q04)**: Tests lay terminology (*"early warning signs"*) against clinical section headings (*"Symptoms"*).
- **Cross-Document Concepts (Q06)**: Tests terms like salt reduction that appear across multiple disease fact sheets.
- **Pharmacological Classes (Q07)**: Tests medical drug terminology against WHO treatment text.
- **Genuine Unanswerables (Q08, Q09, Q10)**: Tests biomedical topics outside the corpus (mRNA vaccines), pure non-health trivia (Olympic games), and communicable diseases outside our 5-document NCD scope (malaria).

---

## 2. Division: Answerable vs. Unanswerable

| Category | Count | IDs | Description |
|---|:---:|---|---|
| **Answerable** | 7 | Q01 – Q07 | Direct or paraphrased queries whose factual answers reside in the 5 WHO documents. |
| **Unanswerable** | 3 | Q08 – Q10 | Valid questions whose factual answers are entirely absent from the 5 WHO documents. |

For all 3 unanswerable questions, the expected behavior is **explicit refusal**:
> *"The available WHO sources do not provide enough information to answer this question."*

---

## 3. Predictions (Evaluation Cycle & Provenance)

> [!NOTE]
> In commit `955429a`, the initial predictions and results were committed simultaneously, meaning Git history did not prove prior commitment. A new prediction template has been prepared in [`predictions.md`](file:///c:/Developers/Sneha/health-ai-technical-assignment/question_c/level_3/predictions.md) to be committed and pushed to GitHub *prior* to executing the evaluation runner.

The baseline evaluation hypotheses recorded during initial system benchmarking were:

| ID | Question | Predicted Retrieval | Predicted Correctness | Predicted Failure Type |
|---|---|:---:|:---:|---|
| **Q01** | *"How many minutes of moderate-intensity physical activity per week does WHO recommend for adults?"* | YES | YES | No failure |
| **Q02** | *"What blood pressure thresholds define hypertension according to WHO?"* | YES | YES | No failure |
| **Q03** | *"What percentage of total daily energy intake should free sugars be limited to in a healthy diet?"* | YES | YES | No failure |
| **Q04** | *"What early warning signs might indicate someone is developing diabetes?"* | NO | NO | **Retrieval failure** |
| **Q05** | *"What BMI threshold classifies an adult as having obesity?"* | YES | YES | No failure |
| **Q06** | *"How does reducing daily salt intake impact high blood pressure and healthy diet?"* | YES | YES | No failure |
| **Q07** | *"What medications are commonly prescribed to lower blood glucose in people with type 2 diabetes?"* | YES | YES | No failure |
| **Q08** | *"What is the primary mechanism of action of mRNA vaccines for infectious diseases?"* | NO | YES | **Expected refusal** |
| **Q09** | *"Which country hosted the first Summer Olympic Games in the modern era?"* | NO | YES | **Expected refusal** |
| **Q10** | *"What are the common symptoms and treatment options for malaria?"* | NO | YES | **Expected refusal** |

---

## 4. Actual Evaluation Results

Run via `run_evaluation.py` on the 71-chunk corpus:

| ID | Question | Top Score | Retrieved Source(s) | Actual Outcome | Correct? |
|---|---|:---:|---|---|:---:|
| **Q01** | Physical activity minutes | `0.2236` | `who_physical_activity` | No failure | ✅ YES |
| **Q02** | Hypertension thresholds | `0.3105` | `who_hypertension` | Retrieval failure (Missing target passage) | ❌ NO |
| **Q03** | Free sugars percentage | `0.3744` | `who_healthy_diet` | No failure | ✅ YES |
| **Q04** | Diabetes early warning signs | `0.1786` | `who_diabetes` | **Retrieval failure (Missing target passage)** | ❌ NO |
| **Q05** | Adult obesity BMI | `0.2025` | `who_obesity` | No failure | ✅ YES |
| **Q06** | Salt reduction & BP | `0.1968` | `who_hypertension`, `who_healthy_diet` | Retrieval failure (Missing target passage) | ❌ NO |
| **Q07** | Diabetes medications | `0.3072` | `who_diabetes` | Retrieval failure (Missing target passage) | ❌ NO |
| **Q08** | mRNA vaccines | `0.0000` | None (Filtered) | **Expected refusal** | ✅ YES |
| **Q09** | Olympic Games | `0.0000` | None (Filtered) | **Expected refusal** | ✅ YES |
| **Q10** | Malaria symptoms & treatment | `0.0000` | None (Filtered) | **Expected refusal** | ✅ YES |

---

## 5. Comparison: Predictions vs. Actual Results

| ID | Predicted Outcome | Actual Outcome | Prediction Match? |
|---|---|---|:---:|
| **Q01** | No failure | No failure | ✅ **Correct** |
| **Q02** | No failure | Retrieval failure (Missing target passage) | ❌ *Incorrect hypothesis* |
| **Q03** | No failure | No failure | ✅ **Correct** |
| **Q04** | Retrieval failure | Retrieval failure (Missing target passage) | ✅ **Correct (Anticipated)** |
| **Q05** | No failure | No failure | ✅ **Correct** |
| **Q06** | No failure | Retrieval failure (Missing target passage) | ❌ *Incorrect hypothesis* |
| **Q07** | No failure | Retrieval failure (Missing target passage) | ❌ *Incorrect hypothesis* |
| **Q08** | Expected refusal | Expected refusal | ✅ **Correct** |
| **Q09** | Expected refusal | Expected refusal | ✅ **Correct** |
| **Q10** | Expected refusal | Expected refusal | ✅ **Correct** |

**Prediction Accuracy**: **7 / 10 (70.0%)**

### Analysis of Incorrect Predictions:
- In Q02, Q06, and Q07, we originally predicted "No failure" expecting the top chunk to capture the core target fact. However, because section chunking fragmented `who_hypertension` and `who_diabetes` into discrete chunks, broad lifestyle overview/prevention chunks outscored specific list/diagnostic chunks in TF-IDF. This demonstrates that document-level relevance does not guarantee passage-level precision.

---

## 6. Unanswerable-Question Behavior

All three unanswerable questions (Q08, Q09, Q10) performed cleanly:
1. **Zero False Positives**: Not a single ungrounded answer was generated.
2. **Threshold Rejection**: Because the core topical nouns (*"mRNA"*, *"Olympic"*, *"malaria"*) have zero document frequency in the 5-document index, maximum cosine similarity was `0.0000`.
3. **Safe Refusal**: The pipeline immediately triggered the refusal handler:
   > *"The available WHO sources do not provide enough information to answer this question."*

---

## 7. Deep-Dive Investigation of One Wrong Answer (Question Q04)

Executed via `question_c/level_3/analyze_failure.py`:

- **Question**: *"What early warning signs might indicate someone is developing diabetes?"*
- **Generated Answer**:
  > *"According to the World Health Organization: Type 2 diabetes affects how your body uses sugar for energy... Early diagnosis is important to prevent the worst effects of type 2 diabetes. The best way to detect diabetes early is to get regular check-ups and blood tests with a healthcare provider."*
- **Ground Truth Expected**: Excessive thirst, frequent urination, blurred vision, tiredness, unintentional weight loss.

### Evidence-Based Failure Attribution:
1. **Location of Ground Truth**:
   The actual symptoms are contained in chunk `who_diabetes_c003` under section heading `## Symptoms`.
2. **Retrieval Rank of Supporting Passage**:
   When scored across the entire corpus, chunk `who_diabetes_c003` received a cosine score of only **0.0583**, ranking **#11** in the corpus.
3. **Absence from Generator Context**:
   Because the retriever only supplies the top-3 chunks ($k=3$), and the minimum similarity threshold is $0.12$, `who_diabetes_c003` was **completely excluded from the prompt context**.
4. **Why Chunk `who_diabetes_c005` Won the Retrieval**:
   The query word `"early"` matched `"early diagnosis"` and `"detect diabetes early"`, and `"developing"` matched `"developing type 2 diabetes"` in `who_diabetes_c005`, generating a score of `0.1786`.
5. **Conclusion**:
   **This was 100% a RETRIEVAL FAILURE caused by the Lexical Gap**. The LLM generator operated correctly on the context it received; it failed to output the symptoms solely because the sparse TF-IDF retriever failed to surface them.

---

## 8. Limitations of This Evaluation

1. **Deterministic Mock Generator**: In mock evaluation mode, LLM generation simulates extractive factual synthesis. Live API calls (Gemini/OpenAI) can synthesize across multiple retrieved chunks more fluidly, but may introduce stochastic phrasing.
2. **Corpus Size**: Evaluating on a 71-chunk corpus provides rapid diagnostic transparency, but larger corpora would introduce greater distractor density.
3. **Top-k Sensitivity**: Restricting context to $k=3$ creates a steep cutoff where rank #4 passages are completely lost.

---

## 9. Key Lessons Learned

1. **TF-IDF is Vulnerable to Lay Paraphrasing**: When users search using non-clinical phrasing (*"early warning signs"* vs *"symptoms"*), sparse lexical search frequently surfaces the wrong paragraph.
2. **Strict Thresholds Successfully Prevent Hallucination**: A chosen similarity threshold (`0.12`) correctly resulted in refusal for all 3 unanswerable out-of-domain and excluded medical topics without hallucinating.
3. **Passage Granularity Matters**: Chunk boundaries must balance section coherence with factual density; if a symptom list is isolated into a separate chunk without common conversational queries in its heading, sparse retrieval cannot easily bridge the gap.
