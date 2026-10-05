"""LLM client abstractions and error handling for Question C Level 1."""

import os
import re
from typing import Optional
import httpx


class LLMError(Exception):
    """Base exception for LLM errors."""
    pass


class MissingAPIKeyError(LLMError):
    """Raised when no LLM API key is configured."""
    pass


class LLMAPIError(LLMError):
    """Raised when the LLM provider call fails."""
    pass


class BaseLLMClient:
    """Base interface for LLM question answering."""

    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class GeminiLLMClient(BaseLLMClient):
    """Client for Google Gemini API via lightweight HTTP requests."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model = model
        self.api_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )

    def generate(self, prompt: str) -> str:
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 1024,
            },
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(self.api_url, json=payload)
                if resp.status_code != 200:
                    raise LLMAPIError(
                        f"Gemini API returned HTTP {resp.status_code}: {resp.text}"
                    )
                data = resp.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    raise LLMAPIError("No response candidate returned by Gemini API.")
                content = (
                    candidates[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
                return content.strip()
        except httpx.RequestError as exc:
            raise LLMAPIError(f"Network error contacting Gemini API: {exc}") from exc


class OpenAILLMClient(BaseLLMClient):
    """Client for OpenAI API via lightweight HTTP requests."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1024,
        }
        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(self.api_url, headers=headers, json=payload)
                if resp.status_code != 200:
                    raise LLMAPIError(
                        f"OpenAI API returned HTTP {resp.status_code}: {resp.text}"
                    )
                data = resp.json()
                choices = data.get("choices", [])
                if not choices:
                    raise LLMAPIError("No completion choice returned by OpenAI API.")
                return choices[0]["message"]["content"].strip()
        except httpx.RequestError as exc:
            raise LLMAPIError(f"Network error contacting OpenAI API: {exc}") from exc


class MockLLMClient(BaseLLMClient):
    """Deterministic local mock LLM for offline verification and automated tests.

    Extracts direct factual statements from the provided context without making external API calls.
    """

    def generate(self, prompt: str) -> str:
        # Check if context was declared empty
        if "NO RELEVANT CONTEXT AVAILABLE" in prompt:
            return "The available WHO sources do not provide enough information to answer this question."

        # Extract question from prompt
        q_match = re.search(r"Question:\s*(.*?)\n\nAnswer:", prompt, re.DOTALL)
        question = q_match.group(1).strip() if q_match else ""

        # Extract context block
        ctx_match = re.search(r"Context:\n(.*?)\n\nQuestion:", prompt, re.DOTALL)
        context = ctx_match.group(1).strip() if ctx_match else ""

        if not context:
            return "The available WHO sources do not provide enough information to answer this question."

        # Synthesize concise factual response based on matching lines in context
        q_words = {
            w.lower()
            for w in re.findall(r"\w+", question)
            if len(w) > 3
            and w.lower()
            not in {"what", "which", "some", "ways", "much", "does", "from", "with", "have"}
        }

        matched_sentences = []
        for line in context.splitlines():
            clean = line.strip()
            if not clean or clean.startswith("[") or clean.startswith("##") or clean.startswith("---"):
                continue
            line_words = set(re.findall(r"\w+", clean.lower()))
            if len(q_words.intersection(line_words)) >= 1:
                matched_sentences.append(clean.lstrip("- ").strip())

        if matched_sentences:
            unique_sentences = list(dict.fromkeys(matched_sentences))[:4]
            return "According to the World Health Organization:\n\n" + "\n\n".join(
                f"- {s}" for s in unique_sentences
            )

        return (
            "According to the provided WHO guidelines:\n\n"
            + context[:400]
            + "..."
        )


def get_llm_client(force_mock: bool = False) -> BaseLLMClient:
    """Factory to instantiate the appropriate LLM client based on environment variables."""
    mock_env = os.environ.get("MOCK_LLM", "").lower() in ("1", "true", "yes")

    if force_mock or mock_env:
        return MockLLMClient()

    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        model = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        return GeminiLLMClient(api_key=gemini_key, model=model)

    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        return OpenAILLMClient(api_key=openai_key, model=model)

    raise MissingAPIKeyError(
        "No LLM API key configured. Please set GEMINI_API_KEY or OPENAI_API_KEY "
        "as an environment variable, or enable MOCK_LLM=1 for local offline testing."
    )
