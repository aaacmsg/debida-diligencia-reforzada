from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import hashlib
import os
import aiofiles
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.models import Documento, Expediente, EventoAuditoria
from app.schemas.schemas import DocumentoResponse

router = APIRouter()

ALLOWED_EXTENSIONS = set(settings.allowed_extensions)
MAX_SIZE = settings.max_file_size_mb * 1024 * 1024


def verify_file_extension(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@router.post("/{expediente_id}/upload", response_model=DocumentoResponse)
async def subir_documento(
    expediente_id: int,
    tipo_documento: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    if not verify_file_extension(file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"Formato no permitido. Solo: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    content = await file.read()

    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo muy grande. Max: {settings.max_file_size_mb}MB"
        )

    hash_sha256 = hashlib.sha256(content).hexdigest()

    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = os.path.join(settings.upload_dir, f"{hash_sha256}_{file.filename}")

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    db_documento = Documento(
        expediente_id=expediente_id,
        tipo_documento=tipo_documento,
        nombre_archivo=file.filename,
        ruta_archivo=file_path,
        hash_sha256=hash_sha256,
        tamano_bytes=len(content),
        mime_type=file.content_type,
        uploaded_by=current_user.get("user_id")
    )

    db.add(db_documento)

    evento = EventoAuditoria(
        expediente_id=expediente_id,
        usuario=current_user.get("user_id"),
        accion="SUBIR_DOCUMENTO",
        detalles={
            "nombre": file.filename,
            "tipo": tipo_documento,
            "hash": hash_sha256
        }
    )
    db.add(evento)

    db.commit()
    db.refresh(db_documento)
    return db_documento


@router.get("/{expediente_id}/documentos", response_model=List[DocumentoResponse])
def listar_documentos(
    expediente_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    documentos = db.query(Documento).filter(
        Documento.expediente_id == expediente_id
    ).all()
    return documentos


@router.get("/{expediente_id}/download/{documento_id}")
def descargar_documento(
    expediente_id: int,
    documento_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    expediente = db.query(Expediente).filter(Expediente.id == expediente_id).first()
    if not expediente:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    documento = db.query(Documento).filter(
        Documento.id == documento_id,
        Documento.expediente_id == expediente_id
    ).first()
    if not documento:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if not os.path.exists(documento.ruta_archivo):
        raise HTTPException(status_code=404, detail="Archivo no encontrado en el servidor")

    return FileResponse(
        path=documento.ruta_archivo,
        filename=documento.nombre_archivo,
        media_type=documento.mime_type or "application/octet-stream"
    )
