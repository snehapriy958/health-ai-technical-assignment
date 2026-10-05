# Document Collection & Preparation Notes

## 1. Rationale for Selecting the World Health Organization (WHO)
The World Health Organization (WHO) was selected as the sole authoritative source because:
- **Global Consensus & Clinical Authority**: WHO fact sheets represent peer-reviewed, internationally agreed-upon clinical guidance and epidemiological data drafted and reviewed by specialized medical working groups.
- **Objective Ground Truth**: Unlike commercial wellness blogs or crowdsourced portals (e.g., Wikipedia), WHO guidelines provide definitive, verified thresholds (e.g., blood pressure cutoffs of $\ge$ 140/90 mmHg, BMI categories of 25 for overweight and 30 for obesity, physical activity guidelines of 150 minutes/week) that serve as trustworthy reference standards for downstream RAG retrieval and question answering.
- **Consistency of Structure**: WHO fact sheets adhere to a structured template (Key Facts, Overview, Symptoms/Definitions, Causes/Risk Factors, Prevention, Treatment/Management, WHO Response), which facilitates consistent passage segmentation, heading extraction, and chunking.

## 2. Selection Rationale for the Five Topics
The five chosen topics form a cohesive, interconnected foundation for personal health and wellness:
1. **Diabetes (`who_diabetes`)**: A primary chronic noncommunicable disease (NCD) affecting metabolic regulation and cardiovascular health, with clear lifestyle and pharmacological management guidelines.
2. **Hypertension (`who_hypertension`)**: Known as the "silent killer", high blood pressure is the leading preventable cause of cardiovascular disease worldwide, frequently comorbid with diabetes and obesity.
3. **Physical Activity (`who_physical_activity`)**: A foundational behavioral determinant directly modifying risk and outcomes across diabetes, hypertension, and obesity across all age cohorts.
4. **Healthy Diet (`who_healthy_diet`)**: The primary nutritional pillar providing quantitative guidelines on macronutrients, sugars, saturated fats, sodium, potassium, and whole foods.
5. **Obesity and Overweight (`who_obesity`)**: A critical chronic disease and major shared risk factor connecting diet, exercise, hypertension, and type 2 diabetes.

Together, these five documents establish an interconnected knowledge corpus covering lifestyle prevention, clinical markers, definitions, risk factors, and evidence-based interventions.

## 3. Public Health Information vs. Personal Health Records (PHR)
- **Public Health Knowledge Base**: The documents in this corpus consist exclusively of population-level public health guidance, diagnostic criteria, disease epidemiology, prevention advice, and clinical treatment principles published for the global public. They contain no protected health information (PHI) or personally identifiable information (PII).
- **Distinct from Question B**: While Question B dealt with individualized patient health records and synthetic electronic health metrics, Question C uses generalized external clinical reference documents. When combined in later stages, this external corpus can supply factual context to answer user queries safely and ground responses in authoritative health guidelines without hallucinating medical claims.

## 4. Extraction & Text Cleaning Decisions
- **Source Isolation**: WHO fact sheets use the Sitefinity CMS where the core factual text is encapsulated inside `<article class="sf-detail-body-wrapper">`. Content was extracted strictly from this container, deliberately excluding header navigation menus, language pickers, donation widgets, search bars, social media links, cookie consent banners, and footer links.
- **Preservation of Medical Text**: No textual summarization, paraphrasing, or medical rewriting was performed. All clinical assertions, statistical estimates, and diagnostic thresholds were preserved verbatim.
- **Hierarchical Headings Preserved**: HTML header elements (`<h1>`, `<h2>`, `<h3>`) were converted to markdown header equivalents (`#`, `##`, `###`) to ensure that downstream chunking and retrieval (e.g., TF-IDF and semantic chunkers) can maintain section context (e.g., distinguishing "Symptoms" from "Prevention" or "Treatment").
- **List & Bullet Formatting**: Unordered and ordered lists (`<ul>`, `<ol>`, `<li>`) were normalized into bullet lists (`- ...`) to retain itemized guidance (such as symptom lists, lifestyle advice, and medication classes).
- **Whitespace & Typography Normalization**: HTML non-breaking spaces (`&nbsp;` / `\xa0`) were normalized to standard whitespace. Extraneous multiple blank lines were condensed to standard paragraph separations (`\n\n`) to preserve readable paragraph structure.
- **Standard Metadata Header**: Each document was prefixed with standardized key-value metadata (`SOURCE_ID`, `TITLE`, `ORGANIZATION`, `SOURCE_URL`, `TOPIC`) for citation tracking.

## 5. Source Availability & Extraction Challenges
- **Page Availability**: All five WHO fact sheet URLs were live, publicly accessible, and returned HTTP status 200 without requiring API keys or authentication.
- **Dynamic Boilerplate Elements**: WHO fact sheets contain client-side reading time calculators and template date placeholders (`#: FormatedDate #`) in the header markup; extraction targeted the rendered timestamp and the core article wrapper to ensure dynamic script tags were completely avoided.
- **Character Encoding**: The raw HTML responses contained standard HTML entities (e.g., `&ndash;`, `&ge;`, `&nbsp;`); these were converted using UTF-8 encoding so that mathematical and epidemiological symbols (such as $\ge$ and numeric ranges $30\text{--}79$) remain intact without corrupted characters.
