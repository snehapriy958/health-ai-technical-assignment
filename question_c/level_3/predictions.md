# Question C — Level 3 Final Predictions

**Seed**: `S = 48`
**Evaluation cycle**: FINAL PREDICTION-BEFORE-TEST CYCLE

> [!IMPORTANT]
> **Chronology Statement**:
> "These predictions are frozen and committed to GitHub before the final Level 3 evaluation is executed. They represent my pre-test reasoning, not conclusions derived from the evaluation results."

---

## Prediction Summary Table

| ID | Retrieval Prediction | Final Prediction | Confidence |
|---|----------------------|------------------|------------|
| **Q01** | YES | Correct | High |
| **Q02** | YES | Correct | High |
| **Q03** | YES | Correct | High |
| **Q04** | NO / likely failure | Incorrect/incomplete | Medium |
| **Q05** | YES | Correct | High |
| **Q06** | YES | Correct | High |
| **Q07** | YES | Correct | High |
| **Q08** | NO | Correct refusal | High |
| **Q09** | NO | Correct refusal | High |
| **Q10** | NO | Correct refusal | Medium-High |

---

## Detailed Pre-Test Predictions (Q01 – Q10)

### Q01
- **Question**: "How many minutes of moderate-intensity physical activity per week does WHO recommend for adults?"
- **Pre-test evidence source**: `question_c/documents/who_physical_activity.txt`
- **Relevant sections**:
  - How much physical activity is recommended?
  - Levels of physical inactivity globally
- **Evidence**:
  The WHO physical activity document explicitly states that adults should meet at least 150 minutes of moderate-intensity physical activity per week.
- **Prediction**:
  - Retrieval: YES
  - Final answer: CORRECT
- **Reasoning**:
  The query has strong lexical overlap with the source, including "moderate-intensity", "physical activity", "week", and "adults". The requested value is explicitly present in the corpus. Because the Level 1 retriever uses TF-IDF with unigrams and bigrams, I expect the correct chunk to rank highly.
- **Confidence**: HIGH

---

### Q02
- **Question**: "What blood pressure thresholds define hypertension according to WHO?"
- **Pre-test evidence source**: `question_c/documents/who_hypertension.txt`
- **Relevant section**:
  - Overview
- **Evidence**:
  The WHO document explicitly defines hypertension as blood pressure of 140/90 mmHg or higher and explains the systolic >=140 and/or diastolic >=90 diagnostic threshold.
- **Prediction**:
  - Retrieval: YES
  - Final answer: CORRECT
- **Reasoning**:
  The question directly contains the major terms "blood pressure" and "hypertension". The requested thresholds are explicitly present in the hypertension document. I therefore expect successful retrieval and grounded answer generation.
- **Confidence**: HIGH

---

### Q03
- **Question**: "What percentage of total daily energy intake should free sugars be limited to in a healthy diet?"
- **Pre-test evidence source**: `question_c/documents/who_healthy_diet.txt`
- **Relevant section**:
  - WHO guidance on healthy diets
  - Sugars
- **Evidence**:
  The source explicitly states that consumption of free sugars should be limited to less than 10% of total daily energy intake.
- **Prediction**:
  - Retrieval: YES
  - Final answer: CORRECT
- **Reasoning**:
  The question closely matches the terminology of the "Sugars" section, including "free sugars" and "total daily energy intake". The exact requested percentage is explicitly present in the source.
- **Confidence**: HIGH

---

### Q04
- **Question**: "What early warning signs might indicate someone is developing diabetes?"
- **Pre-test evidence source**: `question_c/documents/who_diabetes.txt`
- **Relevant sections**:
  - Symptoms
  - Type 2 diabetes
- **Evidence**:
  The diabetes document contains symptoms such as increased thirst, frequent urination, blurred vision, tiredness and unintentional weight loss. However, the document primarily uses the term "symptoms", while the query uses "early warning signs".
- **Prediction**:
  - Retrieval: NO / likely retrieval failure
  - Final answer: INCORRECT OR INCOMPLETE
- **Reasoning**:
  The relevant information exists in the corpus, but the wording differs. The Level 1 retriever is sparse TF-IDF rather than semantic embeddings. The phrase "early warning signs" may not match the source wording "symptoms" strongly enough for the correct chunk to reach the top 3. If the correct passage is not retrieved, the LLM will not have the necessary evidence to answer completely.
- **Confidence**: MEDIUM

