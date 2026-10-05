# Level 3 Evaluation Results

This document contains the empirical evaluation results of running all 10 test questions through the Level 1 RAG pipeline.

## 1. Comprehensive Results Table

| ID | Question | Expected Status | Top Score | Retrieved Source(s) | Top Section | Correct? | Outcome / Failure Type |
|---|---|---|:---:|---|---|:---:|---|
| Q01 | "How many minutes of moderate-intensity physical activity per week does WHO recommend for adults?" | Answerable | 0.2236 | `who_physical_activity`, `who_hypertension`, `who_diabetes` | Levels of physical inactivity globally | ✅ YES | No failure |
| Q02 | "What blood pressure thresholds define hypertension according to WHO?" | Answerable | 0.3105 | `who_hypertension` | Prevention | ❌ NO | Retrieval failure (Missing target passage) |
| Q03 | "What percentage of total daily energy intake should free sugars be limited to in a healthy diet?" | Answerable | 0.3744 | `who_healthy_diet` | Sugars | ✅ YES | No failure |
| Q04 | "What early warning signs might indicate someone is developing diabetes?" | Answerable | 0.1786 | `who_diabetes` | Type 2 diabetes | ❌ NO | Retrieval failure (Missing target passage) |
| Q05 | "What BMI threshold classifies an adult as having obesity?" | Answerable | 0.2025 | `who_obesity` | Adults | ✅ YES | No failure |
| Q06 | "How does reducing daily salt intake impact high blood pressure and healthy diet?" | Answerable | 0.1968 | `who_hypertension`, `who_healthy_diet` | Prevention | ❌ NO | Retrieval failure (Missing target passage) |
| Q07 | "What medications are commonly prescribed to lower blood glucose in people with type 2 diabetes?" | Answerable | 0.3072 | `who_diabetes` | Diagnosis and treatment | ❌ NO | Retrieval failure (Missing target passage) |
| Q08 | "What is the primary mechanism of action of mRNA vaccines for infectious diseases?" | Unanswerable | 0.0000 | None (Filtered) | N/A | ✅ YES | Expected refusal |
| Q09 | "Which country hosted the first Summer Olympic Games in the modern era?" | Unanswerable | 0.0000 | None (Filtered) | N/A | ✅ YES | Expected refusal |
| Q10 | "What are the common symptoms and treatment options for malaria?" | Unanswerable | 0.0000 | None (Filtered) | N/A | ✅ YES | Expected refusal |

---

## 2. Comparison: Predictions vs. Actual Results

| ID | Predicted Outcome | Actual Outcome | Predicted Correctness | Actual Correctness | Prediction Match? |
|---|---|---|:---:|:---:|:---:|
| Q01 | No failure | No failure | YES | YES | ✅ Correct |
| Q02 | No failure | Retrieval failure (Missing target passage) | YES | NO | ❌ Incorrect |
| Q03 | No failure | No failure | YES | YES | ✅ Correct |
| Q04 | Retrieval failure | Retrieval failure (Missing target passage) | NO | NO | ✅ Correct |
| Q05 | No failure | No failure | YES | YES | ✅ Correct |
| Q06 | No failure | Retrieval failure (Missing target passage) | YES | NO | ❌ Incorrect |
| Q07 | No failure | Retrieval failure (Missing target passage) | YES | NO | ❌ Incorrect |
| Q08 | Expected refusal | Expected refusal | YES | YES | ✅ Correct |
| Q09 | Expected refusal | Expected refusal | YES | YES | ✅ Correct |
| Q10 | Expected refusal | Expected refusal | YES | YES | ✅ Correct |

**Prediction Accuracy**: **7 / 10 (70.0%)**

---

## 3. Detailed Per-Question Outputs

### Question Q01: "How many minutes of moderate-intensity physical activity per week does WHO recommend for adults?"
- **Expected Status**: Answerable  
- **Top Similarity Score**: `0.2236`  
- **Retrieved Chunks**: `who_physical_activity_c006, who_hypertension_c005, who_diabetes_c009`  
- **Retrieved Sections**: `Levels of physical inactivity globally, Prevention`  
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
- **Outcome Classification**: **No failure**  
- **Prediction Was**: Accurate

