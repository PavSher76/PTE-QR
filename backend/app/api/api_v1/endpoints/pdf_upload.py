"""
API endpoints for PDF upload and QR code generation
"""

import os
import tempfile
import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.pdf_service import PDFService
from app.services.qr_service import QRService
from app.services.document_service import DocumentService
from app.services.settings_service import SettingsService

router = APIRouter()

@router.post("/upload", summary="Upload PDF and generate QR codes", description="Upload PDF document and generate QR codes for each page")
async def upload_pdf_with_qr_codes(
    file: UploadFile = File(..., description="PDF file to upload"),
    enovia_id: str = Form(..., description="ENOVIA document ID"),
    title: str = Form(..., description="Document title"),
    revision: str = Form(..., description="Document revision"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload PDF document and generate QR codes for each page
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superusers can upload PDF documents"
        )

    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    # Validate required fields
    if not enovia_id.strip() or not title.strip() or not revision.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All fields (enovia_id, title, revision) are required"
        )

    try:
        # Initialize services
        pdf_service = PDFService()
        qr_service = QRService()
        document_service = DocumentService(db)
        settings_service = SettingsService(db)
        
        # Get URL prefix from settings
        settings = await settings_service.get_settings()
        url_prefix = settings.get("urlPrefix", "https://pte-qr.example.com")
        document_status_url = settings.get("documentStatusUrl", "r")
        base_url_prefix = f"{url_prefix}/{document_status_url}"

        # Create temporary file for PDF processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            # Save uploaded file to temporary location
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Read PDF content
            with open(temp_file_path, 'rb') as f:
                pdf_content = f.read()

            # Process PDF (add QR codes)
            processed_pdf_content, qr_codes_data = await pdf_service.add_qr_codes_to_pdf(
                pdf_content=pdf_content,
                enovia_id=enovia_id.strip(),
                revision=revision.strip(),
                base_url_prefix=base_url_prefix,
            )

            # Save document and QR codes to database
            document = await document_service.create_document_with_qr_codes(
                db=db,
                enovia_id=enovia_id.strip(),
                title=title.strip(),
                revision=revision.strip(),
                creator_id=current_user.id,
                qr_codes_data=qr_codes_data,
            )

            # Save processed PDF to file system
            output_filename = f"{enovia_id}_{revision}_{uuid.uuid4().hex[:8]}.pdf"
            output_dir = "/app/tmp/processed_pdfs"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'wb') as f:
                f.write(processed_pdf_content)

            return {
                "message": "PDF processed successfully",
                "document_id": str(document.id),
                "qr_codes_count": len(qr_codes_data),
                "pages_processed": len(qr_codes_data),
                "output_file": output_filename,
                "download_url": f"/api/v1/pdf/download/{output_filename}"
            }

        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        error_message = str(e)
        
        # Handle specific database errors
        if "duplicate key value violates unique constraint" in error_message:
            if "documents_enovia_id_key" in error_message:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Document with ENOVIA ID '{enovia_id}' already exists. Please use a different ENOVIA ID or update the existing document."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A document with this information already exists. Please check your input data."
                )
        elif "EOF marker not found" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PDF file. Please ensure the file is a valid PDF document."
            )
        elif "expected str, bytes or os.PathLike object" in error_message:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing PDF file. Please try again or contact support."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing PDF: {error_message}"
            )


@router.get("/download/{filename}", summary="Download processed PDF", description="Download processed PDF with QR codes")
async def download_processed_pdf(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download processed PDF with QR codes
    """
    try:
        # Validate filename to prevent directory traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename"
            )
        
        # Check if file exists
        output_dir = "/app/tmp/processed_pdfs"
        file_path = os.path.join(output_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Return file for download
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error downloading file: {str(e)}"
        )