---

### Q05
- **Question**: "What BMI threshold classifies an adult as having obesity?"
- **Pre-test evidence source**: `question_c/documents/who_obesity.txt`
- **Relevant section**:
  - Definition of overweight and obesity
  - Adults
- **Evidence**:
  The WHO source explicitly states that for adults:
  - overweight = BMI >= 25
  - obesity = BMI >= 30
- **Prediction**:
  - Retrieval: YES
  - Final answer: CORRECT
- **Reasoning**:
  The question has strong lexical overlap with the source terms "BMI", "adult", and "obesity". The requested threshold is explicitly present.
- **Confidence**: HIGH

---

### Q06
- **Question**: "How does reducing daily salt intake impact high blood pressure and healthy diet?"
- **Pre-test evidence sources**:
  - `question_c/documents/who_healthy_diet.txt` (Section: *Salt/sodium and potassium*)
  - `question_c/documents/who_hypertension.txt` (Sections: *Risk factors* and *Prevention*)
- **Evidence**:
  The healthy-diet document states that high sodium/salt intake is associated with increased blood pressure and provides salt intake guidance. The hypertension document identifies a high-salt diet as a risk factor and recommends reducing salt.
- **Prediction**:
  - Retrieval: YES
  - Final answer: CORRECT
- **Reasoning**:
  The question contains strong matching terms such as "salt intake", "high blood pressure", and "healthy diet". Two documents contain directly relevant evidence, so I expect useful context to be retrieved and the LLM to explain the relationship correctly.
- **Confidence**: HIGH

---

### Q07
- **Question**: "What medications are commonly prescribed to lower blood glucose in people with type 2 diabetes?"
- **Pre-test evidence source**: `question_c/documents/who_diabetes.txt`
- **Relevant section**:
  - Diagnosis and treatment
- **Evidence**:
  The source explicitly discusses medicines for type 2 diabetes and lists examples including metformin, sulfonylureas, SGLT-2 inhibitors, and insulin.
- **Prediction**:
  - Retrieval: YES
  - Final answer: CORRECT
- **Reasoning**:
  The question directly matches the source's terminology around type 2 diabetes, blood glucose and medication. The requested information is explicitly present, so I expect retrieval and grounded generation to succeed.
- **Confidence**: HIGH

---

### Q08
- **Question**: "What is the primary mechanism of action of mRNA vaccines for infectious diseases?"
- **Pre-test evidence source**: The five-document corpus in `question_c/documents/`
- **Corpus topics**:
  - Diabetes
  - Hypertension
  - Physical Activity
  - Healthy Diet
  - Obesity
- **Evidence**:
  No document in the corpus covers mRNA vaccines or vaccine mechanisms.
- **Prediction**:
  - Retrieval: NO
  - Final answer: CORRECT REFUSAL
- **Reasoning**:
  The question is outside the scope of the corpus. I expect the query not to produce sufficiently relevant retrieval results and the RAG pipeline to use its explicit insufficient-information refusal instead of using outside knowledge.
- **Confidence**: HIGH

---

### Q09
- **Question**: "Which country hosted the first Summer Olympic Games in the modern era?"
- **Pre-test evidence source**: The five-document WHO corpus in `question_c/documents/`
- **Evidence**:
  None of the five documents contains historical information about the Olympic Games.
- **Prediction**:
  - Retrieval: NO
  - Final answer: CORRECT REFUSAL
- **Reasoning**:
  The question is unrelated to all documents in the bounded corpus. Therefore I expect no relevant chunk to pass the retrieval threshold and the system should refuse rather than answer using external knowledge.
- **Confidence**: HIGH

---

### Q10
- **Question**: "What are the common symptoms and treatment options for malaria?"
- **Pre-test evidence source**:
  - The five-document WHO corpus in `question_c/documents/`
  - `question_c/level_1/retriever.py`
- **Evidence**:
  There is no malaria document in the corpus. Some unrelated documents contain generic terms such as "symptoms" and "treatment", so lexical overlap is possible even though malaria itself is not covered.
- **Prediction**:
  - Retrieval: NO
  - Final answer: CORRECT REFUSAL
- **Reasoning**:
  Although generic words such as "symptoms" and "treatment" occur in some documents, none of the five documents covers malaria. I expect the disease-specific query to remain below the similarity threshold and the system to refuse rather than use outside medical knowledge.
- **Confidence**: MEDIUM-HIGH
