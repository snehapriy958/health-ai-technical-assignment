# Question C — Level 3 Final Results

**Seed**: `S = 48`
**Prediction commit**: `c9b7f0f` (`docs: freeze Question C Level 3 predictions`)
**Evaluation cycle**: Final empirical evaluation executed strictly after prediction commit.

> [!NOTE]
> These results were produced by running the final evaluation runner script strictly *after*
> committing and pushing the pre-evaluation predictions to GitHub.

---

## 1. Final Results Table

| ID | My Prediction | Actual Retrieval | Actual Outcome | Prediction Match | Evidence |
|---|---|:---:|---|:---:|---|
| **Q01** | Correct | YES | Correct | ✅ Match | Top: `who_physical_activity_c006` (score: 0.2236) |
| **Q02** | Correct | YES | Generation failure | ❌ Mismatch | Top: `who_hypertension_c006` (score: 0.3105) |
| **Q03** | Correct | YES | Correct | ✅ Match | Top: `who_healthy_diet_c005` (score: 0.3744) |
| **Q04** | Incorrect/incomplete | NO | Retrieval failure | ✅ Match | Top: `who_diabetes_c005` (score: 0.1786) |
| **Q05** | Correct | YES | Correct | ✅ Match | Top: `who_obesity_c004` (score: 0.2025) |
| **Q06** | Correct | YES | Correct | ✅ Match | Top: `who_hypertension_c006` (score: 0.1968) |
| **Q07** | Correct | YES | Correct | ✅ Match | Top: `who_diabetes_c010` (score: 0.3072) |
| **Q08** | Correct refusal | NO | Correct refusal | ✅ Match | Top: `None (Filtered)` (score: 0.0000) |
| **Q09** | Correct refusal | NO | Correct refusal | ✅ Match | Top: `None (Filtered)` (score: 0.0000) |
| **Q10** | Correct refusal | NO | Correct refusal | ✅ Match | Top: `None (Filtered)` (score: 0.0000) |

---

## 2. Evaluation Metrics Summary

- **Prediction Accuracy**: **9 / 10 (90.0%)**
  *(Proportion of pre-test predictions that correctly anticipated the actual system outcome)*
- **QA Correctness**: **8 / 10 (80.0%)**
  *(Proportion of questions where the RAG assistant delivered an authoritative factual answer or correct refusal)*

> [!IMPORTANT]
> **Metric Distinction Notice**: Prediction accuracy measures pre-experiment hypothesis quality, whereas QA correctness measures the operational performance of the RAG assistant. They are distinct metrics.

---

## 3. Failure Taxonomy Breakdown

- **Retrieval Failures**: 1
- **Generation Failures**: 1
- **Correct Answers**: 5
- **Correct Refusals**: 3
- **Hallucinations / False Positives**: 0

---

## 4. Detailed Per-Question Outputs and Source Attribution

### Question Q01: "How many minutes of moderate-intensity physical activity per week does WHO recommend for adults?"
- **Expected Status**: Answerable
- **Target Evidence Requirement**: WHO Physical Activity fact sheet states at least 150 minutes of moderate-intensity physical activity per week.
- **My Pre-Test Prediction**: Correct (Retrieval: YES)
- **Actual Retrieval**: YES (Top score: `0.2236`)
- **Actual Outcome**: **Correct** (Prediction Match: ✅ Match)
- **Retrieved Chunks**: `who_physical_activity_c006, who_hypertension_c005, who_diabetes_c009`
- **Generated Answer**:
> According to the World Health Organization:
>
> - WHO regularly monitors trends in physical inactivity. A recent study (1) found that nearly one third (31%) of the world’s adult population, 1.8 billion adults, are physically inactive. That is, they do not meet the global recommendations of at least 150 minutes of moderate-intensity physical activity per week. This is an increase of 5 percentage points between 2010 and 2022. If this trend continues, the proportion of adults not meeting recommended levels of physical activity is projected to rise to 35% by 2030.
>
> - Globally, there are notable age and gender differences in levels of physical inactivity.
>
> - After 60 years of age physical inactivity levels increase in both men and women.
>
> - Lifestyle changes can help lower high blood pressure and can help anyone with hypertension. Many who make these changes will still need to take medicine.

