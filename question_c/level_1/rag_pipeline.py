"""RAG Pipeline combining document retrieval, context formulation, and LLM generation."""

from typing import Any, Dict, List, Optional
from question_c.level_1.chunker import DocumentChunk, load_corpus
from question_c.level_1.retriever import LibraryTFIDFRetriever
from question_c.level_1.llm import BaseLLMClient, get_llm_client


PROMPT_TEMPLATE = """You are an authoritative, factual public health question-answering assistant for the World Health Organization (WHO).

Your task is to answer the user's question accurately and objectively using ONLY the provided WHO document excerpts.

STRICT INSTRUCTIONS:
1. Rely EXCLUSIVELY on the provided context passages below. Do not fabricate facts, introduce outside knowledge, or make ungrounded inferences.
2. If the context does not contain enough information to answer the question, state: "The available WHO sources do not provide enough information to answer this question."
3. Keep the answer clear, professional, and directly responsive to the question.
4. Mention the relevant WHO guidance and topic when answering.

Context:
{context_block}

Question: {question}

Answer:"""


class RAGPipeline:
    """End-to-end question answering pipeline using retrieval and LLM generation."""

    def __init__(
        self,
        retriever: Optional[LibraryTFIDFRetriever] = None,
        llm_client: Optional[BaseLLMClient] = None,
        top_k: int = 3,
    ):
        if retriever is None:
            chunks = load_corpus()
            self.retriever = LibraryTFIDFRetriever(chunks)
        else:
            self.retriever = retriever

        self.llm_client = llm_client
        self.top_k = top_k

    def _format_context(self, retrieved: List[tuple[DocumentChunk, float]]) -> str:
        blocks = []
        for chunk, score in retrieved:
            block = (
                f"[Source ID: {chunk.source_id} | Document: {chunk.title} | "
                f"Section: {chunk.section} | Relevance Score: {score:.3f}]\n"
                f"{chunk.text}"
            )
            blocks.append(block)
        return "\n\n---\n\n".join(blocks)

    def _extract_sources(
        self, retrieved: List[tuple[DocumentChunk, float]]
    ) -> List[Dict[str, Any]]:
        seen_keys = set()
        sources: List[Dict[str, Any]] = []

        for chunk, score in retrieved:
            key = (chunk.source_id, chunk.section)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            sources.append(
                {
                    "source_id": chunk.source_id,
                    "title": chunk.title,
                    "organization": chunk.organization,
                    "url": chunk.source_url,
                    "section": chunk.section,
                    "relevance_score": round(score, 4),
                }
            )
        return sources

    def answer_question(self, question: str) -> Dict[str, Any]:
        """Execute the end-to-end RAG workflow for a user question."""
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        clean_question = question.strip()

        # Step 1: Retrieve relevant document chunks
        retrieved = self.retriever.retrieve(clean_question, top_k=self.top_k)

        # Handle out-of-domain / zero retrieval case
        if not retrieved:
            return {
                "answer": (
                    "The available WHO sources do not provide enough information to "
                    "answer this question."
                ),
                "sources": [],
            }

        # Step 2: Format context and prompt
        context_block = self._format_context(retrieved)
        sources = self._extract_sources(retrieved)
        prompt = PROMPT_TEMPLATE.format(
            context_block=context_block,
            question=clean_question,
        )

        # Step 3: Generate answer using configured LLM
        client = self.llm_client or get_llm_client()
        answer = client.generate(prompt)

        return {
            "answer": answer,
            "sources": sources,
        }
