"""FastAPI web service for Question C Level 1 RAG Question Answering."""

from pathlib import Path
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from question_c.level_1.rag_pipeline import RAGPipeline
from question_c.level_1.llm import MissingAPIKeyError, LLMAPIError

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="WHO Public Health Assistant (Level 1 RAG)",
    description="Question-answering assistant grounded exclusively in official WHO fact sheets.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global lazy pipeline instance
_pipeline: RAGPipeline | None = None


def get_pipeline() -> RAGPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline


class QuestionRequest(BaseModel):
    question: str = Field(..., description="Public health question to be answered.")


class SourceItem(BaseModel):
    source_id: str
    title: str
    organization: str
    url: str
    section: str
    relevance_score: float


class AnswerResponse(BaseModel):
    answer: str
    sources: List[SourceItem]


@app.get("/", response_class=FileResponse)
def serve_index():
    """Serve the Level 1 web interface."""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frontend index.html not found.",
        )
    return FileResponse(index_path)


@app.get("/health")
def health_check():
    """Health check endpoint providing status and corpus chunk count."""
    pipeline = get_pipeline()
    return {
        "status": "healthy",
        "corpus_chunks": len(pipeline.retriever.chunks),
        "topics": list(
            sorted({c.topic for c in pipeline.retriever.chunks})
        ),
    }


@app.post("/ask", response_model=AnswerResponse)
def ask_question(payload: QuestionRequest):
    """Retrieve relevant WHO document chunks and generate an evidence-grounded answer."""
    question = payload.question.strip()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    pipeline = get_pipeline()

    try:
        result = pipeline.answer_question(question)
        return result
    except MissingAPIKeyError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
    except LLMAPIError as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(err),
        ) from err
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error processing question: {err}",
        ) from err


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("question_c.level_1.app:app", host="127.0.0.1", port=8000, reload=True)
