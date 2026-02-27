"""
PDF text extraction helper.
Splits extracted text into overlapping chunks for vector indexing.
"""

import pdfplumber
from typing import List, Tuple


CHUNK_SIZE = 800      # characters per chunk
CHUNK_OVERLAP = 150   # overlap between adjacent chunks


def extract_pages(pdf_path: str) -> List[Tuple[int, str]]:
    """Return a list of (page_number, page_text) tuples (1-indexed)."""
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append((i, text.strip()))
    return pages


def chunk_text(text: str, page: int) -> List[dict]:
    """
    Split *text* into overlapping chunks and return a list of dicts with:
        {"text": ..., "page": ..., "chunk_index": ...}
    """
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end]
        if chunk.strip():
            chunks.append({"text": chunk, "page": page, "chunk_index": idx})
        start += CHUNK_SIZE - CHUNK_OVERLAP
        idx += 1
    return chunks


def extract_chunks(pdf_path: str) -> Tuple[List[dict], int]:
    """
    Extract all text chunks from a PDF.

    Returns:
        (chunks, page_count)
        where each chunk is {"text", "page", "chunk_index"}
    """
    pages = extract_pages(pdf_path)
    all_chunks: List[dict] = []
    for page_num, page_text in pages:
        if page_text:
            all_chunks.extend(chunk_text(page_text, page_num))
    return all_chunks, len(pages)
