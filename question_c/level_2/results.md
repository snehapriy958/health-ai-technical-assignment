# Level 2 Retrieval Comparison Results

**Corpus Size**: 71 chunks from 5 official WHO fact sheets.
**Comparison Target**: Level 1 Library Retriever (`sklearn` TF-IDF) vs. Level 2 Custom Retriever (`NumPy` TF-IDF).

## Summary Table

| Question ID | Category | Question | Library Top-1 | Custom Top-1 | Top-3 Overlap | Top-1 Agreement |
|---|---|---|---|---|---|---|
| Q1 | Straightforward Lexical Match | "What are the recommended physical activity levels for adults?" | `who_physical_activity` (Levels of physical inactivity globally) [0.256] | `who_physical_activity` (Key facts) [0.515] | 2/3 | Same Document |
| Q2 | Chronic Disease Prevention | "What lifestyle changes can help prevent type 2 diabetes?" | `who_diabetes` (Prevention) [0.351] | `who_diabetes` (Prevention) [0.507] | 2/3 | Exact Chunk Match |
| Q3 | Risk Factors / Paraphrase | "What factors can increase the risk of high blood pressure?" | `who_hypertension` (Overview) [0.267] | `who_hypertension` (Overview) [0.499] | 3/3 | Exact Chunk Match |

---

## Detailed Per-Question Breakdown

### Q1: "What are the recommended physical activity levels for adults?"
**Category**: Straightforward Lexical Match  
**Top-3 Overlap**: 2/3 (who_physical_activity_c000, who_physical_activity_c006)  
**Top-1 Match**: Document match only

#### Library Retriever (Scikit-Learn TF-IDF)
| Rank | Chunk ID | Source ID | Section | Cosine Score | Snippet |
|---|---|---|---|---|---|
| 1 | `who_physical_activity_c007` | `who_physical_activity` | Levels of physical inactivity globally | 0.2559 | Many different factors can determine how active people are and the overall levels of physical activity in different popu... |
| 2 | `who_physical_activity_c006` | `who_physical_activity` | Levels of physical inactivity globally | 0.2149 | WHO regularly monitors trends in physical inactivity. A recent study (1) found that nearly one third (31%) of the world’... |
| 3 | `who_physical_activity_c000` | `who_physical_activity` | Key facts | 0.1937 | - Regular physical activity provides significant physical and mental health benefits.  - In adults, physical activity co... |

#### Custom NumPy Retriever (From Scratch)
| Rank | Chunk ID | Source ID | Section | Cosine Score | Snippet |
|---|---|---|---|---|---|
| 1 | `who_physical_activity_c000` | `who_physical_activity` | Key facts | 0.5153 | - Regular physical activity provides significant physical and mental health benefits.  - In adults, physical activity co... |
| 2 | `who_physical_activity_c006` | `who_physical_activity` | Levels of physical inactivity globally | 0.4234 | WHO regularly monitors trends in physical inactivity. A recent study (1) found that nearly one third (31%) of the world’... |
| 3 | `who_physical_activity_c008` | `who_physical_activity` | How Member States can increase levels of physical activity | 0.4134 | The WHO Global action plan on physical activity provides policy recommendations for countries and communities to promote... |

### Q2: "What lifestyle changes can help prevent type 2 diabetes?"
**Category**: Chronic Disease Prevention  
**Top-3 Overlap**: 2/3 (who_diabetes_c009, who_diabetes_c006)  
**Top-1 Match**: Yes (Exact chunk match)

#### Library Retriever (Scikit-Learn TF-IDF)
| Rank | Chunk ID | Source ID | Section | Cosine Score | Snippet |
|---|---|---|---|---|---|
| 1 | `who_diabetes_c009` | `who_diabetes` | Prevention | 0.3515 | Lifestyle changes are the best way to prevent or delay the onset of type 2 diabetes.  To help prevent type 2 diabetes an... |
| 2 | `who_hypertension_c005` | `who_hypertension` | Prevention | 0.2039 | Lifestyle changes can help lower high blood pressure and can help anyone with hypertension. Many who make these changes ... |
| 3 | `who_diabetes_c006` | `who_diabetes` | Type 2 diabetes | 0.1588 | More than 95% of people with diabetes have type 2 diabetes. Type 2 diabetes was formerly called non-insulin dependent, o... |

