import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.api.deps import get_db, get_current_user, require_admin
from app.core.config import settings
from app.models.document import ChurchDocument
from app.models.pokja import Pokja
from app.models.item import Item
from app.models.user import User
from app.schemas.document import DocumentResponse

router = APIRouter(prefix="/documents", tags=["Arsip Dokumen Gereja"])

ALLOWED_DOC_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".docx"}


@router.get("", response_model=List[DocumentResponse])
def get_documents(
    pokja_id: Optional[int] = Query(None),
    related_item_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mengambil daftar seluruh berkas arsip gereja (nota pembelian, kartu garansi, SK, sertifikat).
    """
    query = db.query(ChurchDocument).order_by(ChurchDocument.created_at.desc())

    if pokja_id:
        query = query.filter(ChurchDocument.pokja_id == pokja_id)
    if related_item_id:
        query = query.filter(ChurchDocument.related_item_id == related_item_id)
    if search:
        s = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(ChurchDocument.title).like(s),
                func.lower(ChurchDocument.doc_number).like(s),
                func.lower(ChurchDocument.physical_storage_loc).like(s),
            )
        )

    docs = query.all()
    results = []
    for d in docs:
        results.append(
            DocumentResponse(
                id=d.id,
                title=d.title,
                doc_number=d.doc_number,
                pokja_id=d.pokja_id,
                related_item_id=d.related_item_id,
                file_path=d.file_path,
                file_type=d.file_type,
                file_size_bytes=d.file_size_bytes,
                physical_storage_loc=d.physical_storage_loc,
                pokja_code=d.pokja.code if d.pokja else None,
                item_name=d.related_item.name if d.related_item else None,
                uploaded_by_name=d.uploader.name if d.uploader else None,
                created_at=d.created_at
            )
        )
    return results


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    title: str = Form(..., min_length=3, max_length=200),
    doc_number: Optional[str] = Form(None, max_length=100),
    pokja_id: Optional[int] = Form(None),
    related_item_id: Optional[int] = Form(None),
    physical_storage_loc: Optional[str] = Form(None, max_length=150),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Mengunggah berkas arsip dokumen gereja baru (PDF nota/garansi/sertifikat/SK).
    """
    original_filename = file.filename or "dokumen"
    _, ext = os.path.splitext(original_filename.lower())

    if ext not in ALLOWED_DOC_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipe file {ext} tidak diizinkan. Gunakan format: {', '.join(ALLOWED_DOC_EXTENSIONS)}"
        )

    # Tentukan subfolder per POKJA
    subfolder = "documents"
    if pokja_id:
        pokja = db.query(Pokja).filter(Pokja.id == pokja_id).first()
        if pokja:
            subfolder = f"documents/{pokja.code.lower()}"

    target_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
    os.makedirs(target_dir, exist_ok=True)

    safe_filename = f"{uuid.uuid4().hex[:12]}_{original_filename}"
    full_path = os.path.join(target_dir, safe_filename)

    file_bytes = file.file.read()
    file_size = len(file_bytes)

    # Validasi batas ukuran file (max 10MB per SKILL.md)
    if file_size > (settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024):
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Ukuran file melebihi batas maksimal {settings.MAX_UPLOAD_SIZE_MB} MB."
        )

    with open(full_path, "wb") as f:
        f.write(file_bytes)

    relative_path = os.path.join(subfolder, safe_filename).replace("\\", "/")

    new_doc = ChurchDocument(
        title=title.strip(),
        doc_number=doc_number.strip() if doc_number else None,
        pokja_id=pokja_id,
        related_item_id=related_item_id,
        file_path=relative_path,
        file_type=ext.lstrip("."),
        file_size_bytes=file_size,
        physical_storage_loc=physical_storage_loc.strip() if physical_storage_loc else None,
        uploaded_by=admin.id
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    return DocumentResponse(
        id=new_doc.id,
        title=new_doc.title,
        doc_number=new_doc.doc_number,
        pokja_id=new_doc.pokja_id,
        related_item_id=new_doc.related_item_id,
        file_path=new_doc.file_path,
        file_type=new_doc.file_type,
        file_size_bytes=new_doc.file_size_bytes,
        physical_storage_loc=new_doc.physical_storage_loc,
        pokja_code=new_doc.pokja.code if new_doc.pokja else None,
        item_name=new_doc.related_item.name if new_doc.related_item else None,
        uploaded_by_name=admin.name,
        created_at=new_doc.created_at
    )

