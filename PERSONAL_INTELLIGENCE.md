# Personal Intelligence & Technical Reflection

**Project**: Health AI Technical Assignment (Questions B & C)
**Author**: Sneha Singh
**Date**: October 2026

---

## 1. Key Engineering Decisions & Reasoning

| Component | Chosen Approach | Rejected Alternative | Engineering Rationale & Evidence |
|---|---|---|---|
| **Question B: Model** | Logistic Regression with $L_2$ regularization on 5 normalized clinical features | Deep neural network or complex ensemble (e.g., XGBoost) | A clinical triage tool demands transparent coefficient inspectability, predicted probabilities, and risk tier classifications. Evaluated on the UCI Cleveland dataset, logistic regression produced clear, monotonic risk scores without overfitting risk on a small ($N \approx 300$) sample. |
| **Question B: Feature Scaling** | `StandardScaler` fitted strictly on training data | Unscaled raw values or min-max normalization | Clinical metrics have drastically different units (e.g., age $30\text{--}75$, cholesterol $150\text{--}500\text{ mg/dL}$). Standardization ensures gradient steps and $L_2$ penalty operate uniformly across dimensions without unit bias. |
| **Question B: Database & Storage** | SQLite with WAL mode & raw SQL parameterization | Heavy ORM (SQLAlchemy / Tortoise) or external PostgreSQL | SQLite requires zero infrastructure setup, runs in-process with minimal latency, and WAL mode guarantees concurrent read/write safety. Parameterized raw SQL (`AVG`, `COUNT`, `SUM`) eliminates ORM abstraction overhead and makes audit queries transparent during walkthroughs. |
| **Question B: Failure & Concurrency (Level 3)** | Empirical testing of missing model artifact (HTTP 503, degraded health), invalid string inputs (Pydantic HTTP 422 with audit logging), and 100 concurrent requests | Theoretical assumptions without simulated runtime faults | Validated fault isolation: missing artifacts fail fast with 503 instead of crashing, malformed payloads are logged with 422, and SQLite WAL mode handled 100 concurrent requests with 100% success. |
| **API & UI Framework** | FastAPI with Pydantic v2 schemas + embedded static HTML | Flask or separate React / Next.js frontend | FastAPI delivers automatic OpenAPI documentation, async concurrency, and strict schema validation out-of-the-box. Serving static HTML directly removes Node.js build dependencies while keeping UI deployment single-command. |
| **Question C: Corpus** | 5 official WHO fact sheets (Diabetes, Hypertension, Physical Activity, Healthy Diet, Obesity) | Web scrapes, Wikipedia, or commercial health blogs | Clinical QA assistants require authoritative ground truth. WHO documents provide peer-reviewed, internationally recognized clinical thresholds (e.g., blood pressure $\ge 140/90\text{ mmHg}$, BMI $\ge 30$). Segmented into 71 section-aware passages. |
| **Level 1 Retrieval** | `scikit-learn` `TfidfVectorizer` (sublinear TF, bi-grams) with $0.12$ cutoff | Vector database (Chroma, Pinecone) or sentence-transformers | A 71-chunk corpus does not justify vector database overhead. Sparse TF-IDF provides deterministic, microsecond retrieval with zero external service dependencies. An empirically selected $0.12$ threshold cleanly blocks out-of-domain queries. |
| **Level 2 Retrieval** | Custom Python & NumPy TF-IDF with smoothed IDF and vector dot-products | Calling `sklearn` or external retriever libraries | Writing the mathematical formulation from scratch demystifies vector spaces. Proves complete control over relative term frequency ($\text{count}/\text{total}$), smoothed IDF ($\ln((1+N)/(1+\text{df})) + 1.0$), and safe zero-norm cosine handling. |
| **Level 3 Evaluation** | 10 balanced test queries (7 answerable, 3 unanswerable) with pre-registered predictions | Ad-hoc unrecorded testing or manufactured metrics | Pre-recording hypotheses in `predictions.md` prior to execution enforces scientific rigor and exposes genuine lexical boundaries without post-hoc rationalization. |

---

## 2. Experimental Insights

1. **Level 2 Empirical Alignment**:
   - The custom NumPy retriever achieved **100% Top-1 exact chunk match on Q2 and Q3**, and selected the same document on Q1.
   - Cosine score magnitudes differed (custom $\sim 0.40\text{--}0.52$ vs. library $\sim 0.20\text{--}0.35$) because the library retriever incorporated bi-grams, expanding the feature space ($|V| \approx 3{,}700$ vs. $1{,}544$) and diluting vector energy. This confirmed that cosine similarity is strictly relative within a single representation space.
