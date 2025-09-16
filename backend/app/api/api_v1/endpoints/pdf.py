"""
PDF stamping endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import structlog

from app.core.database import get_db
from app.services.pdf_service import pdf_service
from app.api.api_v1.endpoints.auth import get_current_user_dependency
from app.models.user import User

router = APIRouter()
logger = structlog.get_logger()


@router.post("/stamp")
async def stamp_pdf_with_qr_codes(
    pdf_file: UploadFile = File(..., description="PDF file to stamp"),
    doc_uid: str = Query(..., description="Document UID"),
    revision: str = Query(..., description="Document revision"),
    pages: str = Query(..., description="Comma-separated list of page numbers"),
    position: str = Query("bottom-right", description="QR position (bottom-right, top-right, top-center)"),
    margin_mm: int = Query(5, ge=0, le=50, description="Margin in millimeters"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """
    Stamp existing PDF with QR codes on specified pages
    
    Args:
        pdf_file: PDF file to stamp
        doc_uid: Document UID
        revision: Document revision
        pages: Comma-separated list of page numbers (1-indexed)
        position: QR position on page
        margin_mm: Margin from edge in millimeters
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Stamped PDF file
    """
    try:
        # Validate file type
        if not pdf_file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a PDF"
            )
        
        # Parse page numbers
        try:
            page_numbers = [int(p.strip()) for p in pages.split(',') if p.strip()]
            if not page_numbers:
                raise ValueError("No valid page numbers provided")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid page numbers: {str(e)}"
            )
        
        # Validate position
        valid_positions = ["bottom-right", "top-right", "top-center"]
        if position not in valid_positions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid position. Must be one of: {', '.join(valid_positions)}"
            )
        
        # Read PDF file
        pdf_content = await pdf_file.read()
        
        # Stamp PDF with QR codes
        stamped_pdf = await pdf_service.stamp_pdf_with_qr_codes(
            pdf_file=pdf_content,
            doc_uid=doc_uid,
            revision=revision,
            pages=page_numbers,
            position=position,
            margin_mm=margin_mm,
            user=current_user
        )
        
        logger.info(
            "PDF stamped successfully",
            doc_uid=doc_uid,
            revision=revision,
            pages=page_numbers,
            position=position,
            user_id=current_user.id
        )
        
        # Return stamped PDF
        from fastapi.responses import Response
        return Response(
            content=stamped_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=stamped_{doc_uid}_{revision}.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to stamp PDF",
            doc_uid=doc_uid,
            revision=revision,
            pages=pages,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stamp PDF: {str(e)}"
        )


@router.post("/generate")
async def generate_pdf_with_qr_codes(
    doc_uid: str = Query(..., description="Document UID"),
    revision: str = Query(..., description="Document revision"),
    pages: str = Query(..., description="Comma-separated list of page numbers"),
    position: str = Query("bottom-right", description="QR position (bottom-right, top-right, top-center)"),
    margin_mm: int = Query(5, ge=0, le=50, description="Margin in millimeters"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dependency)
):
    """
    Generate a new PDF with embedded QR codes
    
    Args:
        doc_uid: Document UID
        revision: Document revision
        pages: Comma-separated list of page numbers
        position: QR position on page
        margin_mm: Margin from edge in millimeters
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Generated PDF with QR codes
    """
    try:
        # Parse page numbers
        try:
            page_numbers = [int(p.strip()) for p in pages.split(',') if p.strip()]
            if not page_numbers:
                raise ValueError("No valid page numbers provided")
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid page numbers: {str(e)}"
            )
        
        # Validate position
        valid_positions = ["bottom-right", "top-right", "top-center"]
        if position not in valid_positions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid position. Must be one of: {', '.join(valid_positions)}"
            )
        
        # Generate PDF with QR codes
        generated_pdf = await pdf_service.generate_pdf_with_qr_codes(
            doc_uid=doc_uid,
            revision=revision,
            pages=page_numbers,
            position=position,
            margin_mm=margin_mm,
            user=current_user
        )
        
        logger.info(
            "PDF with QR codes generated successfully",
            doc_uid=doc_uid,
            revision=revision,
            pages=page_numbers,
            position=position,
            user_id=current_user.id
        )
        
        # Return generated PDF
        from fastapi.responses import Response
        return Response(
            content=generated_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={doc_uid}_{revision}_with_qr.pdf"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to generate PDF with QR codes",
            doc_uid=doc_uid,
            revision=revision,
            pages=pages,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )


@router.get("/positions")
async def get_stamp_positions(
    page_width: float = Query(..., description="Page width in points"),
    page_height: float = Query(..., description="Page height in points"),
    position: str = Query("bottom-right", description="QR position"),
    margin_mm: int = Query(5, ge=0, le=50, description="Margin in millimeters")
):
    """
    Get QR stamp positions for given page dimensions
    
    Args:
        page_width: Page width in points
        page_height: Page height in points
        position: QR position on page
        margin_mm: Margin in millimeters
        
    Returns:
        List of stamp positions
    """
    try:
        # Validate position
        valid_positions = ["bottom-right", "top-right", "top-center"]
        if position not in valid_positions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid position. Must be one of: {', '.join(valid_positions)}"
            )
        
        # Get stamp positions
        positions = await pdf_service.get_stamp_positions(
            page_width=page_width,
            page_height=page_height,
            position=position,
            margin_mm=margin_mm
        )
        
        return {
            "positions": positions,
            "page_width": page_width,
            "page_height": page_height,
            "position": position,
            "margin_mm": margin_mm
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get stamp positions",
            page_width=page_width,
            page_height=page_height,
            position=position,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stamp positions: {str(e)}"
        )