- **Verified Source Attribution**:
  - `who_physical_activity` (Physical activity — *Levels of physical inactivity globally*): relevance `0.2236`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/physical-activity)
  - `who_hypertension` (Hypertension — *Prevention*): relevance `0.1344`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/hypertension)
  - `who_diabetes` (Diabetes — *Prevention*): relevance `0.1336`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/diabetes)

### Question Q02: "What blood pressure thresholds define hypertension according to WHO?"
- **Expected Status**: Answerable
- **Target Evidence Requirement**: WHO Hypertension fact sheet defines hypertension as systolic >=140 and/or diastolic >=90 mmHg.
- **My Pre-Test Prediction**: Correct (Retrieval: YES)
- **Actual Retrieval**: YES (Top score: `0.3105`)
- **Actual Outcome**: **Generation failure** (Prediction Match: ❌ Mismatch)
- **Retrieved Chunks**: `who_hypertension_c006, who_hypertension_c001, who_hypertension_c003`
- **Generated Answer**:
> According to the World Health Organization:
>
> - Reducing hypertension prevents heart attack, stroke and kidney damage, as well as other health problems.
>
> - Reduce the risks of hypertension by:
>
> - regularly checking blood pressure
>
> - treating high blood pressure

- **Verified Source Attribution**:
  - `who_hypertension` (Hypertension — *Prevention*): relevance `0.3105`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/hypertension)
  - `who_hypertension` (Hypertension — *Overview*): relevance `0.2805`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/hypertension)
  - `who_hypertension` (Hypertension — *Symptoms*): relevance `0.2591`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/hypertension)

### Question Q03: "What percentage of total daily energy intake should free sugars be limited to in a healthy diet?"
- **Expected Status**: Answerable
- **Target Evidence Requirement**: WHO Healthy Diet fact sheet limits free sugars to less than 10% of total daily energy intake.
- **My Pre-Test Prediction**: Correct (Retrieval: YES)
- **Actual Retrieval**: YES (Top score: `0.3744`)
- **Actual Outcome**: **Correct** (Prediction Match: ✅ Match)
- **Retrieved Chunks**: `who_healthy_diet_c005, who_healthy_diet_c007, who_healthy_diet_c003`
- **Generated Answer**:
> According to the World Health Organization:
>
> - The consumption of free sugars should be limited to less than 10% of total daily energy intake, which is equivalent to 50 g (or about 12 level teaspoons) for a person of healthy body weight consuming about 2000 calories per day. Limiting further to 5% or less of total daily energy intake may provide additional health benefits.
>
> - Consumption of free sugars should be limited throughout the life course. Free sugars include monosaccharides and disaccharides (e.g. sucrose, fructose, glucose) added to foods and beverages by the manufacturer, cook or consumer, and sugars naturally present in honey, syrups, fruit juices and fruit juice concentrates.
>
> - Reducing consumption of free sugars (and maintaining low levels of intake) should be accomplished without the use of non-sugar sweeteners. Examples of common non-sugar sweeteners include acesulfame K, aspartame, advantame, cyclamates, neotame, saccharin, sucralose, stevia and stevia derivatives.
>
> - Proteins provide the building blocks for many of the structural elements of the body, such as muscle, as well as functional molecules such as hormones and enzymes. Protein intake at 10–15% of total daily energy intake is generally sufficient to meet the needs of adults (approximately 50–75 grams for a person of healthy body weight consuming about 2000 calories per day).

