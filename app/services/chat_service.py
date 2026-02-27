"""
RAG chat service.

Strategy
--------
1. Detect unit numbers in the user's message (e.g. "unit 102", "#102").
2. If a unit is mentioned, retrieve chunks from that unit's manual first,
   then do a cross-manual search for any keywords that suggest parts/cross-
   reference needs (hoses, parts, specs, etc.).
3. Build a context block and call the OpenAI chat API.
"""

import os
import re
from typing import List, Optional, Tuple

from openai import OpenAI

from app.services import vector_service
from app.models.schemas import ChatMessage, SourceChunk

_CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
_client: Optional[OpenAI] = None


def _get_openai() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
    return _client


# Keywords that hint at a cross-manual parts/reference query
_CROSS_REF_KEYWORDS = re.compile(
    r"\b(part|parts|hose|hoses|fitting|fittings|filter|filters|"
    r"spec|specs|specification|compatible|replacement|manual|manuals|"
    r"diagram|schematics|oil|fluid|belt|belts|seal|seals)\b",
    re.IGNORECASE,
)

# Patterns that look like a unit number
_UNIT_PATTERNS = [
    re.compile(r"\bunit\s*#?\s*(\w+)\b", re.IGNORECASE),
    re.compile(r"#\s*(\d+)\b"),
    re.compile(r"\bunit\s+(\d+)\b", re.IGNORECASE),
]


def _detect_units(text: str) -> List[str]:
    """Return unit numbers mentioned in *text* (deduplicated, order-preserved)."""
    seen = set()
    units = []
    for pat in _UNIT_PATTERNS:
        for m in pat.finditer(text):
            u = m.group(1).strip()
            if u not in seen:
                seen.add(u)
                units.append(u)
    return units


def _retrieve_context(message: str) -> Tuple[List[dict], bool]:
    """
    Return (chunks, cross_ref_used).

    * If specific unit numbers are mentioned, query those units first.
    * If cross-reference keywords are present (or no unit-specific results),
      also search all manuals.
    """
    units = _detect_units(message)
    chunks: List[dict] = []
    used_ids: set = set()

    def _add(results):
        for r in results:
            key = (r["unit_number"], r["page"], r["text"][:50])
            if key not in used_ids:
                used_ids.add(key)
                chunks.append(r)

    if units:
        for unit in units:
            _add(vector_service.query_unit(unit, message, n_results=5))

    cross_ref = bool(_CROSS_REF_KEYWORDS.search(message))
    if cross_ref or not chunks:
        _add(vector_service.query_all_manuals(message, n_results=5))

    # limit total context to 10 chunks
    chunks = chunks[:10]
    return chunks, cross_ref


_SYSTEM_PROMPT = """You are an expert equipment technician assistant.
You have access to PDF equipment manuals indexed by unit number.

When answering:
- Always cite the unit number and page number you are drawing information from.
- If the question mentions a specific unit, prioritise that unit's manual.
- If parts or cross-reference information is needed (e.g. hoses, filters, fittings),
  look across ALL manuals and note which unit each part belongs to.
- Be concise but complete.  If you don't know, say so.

Context from manuals:
{context}
"""


def chat(message: str, history: List[ChatMessage]) -> Tuple[str, List[SourceChunk]]:
    """
    Run a RAG chat turn.

    Returns (answer_text, source_chunks).
    """
    chunks, _ = _retrieve_context(message)

    # Build context string
    context_lines = []
    for c in chunks:
        context_lines.append(
            f"[Unit {c['unit_number']} | {c['filename']} | Page {c['page']}]\n{c['text']}"
        )
    context_str = "\n\n---\n\n".join(context_lines) if context_lines else "No relevant manual content found."

    system_msg = {"role": "system", "content": _SYSTEM_PROMPT.format(context=context_str)}

    messages = [system_msg]
    for h in history[-10:]:   # keep last 10 turns for context
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": message})

    oai = _get_openai()
    response = oai.chat.completions.create(
        model=_CHAT_MODEL,
        messages=messages,
        temperature=0.2,
    )
    answer = response.choices[0].message.content or ""

    sources = [
        SourceChunk(
            unit_number=c["unit_number"],
            filename=c["filename"],
            page=c["page"],
            text=c["text"][:300],
        )
        for c in chunks
    ]
    return answer, sources
