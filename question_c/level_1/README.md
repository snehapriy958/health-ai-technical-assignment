# Question C — Level 1: Public Health RAG Assistant

A question-answering assistant grounded strictly in authoritative public health fact sheets published by the **World Health Organization (WHO)**.

This implementation represents **Level 1** of Question C, providing a simple, interpretable, and reproducible Retrieval-Augmented Generation (RAG) baseline with source attribution and no vector database.

---

## 1. Architecture

```text
       ┌────────────────────────┐
       │   User Question        │
       │  (Web UI or POST /ask) │
       └───────────┬────────────┘
                   │
                   ▼
       ┌────────────────────────┐
       │ Library Retriever      │
       │ (Scikit-Learn TF-IDF   │
       │ + Cosine Similarity)   │
       └───────────┬────────────┘
                   │ Top-k relevant chunks (similarity ≥ threshold)
                   ▼
       ┌────────────────────────┐
       │ Context Formatter      │
       │ • Injects WHO metadata │
       │ • Strict grounding prompt
       └───────────┬────────────┘
                   │ Context + Question
                   ▼
       ┌────────────────────────┐
       │ LLM Client             │
       │ (Gemini / OpenAI / Mock│
       └───────────┬────────────┘
                   │ Generated response
                   ▼
       ┌────────────────────────┐
       │ Answer + Verified      │
       │ Source Attribution     │
       └────────────────────────┘
```

### Component Breakdown
1. **Document Corpus Loader (`chunker.py`)**:
   - Parses the 5 WHO text documents in `question_c/documents/`.
   - Extracts structured metadata headers (`SOURCE_ID`, `TITLE`, `ORGANIZATION`, `SOURCE_URL`, `TOPIC`).
   - Splits documents along section headers (`##`, `###`) into 70 self-contained passages while keeping metadata attached to every chunk.
2. **Library Retriever (`retriever.py`)**:
   - Uses `sklearn.feature_extraction.text.TfidfVectorizer` with english stop words, sublinear term-frequency scaling, and bi-grams.
   - Computes cosine similarity between user query and chunk vectors.
   - Enforces a minimum similarity threshold (`0.12`) to eliminate irrelevant noise and reject out-of-domain questions.
3. **LLM Client (`llm.py`)**:
   - Lightweight direct HTTP client using `httpx` (no heavy wrapper libraries).
   - Supports Google Gemini (`GEMINI_API_KEY`) and OpenAI (`OPENAI_API_KEY`).
   - Includes a deterministic `MockLLMClient` (`MOCK_LLM=1`) for offline verification, CI/CD testing, and environments without active API keys.
4. **RAG Pipeline Orchestrator (`rag_pipeline.py`)**:
   - Manages query validation, retrieval execution, prompt construction, and source deduplication.
5. **Web Service & UI (`app.py` & `static/index.html`)**:
   - FastAPI server exposing `POST /ask`, `GET /health`, and serving the interactive web interface at `GET /`.

---

## 2. Document Corpus

The corpus consists exclusively of the 5 official WHO fact sheets collected in `question_c/documents/`:

| Source ID | Topic | Official Title | Source URL | Chunks |
|---|---|---|---|---|
| `who_diabetes` | Diabetes | Diabetes | [WHO Diabetes Fact Sheet](https://www.who.int/news-room/fact-sheets/detail/diabetes) | 13 |
| `who_hypertension` | Hypertension | Hypertension | [WHO Hypertension Fact Sheet](https://www.who.int/news-room/fact-sheets/detail/hypertension) | 10 |
| `who_physical_activity` | Physical Activity | Physical activity | [WHO Physical Activity Fact Sheet](https://www.who.int/news-room/fact-sheets/detail/physical-activity) | 11 |
| `who_healthy_diet` | Healthy Diet | Healthy diet | [WHO Healthy Diet Fact Sheet](https://www.who.int/news-room/fact-sheets/detail/healthy-diet) | 16 |
| `who_obesity` | Obesity and Overweight | Obesity and overweight | [WHO Obesity Fact Sheet](https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight) | 20 |
| **Total** | — | — | — | **70** |

All text is factual public health guidance (symptoms, diagnostic cutoffs, prevention strategies, dietary recommendations). No personal health data is present.

---

## 3. Retrieval Approach in Level 1

In accordance with the assignment roadmap:
- **Off-the-shelf Library Retriever**: Scikit-learn's `TfidfVectorizer` + `cosine_similarity`.
- **Vocabulary & Weighting**:
  - Unigram and bigram tokenization (`ngram_range=(1, 2)`).
  - Standard English stop words removal.
  - Sublinear term frequency scaling ($1 + \log(\text{tf})$) to prevent high-frequency repeated words from skewing relevance.
  - L2-normalization for cosine distance equivalence.
- **Relevance Filtering**: If the top similarity score is below `0.12`, the retriever treats the question as out-of-domain and returns an empty chunk list, preventing hallucinations.

*(Note: The custom from-scratch TF-IDF and NumPy cosine similarity implementation is reserved specifically for Level 2.)*

---

## 4. LLM Configuration

The application supports standard cloud LLMs via environment variables without hard-coded secrets:

1. **Google Gemini** (Default recommended):
   ```bash
   export GEMINI_API_KEY="your-api-key"
   # Optional model override (default: gemini-1.5-flash)
   export GEMINI_MODEL="gemini-1.5-flash"
   ```
2. **OpenAI**:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   # Optional model override (default: gpt-4o-mini)
   export OPENAI_MODEL="gpt-4o-mini"
   ```
3. **Local Mock Mode (Offline Verification / Testing)**:
   ```bash
   export MOCK_LLM="1"
   ```
   If no API key is configured and `MOCK_LLM` is not set, the API returns a descriptive `HTTP 400 Bad Request` instructing the operator to provide an API key.

---

## 5. Why This Approach Was Chosen

1. **Clarity & Interview Defensibility**: Every component (parsing, TF-IDF matrices, cosine angles, context prompt, HTTP API) is straightforward and easy to explain end-to-end without black-box dependencies.
2. **Zero Vector Database Overhead**: Avoids heavy external services (e.g. Chroma, Pinecone, FAISS) for a compact 70-chunk corpus where sparse retrieval runs in milliseconds.
3. **Strict Medical Grounding**: The prompt forces the LLM to admit when the WHO sources do not provide sufficient information, eliminating clinical hallucinations.

---

## 6. How Source Attribution Works

Every chunk in the retrieval index carries permanent metadata tags. When chunks are selected for context generation:
1. The prompt prepends the source metadata:
   ```text
   [Source ID: who_diabetes | Document: Diabetes | Section: Prevention | Relevance Score: 0.285]
   ```
2. The API response formats an explicit `sources` array:
   ```json
   {
     "answer": "...",
     "sources": [
       {
         "source_id": "who_diabetes",
         "title": "Diabetes",
         "organization": "World Health Organization",
         "url": "https://www.who.int/news-room/fact-sheets/detail/diabetes",
         "section": "Prevention",
         "relevance_score": 0.2851
       }
     ]
   }
   ```
3. The web frontend renders clickable citation badges linking directly to the official WHO URL.

---

## 7. Limitations

1. **Vocabulary Mismatch (Lexical Gap)**: TF-IDF relies on exact term overlap. If a user asks *"How do I keep my blood pressure normal?"* without using terms like *"hypertension"* or *"prevent"*, lexical score may be lower than a dense semantic embedding model.
2. **Fixed Chunk Boundaries**: Sections split by headings may occasionally separate a question premise from a multi-paragraph explanation across section borders.
3. **No Cross-Chunk Multi-Hop Reasoning**: Answers requiring synthesis across three disparate documents rely on all three chunks being independently retrieved in the top-$k$.

---

## 8. How to Run the Application

### 1. Set Up Environment

Activate the virtual environment:
```powershell
.\.venv\Scripts\Activate.ps1
```

Set your LLM API key (or enable mock mode for testing):
```powershell
# Option A: Google Gemini
$env:GEMINI_API_KEY = "your-gemini-key"

# Option B: OpenAI
$env:OPENAI_API_KEY = "your-openai-key"

# Option C: Offline / Mock Mode
$env:MOCK_LLM = "1"
```

### 2. Start the Server

```powershell
.\.venv\Scripts\python -m uvicorn question_c.level_1.app:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Access the Web Interface

Open your browser at:
```text
http://127.0.0.1:8000
```

### 4. Query via API (cURL / PowerShell)

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/ask" `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body '{"question": "What are some ways to reduce the risk of diabetes?"}' | ConvertTo-Json -Depth 4
```

### 5. Run the Test Suite

```powershell
.\.venv\Scripts\python -m pytest question_c/level_1/tests/test_rag.py -v
```

---

## 9. Manual Example Questions & Ground-Truth Attribution

These 5 questions can be directly answered using our collected WHO documents:

### Example 1: Diabetes Prevention
- **Question**: *"What are some lifestyle changes to help prevent type 2 diabetes?"*
- **Expected WHO Answer**: Reaching and keeping a healthy body weight, staying physically active with at least 150 minutes of moderate exercise each week, eating a healthy diet while avoiding sugar and saturated fats, and not smoking tobacco.
- **Source**: `who_diabetes` | **Title**: Diabetes | **Section**: Prevention | [WHO Diabetes URL](https://www.who.int/news-room/fact-sheets/detail/diabetes)

### Example 2: Hypertension Diagnostic Cutoff
- **Question**: *"What blood pressure measurement confirms a diagnosis of hypertension?"*
- **Expected WHO Answer**: Hypertension is diagnosed if, when measured on two different days, systolic blood pressure readings on both days is $\ge$ 140 mmHg and/or diastolic blood pressure readings on both days is $\ge$ 90 mmHg.
- **Source**: `who_hypertension` | **Title**: Hypertension | **Section**: Overview | [WHO Hypertension URL](https://www.who.int/news-room/fact-sheets/detail/hypertension)

### Example 3: Adult Physical Activity Recommendation
- **Question**: *"How much physical activity is recommended per week for adults?"*
- **Expected WHO Answer**: Adults should undertake at least 150 minutes of moderate-intensity aerobic activity per week, or 75 minutes of vigorous-intensity aerobic physical activity per week, along with muscle-strengthening activities on 2 or more days each week.
- **Source**: `who_physical_activity` | **Title**: Physical activity | **Section**: Key facts & How much physical activity is recommended? | [WHO Physical Activity URL](https://www.who.int/news-room/fact-sheets/detail/physical-activity)

### Example 4: Dietary Sugar Limits
- **Question**: *"What is the WHO recommendation for daily consumption of free sugars?"*
- **Expected WHO Answer**: Free sugars should be limited to less than 10% of total daily energy intake (approximately 50 g or 12 teaspoons for a 2,000 calorie diet). Reducing to less than 5% provides additional health benefits.
- **Source**: `who_healthy_diet` | **Title**: Healthy diet | **Section**: Sugars | [WHO Healthy Diet URL](https://www.who.int/news-room/fact-sheets/detail/healthy-diet)

### Example 5: Adult Obesity Classification
- **Question**: *"How is obesity classified by Body Mass Index (BMI) in adults?"*
- **Expected WHO Answer**: In adults, a BMI greater than or equal to 25 is classified as overweight, and a BMI greater than or equal to 30 is classified as obesity.
- **Source**: `who_obesity` | **Title**: Obesity and overweight | **Section**: Definition of overweight and obesity / Adults | [WHO Obesity URL](https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight)

### Out-of-Domain Example (Refusal Test)
- **Question**: *"What is the capital city of France?"*
- **Expected Response**: *"The available WHO sources do not provide enough information to answer this question."*
- **Sources**: `[]` (Empty)