### Question Q02: "What blood pressure thresholds define hypertension according to WHO?"
- **Expected Status**: Answerable  
- **Top Similarity Score**: `0.3105`  
- **Retrieved Chunks**: `who_hypertension_c006, who_hypertension_c001, who_hypertension_c003`  
- **Retrieved Sections**: `Prevention, Overview, Symptoms`  
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
- **Outcome Classification**: **Retrieval failure (Missing target passage)**  
- **Prediction Was**: Inaccurate

### Question Q03: "What percentage of total daily energy intake should free sugars be limited to in a healthy diet?"
- **Expected Status**: Answerable  
- **Top Similarity Score**: `0.3744`  
- **Retrieved Chunks**: `who_healthy_diet_c005, who_healthy_diet_c007, who_healthy_diet_c003`  
- **Retrieved Sections**: `Sugars, Protein, Carbohydrates`  
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
- **Outcome Classification**: **No failure**  
- **Prediction Was**: Accurate

### Question Q04: "What early warning signs might indicate someone is developing diabetes?"
- **Expected Status**: Answerable  
- **Top Similarity Score**: `0.1786`  
- **Retrieved Chunks**: `who_diabetes_c005`  
- **Retrieved Sections**: `Type 2 diabetes`  
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
- **Outcome Classification**: **Retrieval failure (Missing target passage)**  
- **Prediction Was**: Accurate

### Question Q05: "What BMI threshold classifies an adult as having obesity?"
- **Expected Status**: Answerable  
- **Top Similarity Score**: `0.2025`  
- **Retrieved Chunks**: `who_obesity_c004, who_obesity_c002`  
- **Retrieved Sections**: `Adults, Overview`  
- **Generated Answer**:
> According to the World Health Organization:
> 
> - obesity is a BMI greater than or equal to 30.
> 
> - The BMI categories for defining obesity vary by age and gender for adults, adolescents, children and infants.
- **Outcome Classification**: **No failure**  
- **Prediction Was**: Accurate

### Question Q06: "How does reducing daily salt intake impact high blood pressure and healthy diet?"
- **Expected Status**: Answerable  
- **Top Similarity Score**: `0.1968`  
- **Retrieved Chunks**: `who_hypertension_c006, who_healthy_diet_c008, who_hypertension_c001`  
- **Retrieved Sections**: `Prevention, Salt/sodium and potassium, Overview`  
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
- **Outcome Classification**: **Retrieval failure (Missing target passage)**  
- **Prediction Was**: Inaccurate

### Question Q07: "What medications are commonly prescribed to lower blood glucose in people with type 2 diabetes?"
- **Expected Status**: Answerable  
- **Top Similarity Score**: `0.3072`  
- **Retrieved Chunks**: `who_diabetes_c010, who_diabetes_c006, who_diabetes_c004`  
- **Retrieved Sections**: `Diagnosis and treatment, Type 2 diabetes, Type 1 diabetes`  
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
- **Outcome Classification**: **Retrieval failure (Missing target passage)**  
- **Prediction Was**: Inaccurate

### Question Q08: "What is the primary mechanism of action of mRNA vaccines for infectious diseases?"
- **Expected Status**: Unanswerable  
- **Top Similarity Score**: `0.0000`  
- **Retrieved Chunks**: `None`  
- **Retrieved Sections**: `None`  
- **Generated Answer**:
> The available WHO sources do not provide enough information to answer this question.
- **Outcome Classification**: **Expected refusal**  
- **Prediction Was**: Accurate

### Question Q09: "Which country hosted the first Summer Olympic Games in the modern era?"
- **Expected Status**: Unanswerable  
- **Top Similarity Score**: `0.0000`  
- **Retrieved Chunks**: `None`  
- **Retrieved Sections**: `None`  
- **Generated Answer**:
> The available WHO sources do not provide enough information to answer this question.
- **Outcome Classification**: **Expected refusal**  
- **Prediction Was**: Accurate

### Question Q10: "What are the common symptoms and treatment options for malaria?"
- **Expected Status**: Unanswerable  
- **Top Similarity Score**: `0.0000`  
- **Retrieved Chunks**: `None`  
- **Retrieved Sections**: `None`  
- **Generated Answer**:
> The available WHO sources do not provide enough information to answer this question.
- **Outcome Classification**: **Expected refusal**  
- **Prediction Was**: Accurate

