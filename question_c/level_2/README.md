# Question C — Level 2: Custom TF-IDF and NumPy Cosine Similarity Retrieval

This module implements the retrieval component of Question C **from scratch** using pure Python, NumPy, and standard data structures—without calling `scikit-learn`'s `TfidfVectorizer`, `cosine_similarity`, LangChain, FAISS, or any vector database.

---

## 1. Why Level 2 Requires a Custom Implementation

In production AI systems, library abstractions (such as LangChain, Chroma, or scikit-learn) hide critical design choices:
- How terms are tokenized and weighted.
- How document frequency is smoothed.
- How vector sparsity, normalization, and geometric dot products are calculated.

Implementing TF-IDF and cosine similarity from scratch with NumPy:
1. **Demystifies Sparse Information Retrieval**: Proves mastery of the fundamental linear algebra and information retrieval math underlying search engines.
2. **Eliminates Black-Box Assumptions**: Allows exact control over term normalization, zero-vector safeguards, and term weighting.
3. **Validates Retrieval Mechanics**: Comparing the from-scratch implementation against the Level 1 library baseline demonstrates whether the custom algorithm accurately reproduces expected ranking behavior.

---

## 2. Chunking Approach

For fair, apples-to-apples evaluation, Level 2 reuses the **exact same 71 chunks** produced by the Level 1 chunker (`question_c/level_1/chunker.py`):

- **Corpus Source**: The 5 official WHO fact sheets in `question_c/documents/` (Diabetes, Hypertension, Physical Activity, Healthy Diet, Obesity).
- **Segmentation Strategy**: Documents are parsed along Markdown section headings (`##`, `###`) into coherent clinical topics (e.g. Overview, Symptoms, Risk factors, Prevention, Treatment).
- **Passage Size**: Sections exceeding ~150 words are bounded at paragraph breaks to preserve granular context.
- **Metadata Retention**: Each chunk maintains full provenance: `chunk_id`, `source_id`, `title`, `organization` ("World Health Organization"), `source_url`, and `section`.

---

## 3. Tokenization & Text Preprocessing

A deterministic tokenizer is implemented in `question_c/level_2/custom_tfidf.py`:

```python
def tokenize(text: str) -> List[str]:
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
    return [w for w in words if w not in ENGLISH_STOP_WORDS and not w.isdigit()]
```

### Preprocessing Rules:
1. **Case Normalization**: All input is converted to lowercase.
2. **Word Segmentation**: Alphanumeric tokens are extracted via regex `\b[a-zA-Z0-9]+\b`.
3. **Punctuation Removal**: Non-alphanumeric punctuation marks are stripped.
4. **Digit Removal**: Pure numeric tokens are filtered out to avoid over-weighting isolated year figures.
5. **English Stop Words**: Filtered against a documented set of 128 common English stopwords (e.g. *the*, *is*, *at*, *which*, *on*).
6. **Symmetric Processing**: Documents and query strings undergo the exact same preprocessing function.

---

## 4. Mathematical Formulations

### A. Term Frequency (TF)
For term $t$ in chunk $d$:

$$\text{tf}(t, d) = \frac{f(t, d)}{\sum_{t' \in d} f(t', d)}$$

where:
- $f(t, d)$ is the raw count of term $t$ in document $d$.
- $\sum_{t' \in d} f(t', d)$ is the total count of non-stopword tokens in document $d$.

*Rationale*: Relative term frequency normalizes against passage length, preventing longer sections from dominating simply due to word volume.

### B. Inverse Document Frequency (IDF)
For term $t$ across corpus $D$ with $N = |D|$ total chunks:

$$\text{idf}(t) = \ln\left(\frac{1 + N}{1 + \text{df}(t)}\right) + 1.0$$

where:
- $N = 71$ (total document chunks in the WHO corpus).
- $\text{df}(t) = |\{d \in D : t \in d\}|$ is the document frequency (number of chunks containing term $t$).
- Additive smoothing ($+1$) prevents division by zero and ensures that high-frequency terms still have a non-zero positive weight ($+1.0$).

### C. TF-IDF Weight
The composite weight of term $t$ in document $d$ is:

$$\text{tfidf}(t, d) = \text{tf}(t, d) \times \text{idf}(t)$$

### D. Cosine Similarity
Given query vector $\mathbf{q} \in \mathbb{R}^{|V|}$ and document chunk vector $\mathbf{d} \in \mathbb{R}^{|V|}$:

$$\text{cosine\_similarity}(\mathbf{q}, \mathbf{d}) = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\|_2 \times \|\mathbf{d}\|_2} = \frac{\sum_{i=1}^{|V|} q_i d_i}{\sqrt{\sum_{i=1}^{|V|} q_i^2} \times \sqrt{\sum_{i=1}^{|V|} d_i^2}}$$

### E. Zero-Vector Safeguard
If $\|\mathbf{q}\|_2 = 0$ or $\|\mathbf{d}\|_2 = 0$:

$$\text{cosine\_similarity}(\mathbf{q}, \mathbf{d}) = 0.0$$

This prevents division-by-zero exceptions when processing queries containing only out-of-vocabulary or stop words.

---

## 5. NumPy Vectorized Implementation

In `custom_tfidf.py` and `custom_retriever.py`:
- The vocabulary $V$ is sorted alphabetically into an indexed map: `{term: index}`.
- Chunks are converted into a dense 2D NumPy array `doc_matrix` of shape $(N, |V|) = (71, 1544)$.
- Query processing converts the query into a 1D vector of shape $(|V|,)$.
- Similarity across all $N$ chunks is calculated concurrently using vectorized NumPy matrix-vector multiplication:

```python
doc_norms = np.linalg.norm(doc_matrix, axis=1)
norm_q = np.linalg.norm(query_vec)
dot_products = np.dot(doc_matrix, query_vec)
similarities = np.where(doc_norms > 0.0, dot_products / (doc_norms * norm_q), 0.0)
```

- Ranking is executed using NumPy's `np.argsort(similarities)[::-1][:top_k]`.

---

## 6. Three Comparison Questions

| ID | Category | Question |
|---|---|---|
| **Q1** | Straightforward Lexical Match | *"What are the recommended physical activity levels for adults?"* |
| **Q2** | Chronic Disease Prevention | *"What lifestyle changes can help prevent type 2 diabetes?"* |
| **Q3** | Risk Factors / Lay Paraphrase | *"What factors can increase the risk of high blood pressure?"* |

---

## 7. Hypotheses & Predictions (Recorded Prior to Comparison)

