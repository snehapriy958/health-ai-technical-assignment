# Level 3 Evaluation: Predictions

**Status**: Formally recorded PRIOR to running the evaluation script.  
**Evaluator**: Antigravity Assistant  
**Pipeline under test**: Level 1 RAG Pipeline (`LibraryTFIDFRetriever` + Grounding Prompt + LLM Client)

---

## Prediction Summary Table

| ID | Question | Expected Status | Predicted Retrieval Success | Predicted Final Correctness | Predicted Failure Type |
|---|---|---|:---:|:---:|---|
| **Q01** | *"How many minutes of moderate-intensity physical activity per week does WHO recommend for adults?"* | Answerable | YES | YES | No failure |
| **Q02** | *"What blood pressure thresholds define hypertension according to WHO?"* | Answerable | YES | YES | No failure |
| **Q03** | *"What percentage of total daily energy intake should free sugars be limited to in a healthy diet?"* | Answerable | YES | YES | No failure |
| **Q04** | *"What early warning signs might indicate someone is developing diabetes?"* | Answerable | NO | NO | **Retrieval failure** |
| **Q05** | *"What BMI threshold classifies an adult as having obesity?"* | Answerable | YES | YES | No failure |
| **Q06** | *"How does reducing daily salt intake impact high blood pressure and healthy diet?"* | Answerable | YES | YES | No failure |
| **Q07** | *"What medications are commonly prescribed to lower blood glucose in people with type 2 diabetes?"* | Answerable | YES | YES | No failure |
| **Q08** | *"What is the primary mechanism of action of mRNA vaccines for infectious diseases?"* | Unanswerable | NO | YES | **Expected refusal** |
| **Q09** | *"Which country hosted the first Summer Olympic Games in the modern era?"* | Unanswerable | NO | YES | **Expected refusal** |
| **Q10** | *"What are the common symptoms and treatment options for malaria?"* | Unanswerable | NO | YES | **Expected refusal** |

---

## Detailed Reasoning for Each Prediction

### Q01: Physical Activity Guidelines
- **Retrieval Prediction**: YES
- **Answer Prediction**: YES
- **Expected Failure Type**: No failure
- **Reasoning**: Heavy lexical overlap between query terms (`"minutes"`, `"moderate-intensity"`, `"physical activity"`, `"recommend"`, `"adults"`) and `who_physical_activity` chunk `How much physical activity is recommended?`. Cosine similarity will comfortably exceed the 0.12 threshold.

### Q02: Hypertension Diagnostic Cutoff
- **Retrieval Prediction**: YES
- **Answer Prediction**: YES
- **Expected Failure Type**: No failure
- **Reasoning**: The terms `"blood pressure"`, `"thresholds"`, and `"hypertension"` provide a direct match to `who_hypertension` [Overview], where 140/90 mmHg is explicitly defined.

### Q03: Dietary Sugar Limit
- **Retrieval Prediction**: YES
- **Answer Prediction**: YES
- **Expected Failure Type**: No failure
- **Reasoning**: `"percentage"`, `"daily energy intake"`, and `"free sugars"` have very high inverse document frequency in `who_healthy_diet` [Sugars]. Chunk isolation should be immediate.

### Q04: Diabetes Early Warning Signs (Paraphrase Challenge)
- **Retrieval Prediction**: NO
- **Answer Prediction**: NO
- **Expected Failure Type**: **Retrieval failure**
- **Reasoning**: The prompt uses lay paraphrase `"early warning signs"` instead of the clinical heading `"Symptoms"`. In a sparse TF-IDF model with no embeddings, `"early"`, `"warning"`, and `"signs"` do not match the section title. The retriever may match general diabetes chunks mentioning `"developing diabetes"` (e.g. risk factors or overview) rather than the actual symptom list chunk (`who_diabetes_c003`), causing the generated answer to lack the specific symptoms or fail to retrieve the right chunk.

### Q05: Obesity BMI Cutoff
- **Retrieval Prediction**: YES
- **Answer Prediction**: YES
- **Expected Failure Type**: No failure
- **Reasoning**: `"BMI threshold"`, `"adult"`, and `"obesity"` provide clear query-document alignment to `who_obesity` section *Definition of overweight and obesity > Adults*.

### Q06: Salt Reduction & Blood Pressure
- **Retrieval Prediction**: YES
- **Answer Prediction**: YES
- **Expected Failure Type**: No failure
- **Reasoning**: Mentions `"salt intake"`, `"high blood pressure"`, and `"healthy diet"`. Because these concepts appear prominently in both `who_hypertension` [Prevention] and `who_healthy_diet` [Salt/sodium], cross-topic retrieval should succeed.

### Q07: Type 2 Diabetes Medications
- **Retrieval Prediction**: YES
- **Answer Prediction**: YES
- **Expected Failure Type**: No failure
- **Reasoning**: Query terms `"medications"`, `"type 2 diabetes"`, and `"blood glucose"` will match `who_diabetes` [Diagnosis and treatment], which enumerates metformin, sulfonylureas, and SGLT-2 inhibitors.

### Q08: mRNA Vaccines (Unanswerable — Biomedical Out-of-Corpus)
- **Retrieval Prediction**: NO (Below threshold)
- **Answer Prediction**: YES (Refusal)
- **Expected Failure Type**: **Expected refusal**
- **Reasoning**: mRNA vaccines are not discussed in any of the 5 NCD documents. TF-IDF similarity should fall below 0.12, triggering the pipeline's refusal mechanism: *"The available WHO sources do not provide enough information to answer this question."*

### Q09: Modern Olympics (Unanswerable — General Trivia)
- **Retrieval Prediction**: NO (Below threshold)
- **Answer Prediction**: YES (Refusal)
- **Expected Failure Type**: **Expected refusal**
- **Reasoning**: Zero medical or health terminology overlap. Cosine score will be ~0.00, resulting in clean refusal.

### Q10: Malaria Symptoms & Treatment (Unanswerable — Excluded Disease)
- **Retrieval Prediction**: NO (Below threshold)
- **Answer Prediction**: YES (Refusal)
- **Expected Failure Type**: **Expected refusal**
- **Reasoning**: "Malaria" has 0 document frequency across the entire 71-chunk corpus. Although "symptoms" and "treatment" exist, without the key disease noun, max similarity should remain below the 0.12 threshold, preventing hallucination.
