"""Document loading and structural chunking for Question C RAG corpus."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class DocumentChunk:
    """Represents a discrete passage within a public health document."""
    chunk_id: str
    source_id: str
    title: str
    organization: str
    source_url: str
    topic: str
    section: str
    text: str

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "source_id": self.source_id,
            "title": self.title,
            "organization": self.organization,
            "source_url": self.source_url,
            "topic": self.topic,
            "section": self.section,
            "text": self.text,
        }


def parse_document_file(filepath: Path | str) -> Tuple[Dict[str, str], str]:
    """Parse a document file with key-value metadata headers and text body."""
    path = Path(filepath)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    metadata: Dict[str, str] = {}
    body_lines: List[str] = []
    in_header = True

    for line in lines:
        if in_header:
            if not line.strip():
                in_header = False
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                metadata[k.strip().lower()] = v.strip()
            else:
                in_header = False
                body_lines.append(line)
        else:
            body_lines.append(line)

    return metadata, "\n".join(body_lines).strip()


def chunk_document(
    filepath: Path | str, target_words: int = 150
) -> List[DocumentChunk]:
    """Segment a document into semantically bounded chunks using markdown section headings.

    Chunks respect section headers (##, ###) and paragraph boundaries,
    preserving metadata attribution for each chunk.
    """
    path = Path(filepath)
    meta, body = parse_document_file(path)

    source_id = meta.get("source_id", path.stem)
    title = meta.get("title", source_id)
    org = meta.get("organization", "World Health Organization")
    url = meta.get("source_url", "")
    topic = meta.get("topic", "")

    lines = body.splitlines()
    chunks: List[DocumentChunk] = []

    current_section = "Overview"
    current_paragraphs: List[str] = []
    chunk_index = 0

    def flush_chunk() -> None:
        nonlocal chunk_index, current_paragraphs
        if not current_paragraphs:
            return
        chunk_text = "\n\n".join(current_paragraphs).strip()
        if chunk_text:
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{source_id}_c{chunk_index:03d}",
                    source_id=source_id,
                    title=title,
                    organization=org,
                    source_url=url,
                    topic=topic,
                    section=current_section,
                    text=chunk_text,
                )
            )
            chunk_index += 1
        current_paragraphs = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## ") or stripped.startswith("### "):
            flush_chunk()
            current_section = stripped.lstrip("#").strip()
        elif stripped:
            current_paragraphs.append(stripped)
        else:
            # Paragraph boundary: check word threshold to prevent over-segmentation
            combined_words = len(" ".join(current_paragraphs).split())
            if combined_words >= target_words:
                flush_chunk()

    flush_chunk()
    return chunks


def load_corpus(documents_dir: Path | str | None = None) -> List[DocumentChunk]:
    """Load and chunk all text files in the documents directory."""
    if documents_dir is None:
        documents_dir = Path(__file__).resolve().parent.parent / "documents"
    else:
        documents_dir = Path(documents_dir)

    all_chunks: List[DocumentChunk] = []
    txt_files = sorted(documents_dir.glob("*.txt"))

    if not txt_files:
        raise FileNotFoundError(
            f"No .txt documents found in directory: {documents_dir}"
        )

    for filepath in txt_files:
        chunks = chunk_document(filepath)
        all_chunks.extend(chunks)

    return all_chunks
