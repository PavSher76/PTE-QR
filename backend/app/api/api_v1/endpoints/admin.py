"""
Admin endpoints for configuration and management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import structlog

from app.core.database import get_db
from app.models.schemas import StatusMapping, StatusMappingItem
from app.models.document import DocumentStatusEnum

router = APIRouter()
logger = structlog.get_logger()


@router.get("/status-mapping", response_model=StatusMapping)
async def get_status_mapping():
    """
    Get current ENOVIA to Business Status mapping
    """
    # Default mapping based on requirements
    default_mapping = {
        "Released": StatusMappingItem(
            business_status=DocumentStatusEnum.APPROVED_FOR_CONSTRUCTION,
            color="#28a745",  # Green
            action_label="Открыть документ"
        ),
        "AFC": StatusMappingItem(
            business_status=DocumentStatusEnum.APPROVED_FOR_CONSTRUCTION,
            color="#28a745",  # Green
            action_label="Открыть документ"
        ),
        "Accepted": StatusMappingItem(
            business_status=DocumentStatusEnum.ACCEPTED_BY_CUSTOMER,
            color="#007bff",  # Blue
            action_label="Открыть документ"
        ),
        "Approved": StatusMappingItem(
            business_status=DocumentStatusEnum.ACCEPTED_BY_CUSTOMER,
            color="#007bff",  # Blue
            action_label="Открыть документ"
        ),
        "Obsolete": StatusMappingItem(
            business_status=DocumentStatusEnum.CHANGES_INTRODUCED_GET_NEW,
            color="#dc3545",  # Red
            action_label="Скачать актуальную"
        ),
        "Superseded": StatusMappingItem(
            business_status=DocumentStatusEnum.CHANGES_INTRODUCED_GET_NEW,
            color="#dc3545",  # Red
            action_label="Скачать актуальную"
        ),
        "In Work": StatusMappingItem(
            business_status=DocumentStatusEnum.IN_WORK,
            color="#6c757d",  # Gray
            action_label="Обратиться к ответственному"
        ),
        "Frozen": StatusMappingItem(
            business_status=DocumentStatusEnum.IN_WORK,
            color="#6c757d",  # Gray
            action_label="Обратиться к ответственному"
        )
    }
    
    return StatusMapping(__root__=default_mapping)


@router.put("/status-mapping", status_code=204)
async def update_status_mapping(
    mapping: StatusMapping,
    db: Session = Depends(get_db)
):
    """
    Update ENOVIA to Business Status mapping (admin only)
    """
    # In a real implementation, this would save to database
    # For now, just log the update
    logger.info("Status mapping updated", mapping=mapping.dict())
    
    # TODO: Implement actual mapping storage and retrieval
    # This could be stored in a configuration table or Redis
    
    return {"message": "Status mapping updated successfully"}


@router.get("/audit")
async def get_audit_logs(
    from_date: str = None,
    to_date: str = None,
    doc_uid: str = None,
    action: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get audit logs with filtering
    """
    # TODO: Implement audit log retrieval
    # This would query the audit_logs table with filters
    
    return {
        "message": "Audit logs endpoint - implement audit log retrieval",
        "filters": {
            "from_date": from_date,
            "to_date": to_date,
            "doc_uid": doc_uid,
            "action": action,
            "limit": limit,
            "offset": offset
        }
    }
