# Question C — Level 3: AI Independent Pre-Test Prediction Review

**Status**: Independent AI-assisted review of pre-test evidence, conducted prior to executing the evaluation.
**Corpus**: 5 official World Health Organization (WHO) fact sheets (71 passages)
**Retrieval System Under Test**: Level 1 TF-IDF Retriever (`TfidfVectorizer`, unigrams + bigrams, sublinear TF, threshold $0.12$, top-$k=3$)

> [!IMPORTANT]
> **Independent Review Notice**:
> This document is an independent AI-assisted review of the pre-test evidence. It was created separately from the user's prediction freeze (`predictions.md`) and must not be treated as part of the user's original prediction. Neither review has access to post-test evaluation results; both are formulated purely from the corpus texts and retriever architecture.

---

## Comparative Pre-Test Review Table

| ID | Query Subject | User Retrieval Pred. | AI Retrieval Pred. | User Outcome Pred. | AI Outcome Pred. | Agreement Status |
|:---:|---|:---:|:---:|:---:|:---:|:---:|
| **Q01** | Physical activity recommendation | YES | YES | Correct | Correct | **Full Agreement** |
| **Q02** | Hypertension diagnostic threshold | YES | YES | Correct | Correct | **Full Agreement** |
| **Q03** | Free sugars dietary limit | YES | YES | Correct | Correct | **Full Agreement** |
| **Q04** | Early warning signs of diabetes | NO (Failure) | NO (Failure) | Incorrect | Incorrect | **Full Agreement** |
| **Q05** | Adult obesity BMI cutoff | YES | YES | Correct | Correct | **Full Agreement** |
| **Q06** | Salt reduction and blood pressure | YES | YES | Correct | Correct | **Full Agreement** |
| **Q07** | Type 2 diabetes medications | YES | YES | Correct | Correct | **Full Agreement** |
| **Q08** | mRNA vaccine mechanisms | NO (Refusal) | NO (Refusal) | Correct Refusal | Correct Refusal | **Full Agreement** |
| **Q09** | First modern Olympic Games host | NO (Refusal) | NO (Refusal) | Correct Refusal | Correct Refusal | **Full Agreement** |
| **Q10** | Malaria symptoms and treatment | NO (Refusal) | NO (Refusal) | Correct Refusal | Correct Refusal | **Full Agreement** |

---

## Detailed Question-by-Question Pre-Test Evidence Analysis

### Question 1 (Q01)
- **Question**: *"How many minutes of moderate-intensity physical activity per week does WHO recommend for adults?"*
- **Pre-Test Evidence Source**: `question_c/documents/who_physical_activity.txt` (Section: *Levels of physical inactivity globally* / *How much physical activity is recommended?*)
- **Textual Evidence**: Explicitly states adults should do at least 150 minutes of moderate-intensity physical activity per week.
- **AI Predicted Retrieval**: **YES** (Score will comfortably exceed $0.12$).
- **AI Predicted Final Outcome**: **Correct**
- **AI Reasoning**: Multiple high-IDF keywords (`"moderate-intensity"`, `"physical activity"`, `"150 minutes"`) align directly with document text.
- **Agreement with User**: **Agreed** on retrieval and answer correctness.

---

### Question 2 (Q02)
- **Question**: *"What blood pressure thresholds define hypertension according to WHO?"*
- **Pre-Test Evidence Source**: `question_c/documents/who_hypertension.txt` (Section: *Overview*)
- **Textual Evidence**: Explicitly defines hypertension as systolic blood pressure $\ge 140\text{ mmHg}$ and/or diastolic $\ge 90\text{ mmHg}$.
- **AI Predicted Retrieval**: **YES**
- **AI Predicted Final Outcome**: **Correct**
- **AI Reasoning**: Core clinical terms `"blood pressure"` and `"hypertension"` provide strong unigram and bigram features in `who_hypertension_c001`.
- **Agreement with User**: **Agreed** on retrieval and answer correctness.

---

### Question 3 (Q03)
- **Question**: *"What percentage of total daily energy intake should free sugars be limited to in a healthy diet?"*
- **Pre-Test Evidence Source**: `question_c/documents/who_healthy_diet.txt` (Section: *Sugars*)
- **Textual Evidence**: States that free sugars should be limited to less than 10% of total daily energy intake.
- **AI Predicted Retrieval**: **YES**
- **AI Predicted Final Outcome**: **Correct**
- **AI Reasoning**: The phrase `"free sugars"` and `"daily energy intake"` is highly specific to chunk `who_healthy_diet_c005`.
- **Agreement with User**: **Agreed** on retrieval and answer correctness.

---