- **Verified Source Attribution**:
  - `who_healthy_diet` (Healthy diet — *Sugars*): relevance `0.3744`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/healthy-diet)
  - `who_healthy_diet` (Healthy diet — *Protein*): relevance `0.1869`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/healthy-diet)
  - `who_healthy_diet` (Healthy diet — *Carbohydrates*): relevance `0.1690`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/healthy-diet)

### Question Q04: "What early warning signs might indicate someone is developing diabetes?"
- **Expected Status**: Answerable
- **Target Evidence Requirement**: WHO Diabetes fact sheet section 'Symptoms' (chunk who_diabetes_c003) lists thirst, frequent urination, tiredness.
- **My Pre-Test Prediction**: Incorrect/incomplete (Retrieval: NO / likely failure)
- **Actual Retrieval**: NO (Top score: `0.1786`)
- **Actual Outcome**: **Retrieval failure** (Prediction Match: ✅ Match)
- **Retrieved Chunks**: `who_diabetes_c005`
- **Generated Answer**:
> According to the World Health Organization:
>
> - Type 2 diabetes affects how your body uses sugar (glucose) for energy. It stops the body from using insulin properly, which can lead to high levels of blood sugar if not treated.
>
> - Over time, type 2 diabetes can cause serious damage to the body, especially nerves and blood vessels.
>
> - Type 2 diabetes is often preventable. Factors that contribute to developing type 2 diabetes include being overweight, not getting enough exercise, and genetics.
>
> - Early diagnosis is important to prevent the worst effects of type 2 diabetes. The best way to detect diabetes early is to get regular check-ups and blood tests with a healthcare provider.

- **Verified Source Attribution**:
  - `who_diabetes` (Diabetes — *Type 2 diabetes*): relevance `0.1786`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/diabetes)

### Question Q05: "What BMI threshold classifies an adult as having obesity?"
- **Expected Status**: Answerable
- **Target Evidence Requirement**: WHO Obesity fact sheet defines adult obesity as BMI >= 30.
- **My Pre-Test Prediction**: Correct (Retrieval: YES)
- **Actual Retrieval**: YES (Top score: `0.2025`)
- **Actual Outcome**: **Correct** (Prediction Match: ✅ Match)
- **Retrieved Chunks**: `who_obesity_c004, who_obesity_c002`
- **Generated Answer**:
> According to the World Health Organization:
>
> - obesity is a BMI greater than or equal to 30.
>
> - The BMI categories for defining obesity vary by age and gender for adults, adolescents, children and infants.

- **Verified Source Attribution**:
  - `who_obesity` (Obesity and overweight — *Adults*): relevance `0.2025`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight)
  - `who_obesity` (Obesity and overweight — *Overview*): relevance `0.1604`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight)

### Question Q06: "How does reducing daily salt intake impact high blood pressure and healthy diet?"
- **Expected Status**: Answerable
- **Target Evidence Requirement**: WHO Healthy Diet and Hypertension fact sheets link salt reduction to lowering blood pressure.
- **My Pre-Test Prediction**: Correct (Retrieval: YES)
- **Actual Retrieval**: YES (Top score: `0.1968`)
- **Actual Outcome**: **Correct** (Prediction Match: ✅ Match)
- **Retrieved Chunks**: `who_hypertension_c006, who_healthy_diet_c008, who_hypertension_c001`
- **Generated Answer**:
> According to the World Health Organization:
>
> - Reducing hypertension prevents heart attack, stroke and kidney damage, as well as other health problems.
>
> - reducing and managing stress
>
> - regularly checking blood pressure
>
> - treating high blood pressure

- **Verified Source Attribution**:
  - `who_hypertension` (Hypertension — *Prevention*): relevance `0.1968`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/hypertension)
  - `who_healthy_diet` (Healthy diet — *Salt/sodium and potassium*): relevance `0.1800`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/healthy-diet)
  - `who_hypertension` (Hypertension — *Overview*): relevance `0.1741`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/hypertension)

