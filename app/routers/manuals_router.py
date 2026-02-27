"""
Manuals router — upload, list, delete PDF manuals.
"""

import json
import os
import shutil
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.auth import get_current_user, require_admin
from app.models.schemas import ManualList, ManualMeta
from app.services import pdf_service, vector_service

router = APIRouter(prefix="/api/manuals", tags=["manuals"])

_PDF_DIR = os.getenv("PDF_STORAGE_DIR", "./data/pdfs")
_META_FILE = os.path.join(_PDF_DIR, "_metadata.json")


def _load_meta() -> dict:
    os.makedirs(_PDF_DIR, exist_ok=True)
    if os.path.exists(_META_FILE):
        with open(_META_FILE) as f:
            return json.load(f)
    return {}


def _save_meta(meta: dict) -> None:
    os.makedirs(_PDF_DIR, exist_ok=True)
    with open(_META_FILE, "w") as f:
        json.dump(meta, f, indent=2)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("", response_model=ManualList)
async def list_manuals(_: dict = Depends(get_current_user)):
    meta = _load_meta()
    manuals = [ManualMeta(**v) for v in meta.values()]
    manuals.sort(key=lambda m: m.unit_number)
    return ManualList(manuals=manuals)


@router.post("", response_model=ManualMeta, status_code=201)
async def upload_manual(
    unit_number: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Sanitise unit number for use as a filename key
    safe_unit = unit_number.strip().replace("/", "_").replace("\\", "_")
    if not safe_unit:
        raise HTTPException(status_code=400, detail="unit_number must not be empty")

    # Check if unit already exists
    meta = _load_meta()
    if safe_unit in meta:
        raise HTTPException(
            status_code=409,
            detail=f"Unit {safe_unit} already exists. Delete it first to replace.",
        )

    # Save the PDF
    os.makedirs(_PDF_DIR, exist_ok=True)
    dest_path = os.path.join(_PDF_DIR, f"{safe_unit}.pdf")
    with open(dest_path, "wb") as out:
        shutil.copyfileobj(file.file, out)

    # Extract text and index
    try:
        chunks, page_count = pdf_service.extract_chunks(dest_path)
        vector_service.index_manual(safe_unit, file.filename, chunks)
    except Exception as exc:
        os.remove(dest_path)
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {exc}")

    record = ManualMeta(
        unit_number=safe_unit,
        filename=file.filename,
        description=description or "",
        uploaded_at=datetime.now(timezone.utc).isoformat(),
        uploaded_by=current_user["username"],
        page_count=page_count,
    )
    meta[safe_unit] = record.model_dump()
    _save_meta(meta)
    return record


@router.get("/{unit_number}", response_model=ManualMeta)
async def get_manual(unit_number: str, _: dict = Depends(get_current_user)):
    meta = _load_meta()
    if unit_number not in meta:
        raise HTTPException(status_code=404, detail="Manual not found")
    return ManualMeta(**meta[unit_number])


@router.get("/{unit_number}/download")
async def download_manual(unit_number: str, _: dict = Depends(get_current_user)):
    meta = _load_meta()
    if unit_number not in meta:
        raise HTTPException(status_code=404, detail="Manual not found")
    pdf_path = os.path.join(_PDF_DIR, f"{unit_number}.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")
    return FileResponse(pdf_path, media_type="application/pdf", filename=meta[unit_number]["filename"])


@router.delete("/{unit_number}", status_code=204)
async def delete_manual(unit_number: str, _: dict = Depends(require_admin)):
    meta = _load_meta()
    if unit_number not in meta:
        raise HTTPException(status_code=404, detail="Manual not found")

    # Remove PDF file
    pdf_path = os.path.join(_PDF_DIR, f"{unit_number}.pdf")
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    # Remove vector index
    vector_service.delete_manual_index(unit_number)

    del meta[unit_number]
    _save_meta(meta)