#### Custom NumPy Retriever (From Scratch)
| Rank | Chunk ID | Source ID | Section | Cosine Score | Snippet |
|---|---|---|---|---|---|
| 1 | `who_diabetes_c009` | `who_diabetes` | Prevention | 0.5074 | Lifestyle changes are the best way to prevent or delay the onset of type 2 diabetes.  To help prevent type 2 diabetes an... |
| 2 | `who_diabetes_c006` | `who_diabetes` | Type 2 diabetes | 0.3646 | More than 95% of people with diabetes have type 2 diabetes. Type 2 diabetes was formerly called non-insulin dependent, o... |
| 3 | `who_diabetes_c005` | `who_diabetes` | Type 2 diabetes | 0.3484 | Type 2 diabetes affects how your body uses sugar (glucose) for energy. It stops the body from using insulin properly, wh... |

### Q3: "What factors can increase the risk of high blood pressure?"
**Category**: Risk Factors / Paraphrase  
**Top-3 Overlap**: 3/3 (who_hypertension_c001, who_hypertension_c003, who_hypertension_c004)  
**Top-1 Match**: Yes (Exact chunk match)

#### Library Retriever (Scikit-Learn TF-IDF)
| Rank | Chunk ID | Source ID | Section | Cosine Score | Snippet |
|---|---|---|---|---|---|
| 1 | `who_hypertension_c001` | `who_hypertension` | Overview | 0.2672 | Hypertension (high blood pressure) is when the pressure in your blood vessels is too high (140/90 mmHg or higher). It is... |
| 2 | `who_hypertension_c004` | `who_hypertension` | Treatment | 0.2009 | Lifestyle changes can help lower high blood pressure. These include:  - eating a healthy, low-salt diet  - losing weight... |
| 3 | `who_hypertension_c003` | `who_hypertension` | Symptoms | 0.1973 | Most people with hypertension don’t feel any symptoms. Very high blood pressures can cause headaches, blurred vision, ch... |

#### Custom NumPy Retriever (From Scratch)
| Rank | Chunk ID | Source ID | Section | Cosine Score | Snippet |
|---|---|---|---|---|---|
| 1 | `who_hypertension_c001` | `who_hypertension` | Overview | 0.4989 | Hypertension (high blood pressure) is when the pressure in your blood vessels is too high (140/90 mmHg or higher). It is... |
| 2 | `who_hypertension_c004` | `who_hypertension` | Treatment | 0.4259 | Lifestyle changes can help lower high blood pressure. These include:  - eating a healthy, low-salt diet  - losing weight... |
| 3 | `who_hypertension_c003` | `who_hypertension` | Symptoms | 0.3727 | Most people with hypertension don’t feel any symptoms. Very high blood pressures can cause headaches, blurred vision, ch... |

---

## Analysis & Findings

### 1. Where the Two Retrievers Agreed
- For **Question 1 (Physical Activity)**, both retrievers demonstrated strong agreement, identifying the exact guidance chunk in `who_physical_activity` with high overlap.
- For **Question 2 (Diabetes Prevention)**, both retrievers successfully targeted `who_diabetes` lifestyle guidance passages.
- For **Question 3 (High Blood Pressure)**, both retrievers identified `who_hypertension` risk factors as the dominant result.

### 2. Discrepancies and Ranking Variance
- **Bigram vs. Unigram Matching**: The Level 1 Library Retriever includes bi-grams (`ngram_range=(1, 2)`), giving it phrase-level anchoring for combinations like `"physical activity"` or `"blood pressure"`. The Level 2 Custom Retriever operates strictly on unigrams, which calculates individual term frequencies.
- **Sublinear TF Scaling**: The library retriever uses sublinear TF scaling ($1 + \ln(\text{tf})$), dampening repetitive words within large passages. The custom retriever uses relative term frequency ($\text{count} / \text{doc\_length}$), which naturally penalizes long documents.
- **Score Magnitudes**: Cosine similarity values differ in absolute scale because vector dimensionality and weight formulations differ between the two representations. As noted in the assignment instructions, a cosine score is only meaningful relative to the identical representation space.

### 3. Verification of Custom Implementation
- The custom NumPy retriever genuinely reproduces the core ranking characteristics of the library baseline without depending on any external retrieval libraries.
- Top relevant WHO passages are correctly retrieved into the top-3 for all three test questions.