### Question 4 (Q04)
- **Question**: *"What early warning signs might indicate someone is developing diabetes?"*
- **Pre-Test Evidence Source**: `question_c/documents/who_diabetes.txt` (Section: *Symptoms*)
- **Textual Evidence**: The document lists symptoms (excessive thirst, frequent urination, blurred vision, fatigue), but places them under the heading `## Symptoms`.
- **AI Predicted Retrieval**: **NO / High Risk of Retrieval Failure**
- **AI Predicted Final Outcome**: **Incorrect or Incomplete**
- **AI Reasoning**: Sparse TF-IDF lacks semantic embeddings and cannot equate the lay phrase `"early warning signs"` with `"symptoms"`. Instead, the query term `"early"` strongly matches `"early diagnosis"` in section `Type 2 diabetes` (`who_diabetes_c005`), which will outscore the actual symptoms passage (`who_diabetes_c003`).
- **Agreement with User**: **Agreed** on predicted retrieval failure due to the vocabulary mismatch.

---

### Question 5 (Q05)
- **Question**: *"What BMI threshold classifies an adult as having obesity?"*
- **Pre-Test Evidence Source**: `question_c/documents/who_obesity.txt` (Section: *Definition of overweight and obesity > Adults*)
- **Textual Evidence**: Explicitly states BMI $\ge 25$ is overweight and BMI $\ge 30$ is obesity for adults.
- **AI Predicted Retrieval**: **YES**
- **AI Predicted Final Outcome**: **Correct**
- **AI Reasoning**: Query terms `"BMI"`, `"adult"`, and `"obesity"` align exactly with the section title and text in `who_obesity_c004`.
- **Agreement with User**: **Agreed** on retrieval and answer correctness.

---

### Question 6 (Q06)
- **Question**: *"How does reducing daily salt intake impact high blood pressure and healthy diet?"*
- **Pre-Test Evidence Sources**:
  - `question_c/documents/who_healthy_diet.txt` (Section: *Salt/sodium and potassium*)
  - `question_c/documents/who_hypertension.txt` (Sections: *Risk factors* and *Prevention*)
- **Textual Evidence**: Both fact sheets emphasize that reducing salt intake to $<5\text{ g/day}$ lowers blood pressure and risk of cardiovascular disease.
- **AI Predicted Retrieval**: **YES**
- **AI Predicted Final Outcome**: **Correct**
- **AI Reasoning**: Query spans dual topics with high term frequencies across both documents. Top-3 will contain relevant guidance.
- **Agreement with User**: **Agreed** on retrieval and answer correctness.

---

### Question 7 (Q07)
- **Question**: *"What medications are commonly prescribed to lower blood glucose in people with type 2 diabetes?"*
- **Pre-Test Evidence Source**: `question_c/documents/who_diabetes.txt` (Section: *Diagnosis and treatment*)
- **Textual Evidence**: Lists metformin, sulfonylureas, SGLT-2 inhibitors, and insulin injections.
- **AI Predicted Retrieval**: **YES**
- **AI Predicted Final Outcome**: **Correct**
- **AI Reasoning**: Key terms `"medications"`, `"type 2 diabetes"`, and `"blood glucose"` have direct lexical representation in section *Diagnosis and treatment*.
- **Agreement with User**: **Agreed** on retrieval and answer correctness.

---

### Question 8 (Q08)
- **Question**: *"What is the primary mechanism of action of mRNA vaccines for infectious diseases?"*
- **Pre-Test Evidence Source**: None (Corpus is restricted to noncommunicable lifestyle conditions)
- **Textual Evidence**: Zero coverage of vaccines or mRNA biotechnology.
- **AI Predicted Retrieval**: **NO** (Score below $0.12$).
- **AI Predicted Final Outcome**: **Correct Refusal**
- **AI Reasoning**: Out-of-corpus query lacking domain terms. Expected score $0.0000$, cleanly triggering explicit refusal.
- **Agreement with User**: **Agreed** on expected refusal.

---

### Question 9 (Q09)
- **Question**: *"Which country hosted the first Summer Olympic Games in the modern era?"*
- **Pre-Test Evidence Source**: None
- **Textual Evidence**: Zero sports history content.
- **AI Predicted Retrieval**: **NO** (Score below $0.12$).
- **AI Predicted Final Outcome**: **Correct Refusal**
- **AI Reasoning**: Completely unrelated trivia query. Guaranteed zero similarity score.
- **Agreement with User**: **Agreed** on expected refusal.

---

### Question 10 (Q10)
- **Question**: *"What are the common symptoms and treatment options for malaria?"*
- **Pre-Test Evidence Source**: None (Malaria is an infectious tropical disease not present in corpus)
- **Textual Evidence**: Words `"symptoms"` and `"treatment"` exist in the corpus, but the disease noun `"malaria"` has 0 document frequency.
- **AI Predicted Retrieval**: **NO** (Score below $0.12$).
- **AI Predicted Final Outcome**: **Correct Refusal**
- **AI Reasoning**: Even if generic stop-like medical words match weakly, the absence of `"malaria"` should keep maximum cosine similarity below the $0.12$ cutoff, enforcing safe refusal.
- **Agreement with User**: **Agreed** on expected refusal.