### Question Q07: "What medications are commonly prescribed to lower blood glucose in people with type 2 diabetes?"
- **Expected Status**: Answerable
- **Target Evidence Requirement**: WHO Diabetes fact sheet 'Diagnosis and treatment' lists metformin, sulfonylureas, SGLT-2 inhibitors, insulin.
- **My Pre-Test Prediction**: Correct (Retrieval: YES)
- **Actual Retrieval**: YES (Top score: `0.3072`)
- **Actual Outcome**: **Correct** (Prediction Match: ✅ Match)
- **Retrieved Chunks**: `who_diabetes_c010, who_diabetes_c006, who_diabetes_c004`
- **Generated Answer**:
> According to the World Health Organization:
>
> - Early diagnosis can be accomplished through relatively inexpensive testing of blood glucose. People with type 1 diabetes need insulin injections for survival.
>
> - One of the most important ways to treat diabetes is to keep a healthy lifestyle.
>
> - Some people with type 2 diabetes will need to take medicines to help manage their blood sugar levels. These can include insulin injections or other medicines. Some examples include:
>
> - sodium-glucose co-transporters type 2 (SGLT-2) inhibitors.

- **Verified Source Attribution**:
  - `who_diabetes` (Diabetes — *Diagnosis and treatment*): relevance `0.3072`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/diabetes)
  - `who_diabetes` (Diabetes — *Type 2 diabetes*): relevance `0.1552`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/diabetes)
  - `who_diabetes` (Diabetes — *Type 1 diabetes*): relevance `0.1544`, [WHO Source URL](https://www.who.int/news-room/fact-sheets/detail/diabetes)

### Question Q08: "What is the primary mechanism of action of mRNA vaccines for infectious diseases?"
- **Expected Status**: Unanswerable
- **Target Evidence Requirement**: Out-of-corpus biomedical topic; mRNA vaccines are completely absent from the 5-document NCD corpus.
- **My Pre-Test Prediction**: Correct refusal (Retrieval: NO)
- **Actual Retrieval**: NO (Top score: `0.0000`)
- **Actual Outcome**: **Correct refusal** (Prediction Match: ✅ Match)
- **Retrieved Chunks**: `None (Below threshold 0.12)`
- **Generated Answer**:
> The available WHO sources do not provide enough information to answer this question.

- **Verified Source Attribution**:
  - *No sources attributed (Clean out-of-corpus refusal)*

### Question Q09: "Which country hosted the first Summer Olympic Games in the modern era?"
- **Expected Status**: Unanswerable
- **Target Evidence Requirement**: Out-of-corpus general trivia; sports history is completely absent from the 5-document NCD corpus.
- **My Pre-Test Prediction**: Correct refusal (Retrieval: NO)
- **Actual Retrieval**: NO (Top score: `0.0000`)
- **Actual Outcome**: **Correct refusal** (Prediction Match: ✅ Match)
- **Retrieved Chunks**: `None (Below threshold 0.12)`
- **Generated Answer**:
> The available WHO sources do not provide enough information to answer this question.

- **Verified Source Attribution**:
  - *No sources attributed (Clean out-of-corpus refusal)*

### Question Q10: "What are the common symptoms and treatment options for malaria?"
- **Expected Status**: Unanswerable
- **Target Evidence Requirement**: Out-of-corpus communicable disease; malaria is completely absent from the 5-document NCD corpus.
- **My Pre-Test Prediction**: Correct refusal (Retrieval: NO)
- **Actual Retrieval**: NO (Top score: `0.0000`)
- **Actual Outcome**: **Correct refusal** (Prediction Match: ✅ Match)
- **Retrieved Chunks**: `None (Below threshold 0.12)`
- **Generated Answer**:
> The available WHO sources do not provide enough information to answer this question.

- **Verified Source Attribution**:
  - *No sources attributed (Clean out-of-corpus refusal)*
