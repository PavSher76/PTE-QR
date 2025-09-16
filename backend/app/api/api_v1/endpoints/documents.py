"""
Document status endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import structlog

from app.core.database import get_db, get_redis
from app.models.schemas import StatusResponse, ErrorResponse
from app.models.document import Document, DocumentRevision, DocumentStatus, DocumentStatusEnum, EnoviaStateEnum
from app.services.enovia_service import enovia_service
from app.utils.hmac_signer import HMACSigner

router = APIRouter()
logger = structlog.get_logger()


@router.get(
    "/{doc_uid}/revisions/{rev}/status",
    response_model=StatusResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Document or revision not found"},
        410: {"model": StatusResponse, "description": "Revision is outdated"},
        400: {"model": ErrorResponse, "description": "Invalid parameters"}
    }
)
async def get_document_status(
    doc_uid: str,
    rev: str,
    page: int = Query(..., ge=1, description="Page number"),
    db: Session = Depends(get_db),
    redis = Depends(get_redis)
):
    """
    Check status of specific document revision and page
    """
    try:
        # Check cache first
        cache_key = f"status:{doc_uid}:{rev}:{page}"
        cached_status = redis.get(cache_key)
        
        if cached_status:
            logger.info("Status cache hit", doc_uid=doc_uid, revision=rev, page=page)
            # Parse cached data and return
            import json
            cached_data = json.loads(cached_status)
            return StatusResponse(**cached_data)
        
        # Get from database or ENOVIA
        enovia_client = ENOVIAClient()
        
        # Try to get from database first
        document = db.query(Document).filter(Document.doc_uid == doc_uid).first()
        if not document:
            # Try to get from ENOVIA
            doc_meta = await enovia_client.get_document_meta(doc_uid)
            if not doc_meta:
                raise HTTPException(status_code=404, detail="Document not found")
            
            # Create document in database
            document = Document(
                doc_uid=doc_uid,
                title=doc_meta.get("title", ""),
                number=doc_meta.get("number"),
                enovia_id=doc_meta.get("id")
            )
            db.add(document)
            db.commit()
            db.refresh(document)
        
        # Get revision
        revision = db.query(DocumentRevision).filter(
            DocumentRevision.document_id == document.id,
            DocumentRevision.revision == rev
        ).first()
        
        if not revision:
            # Try to get from ENOVIA
            rev_meta = await enovia_client.get_revision_meta(doc_uid, rev)
            if not rev_meta:
                raise HTTPException(status_code=404, detail="Revision not found")
            
            # Create revision in database
            enovia_state = EnoviaStateEnum(rev_meta.get("maturityState", "In Work"))
            business_status = enovia_client.map_enovia_state_to_business_status(
                rev_meta.get("maturityState", "In Work")
            )
            
            revision = DocumentRevision(
                document_id=document.id,
                revision=rev,
                enovia_state=enovia_state,
                business_status=business_status,
                released_at=rev_meta.get("releasedDate"),
                superseded_by=rev_meta.get("supersededBy"),
                last_modified=rev_meta.get("lastModified"),
                enovia_revision_id=rev_meta.get("id"),
                maturity_state=rev_meta.get("maturityState")
            )
            db.add(revision)
            db.commit()
            db.refresh(revision)
        
        # Check if revision is actual
        is_actual = enovia_client.is_revision_actual({
            "maturityState": revision.enovia_state.value,
            "supersededBy": revision.superseded_by
        })
        
        # Prepare response
        response_data = {
            "doc_uid": doc_uid,
            "revision": rev,
            "page": page,
            "business_status": revision.business_status,
            "enovia_state": revision.enovia_state,
            "is_actual": is_actual,
            "released_at": revision.released_at,
            "superseded_by": revision.superseded_by,
            "links": {
                "openDocument": f"https://enovia.pti.ru/3dspace/document/{doc_uid}?rev={rev}",
                "openLatest": None
            }
        }
        
        # If not actual, get latest revision
        if not is_actual:
            latest_meta = await enovia_client.get_latest_released(doc_uid)
            if latest_meta:
                latest_rev = latest_meta.get("revision", "unknown")
                response_data["links"]["openLatest"] = f"https://enovia.pti.ru/3dspace/document/{doc_uid}?rev={latest_rev}"
        
        # Cache the result
        import json
        redis.setex(cache_key, 900, json.dumps(response_data, default=str))  # 15 minutes TTL
        
        # Log status check
        status_check = DocumentStatus(
            revision_id=revision.id,
            page=page,
            is_actual=is_actual,
            business_status=revision.business_status,
            enovia_state=revision.enovia_state
        )
        db.add(status_check)
        db.commit()
        
        logger.info(
            "Status check completed",
            doc_uid=doc_uid,
            revision=rev,
            page=page,
            is_actual=is_actual,
            business_status=revision.business_status.value
        )
        
        # Return appropriate status code
        if not is_actual:
            return StatusResponse(**response_data)  # 410 will be handled by response model
        
        return StatusResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get document status",
            doc_uid=doc_uid,
            revision=rev,
            page=page,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/qr/verify")
async def verify_qr_signature(
    doc_uid: str = Query(..., description="Document UID"),
    rev: str = Query(..., description="Revision"),
    page: int = Query(..., description="Page number"),
    ts: int = Query(..., description="Timestamp"),
    sig: str = Query(..., description="Signature")
):
    """
    Verify QR code signature (for debugging)
    """
    try:
        hmac_signer = HMACSigner()
        is_valid = hmac_signer.verify_signature(doc_uid, rev, page, ts, sig)
        
        if is_valid:
            return {"valid": True, "message": "Signature is valid"}
        else:
            return {"valid": False, "message": "Invalid signature"}
            
    except Exception as e:
        logger.error("QR signature verification failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid parameters")
