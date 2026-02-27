"""
ChromaDB vector store wrapper.

Each manual is stored as a ChromaDB collection whose name is derived from
the unit number so that per-unit and cross-unit queries are both easy.
"""

import os
import re
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Optional

_CHROMA_DIR = os.getenv("CHROMA_DB_DIR", "./data/chroma")
_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
_OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

# Lazy singleton client
_client: Optional[chromadb.PersistentClient] = None
_ef: Optional[embedding_functions.OpenAIEmbeddingFunction] = None


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=_CHROMA_DIR)
    return _client


def _get_ef() -> embedding_functions.OpenAIEmbeddingFunction:
    global _ef
    if _ef is None:
        _ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=_OPENAI_KEY,
            model_name=_EMBEDDING_MODEL,
        )
    return _ef


def _collection_name(unit_number: str) -> str:
    """Sanitise unit number so it is a valid ChromaDB collection name."""
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", unit_number.strip()).lower()
    return f"unit_{name}"


# ── Public API ────────────────────────────────────────────────────────────────

def index_manual(unit_number: str, filename: str, chunks: List[dict]) -> None:
    """
    Store text chunks for a manual in ChromaDB.

    Each chunk dict must have: {"text", "page", "chunk_index"}
    """
    client = _get_client()
    col_name = _collection_name(unit_number)
    # delete any previous index for this unit before re-indexing
    try:
        client.delete_collection(col_name)
    except Exception:
        pass
    col = client.get_or_create_collection(
        name=col_name,
        embedding_function=_get_ef(),
        metadata={"hnsw:space": "cosine"},
    )
    documents = [c["text"] for c in chunks]
    ids = [f"{col_name}_p{c['page']}_c{c['chunk_index']}" for c in chunks]
    metadatas = [
        {"unit_number": unit_number, "filename": filename, "page": c["page"]}
        for c in chunks
    ]
    # ChromaDB has an add-limit; batch in groups of 500
    batch = 500
    for i in range(0, len(documents), batch):
        col.add(
            documents=documents[i : i + batch],
            ids=ids[i : i + batch],
            metadatas=metadatas[i : i + batch],
        )


def delete_manual_index(unit_number: str) -> None:
    """Remove the ChromaDB collection for a unit."""
    client = _get_client()
    col_name = _collection_name(unit_number)
    try:
        client.delete_collection(col_name)
    except Exception:
        pass


def query_unit(unit_number: str, query: str, n_results: int = 5) -> List[dict]:
    """
    Return the top-n chunks from a specific unit's manual.
    Each result: {"unit_number", "filename", "page", "text", "distance"}
    """
    client = _get_client()
    col_name = _collection_name(unit_number)
    try:
        col = client.get_collection(col_name, embedding_function=_get_ef())
    except Exception:
        return []
    results = col.query(query_texts=[query], n_results=min(n_results, col.count()))
    return _unpack_results(results)


def query_all_manuals(query: str, n_results: int = 5) -> List[dict]:
    """
    Query ALL indexed manuals and return the top-n chunks across all of them.
    Each result: {"unit_number", "filename", "page", "text", "distance"}
    """
    client = _get_client()
    all_results: List[dict] = []
    for col_meta in client.list_collections():
        name = col_meta.name if hasattr(col_meta, "name") else col_meta
        if not name.startswith("unit_"):
            continue
        try:
            col = client.get_collection(name, embedding_function=_get_ef())
            count = col.count()
            if count == 0:
                continue
            r = col.query(query_texts=[query], n_results=min(n_results, count))
            all_results.extend(_unpack_results(r))
        except Exception:
            continue
    # sort by distance (lower = better for cosine)
    all_results.sort(key=lambda x: x["distance"])
    return all_results[:n_results]


def list_indexed_units() -> List[str]:
    """Return unit numbers that have been indexed."""
    client = _get_client()
    units = []
    for col_meta in client.list_collections():
        name = col_meta.name if hasattr(col_meta, "name") else col_meta
        if name.startswith("unit_"):
            units.append(name[len("unit_"):])
    return units


# ── Internal helpers ──────────────────────────────────────────────────────────

def _unpack_results(results: dict) -> List[dict]:
    out = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]
    for doc, meta, dist in zip(docs, metas, dists):
        out.append(
            {
                "unit_number": meta.get("unit_number", ""),
                "filename": meta.get("filename", ""),
                "page": meta.get("page", 0),
                "text": doc,
                "distance": dist,
            }
        )
    return out
