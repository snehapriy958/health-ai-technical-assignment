# Level 3 Evaluation: Test Questions Specification

This document defines the 10 test questions designed to evaluate the Question C RAG question-answering assistant.

The corpus comprises **71 passages** extracted from 5 official World Health Organization (WHO) fact sheets:
1. `who_diabetes`
2. `who_hypertension`
3. `who_physical_activity`
4. `who_healthy_diet`
5. `who_obesity`

---

## Question Inventory

### Answerable Questions (7 Questions)

#### Question 1 (Q01)
- **Question**: *"How many minutes of moderate-intensity physical activity per week does WHO recommend for adults?"*
- **Category**: Direct numerical / guideline fact
- **Expected Status**: Answerable
- **Expected Source**: `who_physical_activity` (Section: *How much physical activity is recommended?* or *Key facts*)
- **Expected Core Answer**: At least 150–300 minutes of moderate-intensity physical activity per week (or at least 75–150 minutes of vigorous-intensity activity).
- **Why this question is useful**: Tests whether the retriever can precisely surface specific numerical health recommendations when high lexical overlap exists between query and text.

#### Question 2 (Q02)
- **Question**: *"What blood pressure thresholds define hypertension according to WHO?"*
- **Category**: Direct clinical diagnostic cutoff
- **Expected Status**: Answerable
- **Expected Source**: `who_hypertension` (Section: *Overview*)
- **Expected Core Answer**: Systolic blood pressure $\ge 140\text{ mmHg}$ and/or diastolic blood pressure $\ge 90\text{ mmHg}$ on two different days.
- **Why this question is useful**: Tests retrieval of essential clinical diagnostic cutoffs, a vital capability for a medical QA assistant.

#### Question 3 (Q03)
- **Category**: Dietary quantitative limit
- **Question**: *"What percentage of total daily energy intake should free sugars be limited to in a healthy diet?"*
- **Expected Status**: Answerable
- **Expected Source**: `who_healthy_diet` (Section: *Sugars*)
- **Expected Core Answer**: Less than 10% of total daily energy intake (with further reduction to 5% providing additional health benefits).
- **Why this question is useful**: Tests numerical dietary guideline retrieval within nested subsection headings (`WHO guidance on healthy diets > Sugars`).

#### Question 4 (Q04)
- **Question**: *"What early warning signs might indicate someone is developing diabetes?"*
- **Category**: Symptom identification with lexical paraphrase
- **Expected Status**: Answerable
- **Expected Source**: `who_diabetes` (Section: *Symptoms*)
- **Expected Core Answer**: Excessive thirst, frequent urination, blurred vision, fatigue, and unintentional weight loss.
- **Why this question is useful**: Tests how well the TF-IDF retriever bridges paraphrased language: the query asks for "early warning signs", whereas the document section uses "Symptoms".

#### Question 5 (Q05)
- **Question**: *"What BMI threshold classifies an adult as having obesity?"*
- **Category**: Anthropometric definition / clinical cutoff
- **Expected Status**: Answerable
- **Expected Source**: `who_obesity` (Section: *Definition of overweight and obesity > Adults*)
- **Expected Core Answer**: A Body Mass Index (BMI) greater than or equal to 30 ($\text{BMI} \ge 30$).
- **Why this question is useful**: Tests retrieval of concise clinical definitions distinguishing overweight ($\text{BMI} \ge 25$) from obesity ($\text{BMI} \ge 30$).

#### Question 6 (Q06)
- **Question**: *"How does reducing daily salt intake impact high blood pressure and healthy diet?"*
- **Category**: Cross-topic risk factor synthesis
- **Expected Status**: Answerable
- **Expected Source**: `who_hypertension` (Section: *Prevention*) and/or `who_healthy_diet` (Section: *Salt/sodium and potassium*)
- **Expected Core Answer**: Consuming less than 2 g of sodium per day (equivalent to less than 5 g of salt / about 1 teaspoon) lowers blood pressure and reduces cardiovascular disease risk.
- **Why this question is useful**: Tests whether the retriever can handle multi-document concepts present in both the hypertension and healthy diet fact sheets.

#### Question 7 (Q07)
- **Question**: *"What medications are commonly prescribed to lower blood glucose in people with type 2 diabetes?"*
- **Category**: Pharmacological intervention
- **Expected Status**: Answerable
- **Expected Source**: `who_diabetes` (Section: *Diagnosis and treatment*)
- **Expected Core Answer**: Metformin, sulfonylureas, sodium-glucose co-transporters type 2 (SGLT-2) inhibitors, and insulin injections.
- **Why this question is useful**: Tests retrieval of pharmacological classes using clinical terminology ("medications to lower blood glucose") against document text ("medicines to help manage their blood sugar levels").

---

### Unanswerable Questions (3 Questions)

#### Question 8 (Q08)
- **Question**: *"What is the primary mechanism of action of mRNA vaccines for infectious diseases?"*
- **Category**: Outside biomedical topic (Immunology / Vaccines)
- **Expected Status**: Unanswerable
- **Expected Source**: None (Corpus covers NCDs: diabetes, hypertension, activity, diet, obesity)
- **Expected Behavior**: Refusal ("The available WHO sources do not provide enough information to answer this question.")
- **Why this question is useful**: Tests whether the system correctly detects that an authentic medical topic is absent from this specific 5-document NCD corpus, rather than hallucinating vaccine immunology.

#### Question 9 (Q09)
- **Question**: *"Which country hosted the first Summer Olympic Games in the modern era?"*
- **Category**: Completely out-of-domain trivia (Sports History)
- **Expected Status**: Unanswerable
- **Expected Source**: None
- **Expected Behavior**: Refusal
- **Why this question is useful**: Tests baseline out-of-domain rejection where lexical overlap with public health guidance should be close to zero.

#### Question 10 (Q10)
- **Question**: *"What are the common symptoms and treatment options for malaria?"*
- **Category**: Communicable disease (Infectious disease outside corpus)
- **Expected Status**: Unanswerable
- **Expected Source**: None (Corpus covers noncommunicable lifestyle conditions only)
- **Expected Behavior**: Refusal
- **Why this question is useful**: Tests whether the system refuses an infectious disease question despite containing other medical documents discussing symptoms and medications.