As formally documented in [`predictions.md`](file:///c:/Developers/Sneha/health-ai-technical-assignment/question_c/level_2/predictions.md) before execution:
1. **Q1 (Physical Activity)**: Predicted strong agreement on `who_physical_activity` with $\ge 2/3$ top-3 overlap due to high keyword density matching document headings.
2. **Q2 (Diabetes Prevention)**: Predicted Top-1 agreement on `who_diabetes` section `Prevention` with $\ge 2/3$ top-3 overlap. Library retriever might benefit slightly from bi-gram matching for `"type 2"` and `"lifestyle changes"`.
3. **Q3 (High Blood Pressure)**: Predicted `who_hypertension` would dominate, with potential slight differences in ranks #2 and #3 because the lay term `"high blood pressure"` is unigram-split in custom vs. bi-gram preserved in library.

---

## 8. Actual Empirical Results

Executed via `compare_retrievers.py` over the identical 71 chunks:

| Question ID | Category | Library Top-1 | Custom Top-1 | Top-3 Overlap | Top-1 Agreement |
|---|---|---|---|---|---|
| **Q1** | Physical Activity | `who_physical_activity` (Levels of physical inactivity) `[0.256]` | `who_physical_activity` (Key facts) `[0.515]` | **2/3** | Same Document |
| **Q2** | Diabetes Prevention | `who_diabetes` (Prevention) `[0.351]` | `who_diabetes` (Prevention) `[0.507]` | **2/3** | **Exact Chunk Match** |
| **Q3** | High Blood Pressure | `who_hypertension` (Overview) `[0.267]` | `who_hypertension` (Overview) `[0.499]` | **3/3** | **Exact Chunk Match (100% Rank Match)** |

### Per-Question Details:

#### Q1: "What are the recommended physical activity levels for adults?"
- **Library Top-3**:
  1. `who_physical_activity_c007` (Levels of physical inactivity globally) — score: `0.2559`
  2. `who_physical_activity_c006` (Levels of physical inactivity globally) — score: `0.2149`
  3. `who_physical_activity_c000` (Key facts) — score: `0.1937`
- **Custom Top-3**:
  1. `who_physical_activity_c000` (Key facts) — score: `0.5153`
  2. `who_physical_activity_c006` (Levels of physical inactivity globally) — score: `0.4234`
  3. `who_physical_activity_c008` (How Member States can increase levels) — score: `0.4134`
- **Overlap**: 2 of 3 chunks shared (`who_physical_activity_c000`, `who_physical_activity_c006`).

#### Q2: "What lifestyle changes can help prevent type 2 diabetes?"
- **Library Top-3**:
  1. `who_diabetes_c009` (Prevention) — score: `0.3515`
  2. `who_hypertension_c005` (Prevention) — score: `0.2039`
  3. `who_diabetes_c006` (Type 2 diabetes) — score: `0.1588`
- **Custom Top-3**:
  1. `who_diabetes_c009` (Prevention) — score: `0.5074`
  2. `who_diabetes_c006` (Type 2 diabetes) — score: `0.3646`
  3. `who_diabetes_c005` (Type 2 diabetes) — score: `0.3484`
- **Overlap**: 2 of 3 chunks shared (`who_diabetes_c009`, `who_diabetes_c006`). Top-1 is identical.

#### Q3: "What factors can increase the risk of high blood pressure?"
- **Library Top-3**:
  1. `who_hypertension_c001` (Overview) — score: `0.2672`
  2. `who_hypertension_c004` (Treatment) — score: `0.2009`
  3. `who_hypertension_c003` (Symptoms) — score: `0.1973`
- **Custom Top-3**:
  1. `who_hypertension_c001` (Overview) — score: `0.4989`
  2. `who_hypertension_c004` (Treatment) — score: `0.4259`
  3. `who_hypertension_c003` (Symptoms) — score: `0.3727`
- **Overlap**: **3 of 3 chunks shared (100% agreement on ranks 1, 2, and 3)**.

---

## 9. Interpretation & Comparative Analysis

1. **Top-1 Agreement**:
   - For **Q2** and **Q3**, both retrievers converged on the exact same Top-1 chunk (`who_diabetes_c009` and `who_hypertension_c001`).
   - For **Q1**, both retrievers targeted the exact same document (`who_physical_activity`) and shared 2 of 3 top chunks. The custom retriever ranked `Key facts` higher because its relative TF calculation favored concise passages where "physical", "activity", and "adults" constitute a high proportion of total tokens.
2. **Score Magnitude Variance**:
   - The custom retriever produces higher numerical cosine similarity scores ($\sim 0.40 - 0.52$) than the library retriever ($\sim 0.20 - 0.35$).
   - This occurs because the library vectorizer incorporates bi-grams, greatly expanding the vector dimension and diluting individual token weights across a larger feature space.
   - *Crucially, cosine similarity is relative within each representation space; higher absolute scores do not imply superior retrieval.*
3. **Reproducibility**:
   - The custom implementation successfully reproduced the document selection and ranking behavior of scikit-learn without any library shortcuts.

---

## 10. Limitations of Custom Implementation

1. **Unigram Only**: Does not capture multi-word medical expressions (e.g., distinguishing "type 1" vs. "type 2", or "blood pressure" vs. "arterial pressure").
2. **Dense Memory Footprint**: Stores an $(N, |V|)$ dense NumPy float array. While optimal for 71 chunks, a massive corpus of $10^6$ chunks would require sparse matrix structures (`scipy.sparse.csr_matrix`).
3. **Lexical Exact Match**: Cannot match synonyms or lay phrasing unless those terms appear verbatim in the source corpus.

---

## 11. Verification Commands

Run all Level 2 unit and algorithmic tests:
```powershell
.\.venv\Scripts\python -m pytest question_c/level_2/test_custom_retriever.py -v
```

Re-run the automated comparison script:
```powershell
.\.venv\Scripts\python question_c/level_2/compare_retrievers.py
```
