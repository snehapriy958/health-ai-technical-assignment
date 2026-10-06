# Personal Intelligence & Technical Reflection

**Candidate**: Sneha Kumari | **Personal Seed (S)**: 48 | **Questions Selected**: B & C
**Repository**: [health-ai-technical-assignment](https://github.com/snehapriy958/health-ai-technical-assignment) | **Date**: October 2026

---

### 1. Key Engineering Decisions (Chosen vs. Rejected)

| Decision Component | Chosen Approach | Rejected Alternative | Engineering Rationale & Own Results |
|---|---|---|---|
| **Question B: Model** | Logistic Regression + `StandardScaler` ($L_2$ reg) | Deep Neural Net / Gradient Boosting | Small clinical sample ($N \approx 300$). Logistic Regression prevents overfitting, yields monotonic risk scores, and provides transparent coefficients. |
| **Question B: Persistence** | SQLite (WAL mode, parameterized raw SQL) | Heavy ORM (SQLAlchemy) / PostgreSQL | Zero external service overhead; WAL enables safe concurrent reads. Raw SQL makes `/stats` aggregations (`COUNT`, `AVG`) fully transparent. |
| **Question C: Corpus** | 5 official WHO fact sheets (71 section chunks) | Uncurated web scrapes / Wikipedia | Clinical QA demands peer-reviewed authority for diagnostic cutoffs ($\ge 140/90\text{ mmHg}$, $\text{BMI} \ge 30$). |
| **Question C: L1 Retrieval** | `sklearn` TF-IDF (unigrams + bigrams, threshold 0.12) | Vector DB (Chroma/Pinecone) | A 71-chunk corpus does not justify vector DB overhead. Sparse TF-IDF provides sub-millisecond retrieval with an exact 0.12 refusal cutoff. |
| **Question C: L2 Retrieval** | Custom Python & NumPy TF-IDF from scratch | Library retrievers for custom task | Proves first-principles control over TF ($\text{count}/\text{total}$), smoothed IDF ($\ln((1+N)/(1+\text{df})) + 1.0$), and safe zero-norm cosine handling. |

---

### 2. Experimental Insights & Failure Analysis

- **Question B Model**: Test Accuracy **73.77%** (45/61), ROC-AUC **0.7955**. Outputs predicted probabilities and plain-language risk tiers ("Low" / "High").
- **Question B Concurrency**: Evaluated 100 concurrent async requests via `load_test.py`: **100/100 HTTP 200** (100% success, 100 rows persisted). Latency: median (p50) **1.43 s**, 95th percentile (p95) **2.15 s**. SQLite write serialization was the observed queuing bottleneck; production multi-user scaling requires PostgreSQL with connection pooling.
- **Question C Custom Retrieval**: Custom NumPy retriever matched library top-1 on Q2 (`who_diabetes_c009`) and Q3 (`who_hypertension_c001`), and top document on Q1. Raw cosine scores were higher ($\sim 0.50$ vs $\sim 0.25$) because unigram-only space ($|V|=1{,}544$) concentrates weights compared to library bigrams ($|V| \approx 3{,}700$).
- **Question C Level 3 Evaluation**:
  - **Prediction Accuracy**: **9 / 10 (90.0%)** | **QA Correctness**: **8 / 10 (80.0%)** | **Hallucinations**: **0**
  - **Retrieval Failure (Q04)**: Query *"early warning signs of diabetes"* failed to retrieve symptom chunk `who_diabetes_c003` (ranked #11, score 0.0583) due to lexical mismatch with heading *"Symptoms"*. Ground truth was absent from top-3 context.
  - **Generation Failure (Q02)**: Query *"hypertension blood pressure thresholds"* retrieved ground-truth chunk `who_hypertension_c001` in top-3 (rank #2, score 0.2805), but extractive synthesis selected general prevention sentences, omitting numerical 140/90 thresholds.
  - **Correct Refusals (Q08–Q10)**: Out-of-corpus queries (mRNA vaccines, Olympics, malaria) scored `0.0000` and triggered clean refusals without hallucinating.

---

### 3. AI Usage Disclosure & Weakness Encountered

- **AI Tools Used**:
  - **ChatGPT**: Used for technical planning, reasoning about architecture and assignment requirements, debugging/review support, documentation review, and interview/demo preparation.
  - **Antigravity**: Used for repository implementation assistance, code scaffolding, repetitive test writing, HTML/CSS structuring, running/verifying commands, and repository checks.
- **Concrete AI Weakness**: During Level 1 out-of-domain tuning, the AI generated an initial test with a default similarity threshold of `0.05`, assuming non-health queries would score near zero. However, the negative query *"Who won the 1994 FIFA World Cup soccer championship?"* unexpectedly scored `0.1071` because the token `"world"` matched boilerplate *"World Health Organization"* text across documents. I manually diagnosed the token analyzer weights and raised the refusal threshold to `0.12`, cleanly blocking non-health queries while preserving clinical matches ($\ge 0.18$).

---

### 4. Prediction-Before-Test Evidence & Repository Verification

- **Chronology Provenance**: Earlier prototype commit `955429a` contained predictions and results concurrently. Without rewriting Git history, a new final verifiable evaluation cycle was executed:
  - **Question B**: Predictions frozen in commit `f6ec003` $\rightarrow$ experiments run $\rightarrow$ results recorded in `626ff92`.
  - **Question C**: Predictions frozen in commit `c9b7f0f` $\rightarrow$ evaluation run $\rightarrow$ results recorded in `458e89d`.
- **Automated Verification**: **24/24 pytest tests pass** (5 API tests, 11 RAG pipeline tests, 8 custom NumPy TF-IDF tests). Zero secrets tracked.
- **Live Walkthrough**: Candidate can explain all components (Logistic Regression math, StandardScaler, SQLite WAL/raw SQL, TF-IDF formulas, cosine similarity, and retrieval vs. generation failure attribution) without AI assistance.
