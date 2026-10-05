# Level 2 Retrieval Predictions

**Recorded Date**: 2026-10-06  
**Status**: Recorded PRIOR to executing `compare_retrievers.py`.

This document records the formal hypothesis and predictions for the comparison between:
- **Retriever A (Library)**: Scikit-learn `TfidfVectorizer` (sublinear TF, bi-grams enabled, L2-norm) + `cosine_similarity`.
- **Retriever B (Custom NumPy)**: From-scratch unigram relative TF ($\text{count}/\text{total}$), smoothed IDF ($\ln((1+N)/(1+\text{df})) + 1.0$), and manual NumPy cosine similarity.

Both retrievers operate over the **identical corpus of 71 WHO document chunks**.

---

## Question 1: Straightforward Lexical Match
**Query**: `"What are the recommended physical activity levels for adults?"`

- **Prediction**: 
  - Both retrievers will achieve Top-1 agreement on `who_physical_activity` (specifically section `How much physical activity is recommended?` or `Key facts`).
  - High Top-3 overlap ($\ge 2/3$ or $3/3$).
- **Why I expect the library/custom retriever to perform better**: 
  - The query terms (`recommended`, `physical`, `activity`, `adults`) exhibit high lexical overlap directly matching the document section title and paragraph text. 
  - Because keyword density is prominent, unigram matching in the custom retriever is expected to be sufficient to isolate the exact passage.
  - The library retriever's bi-grams (`"physical activity"`) will increase score confidence, but the underlying ranking should be nearly identical.
- **What evidence I will look for**: 
  - Presence of chunk `who_physical_activity` containing numerical guidelines (150 minutes of moderate-intensity activity / 75 minutes of vigorous activity).
  - High cosine similarity score ($> 0.20$) in both systems.

---

## Question 2: Specific Chronic Condition Prevention
**Query**: `"What lifestyle changes can help prevent type 2 diabetes?"`

- **Prediction**: 
  - Both retrievers will identify `who_diabetes` as the primary source.
  - Likely Top-1 agreement on `who_diabetes` section `Prevention` (or `Key facts`).
  - Top-3 overlap is predicted to be at least $2/3$.
- **Why I expect the library/custom retriever to perform better**: 
  - The library retriever has bi-grams enabled (`"type 2"`, `"lifestyle changes"`), which may give it higher discriminatory power to pinpoint the concise `Prevention` subsection over broader overview sections.
  - The custom unigram retriever relies on individual term frequencies (`lifestyle`, `changes`, `prevent`, `type`, `diabetes`), which might slightly elevate larger chunks containing multiple mentions of "diabetes".
- **What evidence I will look for**: 
  - Whether `who_diabetes` [Prevention] is ranked #1 in both or if the custom retriever ranks `who_diabetes` [Diagnosis and treatment] or [Overview] higher due to term count volume.
  - Whether lifestyle-related chunks from `who_healthy_diet` or `who_obesity` appear in ranks #2 or #3.

---

## Question 3: Paraphrase & Risk Factor Retrieval
**Query**: `"What factors can increase the risk of high blood pressure?"`

- **Prediction**: 
  - Both retrievers will surface `who_hypertension` in the top results, with likely focus on section `Risk factors` or `Overview`.
  - Moderate Top-3 overlap ($2/3$). Ranks #2 and #3 may diverge.
- **Why I expect the library/custom retriever to perform better**: 
  - The query uses the lay phrase `"high blood pressure"` rather than the medical term `"hypertension"`. 
  - In `who_hypertension`, the heading is "Risk factors", but the text defines both "high blood pressure" and "hypertension".
  - The library retriever's bi-gram `"blood pressure"` and `"high blood"` gives it strong phrase affinity to `who_hypertension`.
  - The custom retriever treats "blood" and "pressure" as isolated unigrams; because diet (salt) and obesity are also cited as causing high blood pressure across `who_healthy_diet` and `who_obesity`, the custom retriever might pull a chunk from those related documents into the top-3.
- **What evidence I will look for**: 
  - Top-1 agreement on `who_hypertension` [Risk factors] or [Overview].
  - Differences in 2nd and 3rd rank items (e.g. cross-topic retrieval from diet/obesity versus internal hypertension sections).