2. **70% Level 3 Prediction Accuracy**:
   - 7 of 10 pre-registered predictions matched empirical results.
   - 3/3 unanswerable questions (mRNA vaccines, Olympic games, malaria) were correctly refused (`0.0000` similarity score, zero hallucinations).
3. **The Q04 Failure Case (Lexical Gap)**:
   - Query: *"What early warning signs might indicate someone is developing diabetes?"*
   - Target passage: `who_diabetes_c003` (Symptoms: excessive thirst, urination, blurred vision).
   - Actual retrieval: `who_diabetes_c005` (Type 2 diabetes: *"early diagnosis is important to prevent..."*).
   - **Root Cause Analysis**: The ground-truth symptom passage ranked **#11** with a score of $0.0583$ because the lay term *"early warning signs"* had zero overlap with the heading *"Symptoms"*. Meanwhile, the word *"early"* matched *"early diagnosis"* in chunk `c005` (score $0.1786$). Because `who_diabetes_c003` was completely excluded from the top-3 context, the LLM could not possibly state the symptoms. **This proved a pure Retrieval Failure caused by sparse vocabulary mismatch.**

---

## 3. AI Usage Disclosure & Weakness Encountered

- **Disclosure**: AI coding assistant tooling was used for code scaffolding, repetitive test writing, HTML/CSS structuring, and documentation drafting.
- **Concrete AI Weakness**: During Level 1 out-of-domain testing, the AI generated an initial test with a default similarity threshold of `0.05`, assuming non-health queries would score near zero. However, when evaluating the negative test query *"Who won the 1994 FIFA World Cup soccer championship?"*, the test unexpectedly failed because the query matched *"World Health Organization"* on the single token `"world"`, generating a cosine score of `0.1071`. The AI did not anticipate that corpus boilerplate creates non-zero background noise. I had to manually inspect the token analyzer, diagnose the overlap on `"world"`, and adjust the minimum threshold to `0.12` to cleanly separate legitimate clinical matches ($\ge 0.18$) from accidental single-token overlap.

---

## 4. Verification Performed

- **Automated Test Suites**: Executed and passed 24 unit and integration tests across the codebase:
  - `question_b/level_2/tests/test_api.py` (5 passed)
  - `question_c/level_1/tests/test_rag.py` (11 passed)
  - `question_c/level_2/test_custom_retriever.py` (8 passed)
- **Live HTTP & Browser Verification**: Verified FastAPI endpoints (`POST /predict`, `GET /stats`, `POST /ask`, `GET /health`) using `httpx` client scripts and interactive browser sessions on ports 8000/8012.
- **Empirical Reproducibility**: Executed `compare_retrievers.py`, `run_evaluation.py`, and `analyze_failure.py` without errors, confirming all markdown reports reflect real execution traces.
- **Secrets Audit**: Confirmed zero API keys or credentials exist in tracked code.

---

## 5. Live Walkthrough Readiness Checklist

I can explain the following technical concepts from first principles without assistance:
- **Logistic Regression**: Linear combination $z = \mathbf{w}^T\mathbf{x} + b$ mapped through the sigmoid function $\sigma(z) = \frac{1}{1 + e^{-z}}$ to yield bounded probabilities $[0, 1]$, optimized via log-loss.
- **StandardScaler**: Transforming features via $z = \frac{x - \mu}{\sigma}$ so every predictor has mean 0 and variance 1, preventing high-magnitude features from dominating weights.
- **FastAPI / Pydantic Validation**: How type annotations enforce runtime schema compliance, reject malformed payloads with HTTP 422/400, and generate OpenAPI specifications.
- **SQLite Concurrency & Raw SQL**: Using Write-Ahead Logging (WAL) to enable concurrent readers alongside serialized writers, and executing parameterized SQL aggregations (`AVG`, `COUNT`, `SUM`) safely.
- **TF-IDF & Smoothed IDF**: Relative term frequency $\text{tf}(t, d) = \frac{f(t, d)}{|d|}$ multiplied by smoothed inverse document frequency $\text{idf}(t) = \ln\left(\frac{1 + N}{1 + \text{df}(t)}\right) + 1.0$ to down-weight ubiquitous terms and boost discriminative keywords.
- **Cosine Similarity**: Inner product divided by Euclidean norms $\frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$, including the necessity of checking $\|\mathbf{u}\| = 0$ or $\|\mathbf{v}\| = 0$ to avoid division by zero.
- **Retrieval vs. Generation Failures**: How inspecting the prompt context separates upstream search misses (ground truth absent from context) from downstream LLM hallucination (ground truth present but ignored or contradicted).
- **The Q04 Failure**: Exactly why lexical synonym mismatch (*"early warning signs"* vs. *"symptoms"*) causes sparse retrieval to degrade, motivating dense semantic embeddings for production systems.
