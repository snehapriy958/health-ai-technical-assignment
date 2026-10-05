# Question C — Trusted Health QA Assistant

## Objective

Build a document-grounded health question-answering assistant that
answers using a small collection of public health documents and shows
the source used for each answer.

## Level 1

Requirements:

1. Collect 5–10 public health documents.
2. Build a RAG + LLM question-answering pipeline.
3. Display the source for every answer.

## Level 2

Implement retrieval yourself:

1. Chunk the documents.
2. Generate TF-IDF representations.
3. Calculate cosine similarity using NumPy.
4. Retrieve the most relevant chunks.
5. Compare the custom top-3 retrieval with a library retriever
   using three questions.

A vector database or retriever library must not replace the required
manual retrieval implementation.

## Level 3

Requirements:

1. Create 10 evaluation questions.
2. Include at least 3 questions that cannot be answered from the
   collected documents.
3. Write predictions before running the evaluation.
4. Report the actual results.
5. Analyze one incorrect answer.
6. Determine whether the failure came from retrieval or the LLM.

## Personal Seed

`S = 48`

## Run Instructions

To be added after implementation.

## Results

To be added after experiments.

## Sources

All documents and external resources will be credited here.