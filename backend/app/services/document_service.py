"""
Service for document management
"""

import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
import structlog

from app.models.document import Document
from app.models.qr_code import QRCode
from app.models.user import User

logger = structlog.get_logger()

class DocumentService:
    """Service for document management"""

    def __init__(self, db: Session):
        self.db = db

    async def create_or_update_document(
        self,
        enovia_id: str,
        title: str,
        revision: str,
        total_pages: int,
        created_by: uuid.UUID
    ) -> Document:
        """
        Create new document or update existing one
        If document with same enovia_id exists, mark older revisions as not actual
        """
        try:
            # Check if document with same enovia_id exists
            existing_document = self.db.query(Document).filter(
                Document.enovia_id == enovia_id
            ).first()

            if existing_document:
                # Mark all existing documents with this enovia_id as not actual
                self.db.query(Document).filter(
                    Document.enovia_id == enovia_id
                ).update({"is_actual": False})
                
                logger.info(f"Marked existing documents as not actual", 
                           enovia_id=enovia_id)

            # Create new document
            document = Document(
                enovia_id=enovia_id,
                title=title,
                revision=revision,
                current_page=total_pages,
                is_actual=True,
                created_by=created_by
            )
            
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            
            logger.info(f"Created new document", 
                       document_id=str(document.id),
                       enovia_id=enovia_id,
                       revision=revision)
            
            return document
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating/updating document", error=str(e))
            raise

    async def create_qr_code(
        self,
        document_id: uuid.UUID,
        enovia_id: str,
        revision: str,
        page_number: int,
        qr_data: str,
        created_by: uuid.UUID
    ) -> QRCode:
        """
        Create QR code record in database
        """
        try:
            # Check if QR code already exists for this page
            existing_qr = self.db.query(QRCode).filter(
                and_(
                    QRCode.enovia_id == enovia_id,
                    QRCode.revision == revision,
                    QRCode.page_number == page_number
                )
            ).first()

            if existing_qr:
                # Update existing QR code
                existing_qr.qr_data = qr_data
                existing_qr.document_id = document_id
                existing_qr.created_by = created_by
                self.db.commit()
                self.db.refresh(existing_qr)
                
                logger.info(f"Updated existing QR code", 
                           enovia_id=enovia_id,
                           revision=revision,
                           page_number=page_number)
                
                return existing_qr
            else:
                # Create new QR code
                qr_code = QRCode(
                    document_id=document_id,
                    enovia_id=enovia_id,
                    revision=revision,
                    page_number=page_number,
                    qr_data=qr_data,
                    created_by=created_by
                )
                
                self.db.add(qr_code)
                self.db.commit()
                self.db.refresh(qr_code)
                
                logger.info(f"Created new QR code", 
                           qr_id=str(qr_code.id),
                           enovia_id=enovia_id,
                           revision=revision,
                           page_number=page_number)
                
                return qr_code
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating QR code", error=str(e))
            raise

    async def get_document_by_enovia_id(
        self, 
        enovia_id: str, 
        revision: str = None
    ) -> Optional[Document]:
        """
        Get document by ENOVIA ID and optionally by revision
        """
        try:
            query = self.db.query(Document).filter(Document.enovia_id == enovia_id)
            
            if revision:
                query = query.filter(Document.revision == revision)
            else:
                # Get the most recent actual document
                query = query.filter(Document.is_actual == True)
            
            return query.first()
            
        except Exception as e:
            logger.error(f"Error getting document", error=str(e))
            return None

    async def get_qr_codes_by_document(
        self, 
        document_id: uuid.UUID
    ) -> list[QRCode]:
        """
        Get all QR codes for a document
        """
        try:
            return self.db.query(QRCode).filter(
                QRCode.document_id == document_id
            ).order_by(QRCode.page_number).all()
            
        except Exception as e:
            logger.error(f"Error getting QR codes", error=str(e))
            return []

    async def get_qr_code_by_data(
        self, 
        enovia_id: str, 
        revision: str, 
        page_number: int
    ) -> Optional[QRCode]:
        """
        Get QR code by its data components
        """
        try:
            return self.db.query(QRCode).filter(
                and_(
                    QRCode.enovia_id == enovia_id,
                    QRCode.revision == revision,
                    QRCode.page_number == page_number
                )
            ).first()
            
        except Exception as e:
            logger.error(f"Error getting QR code by data", error=str(e))
            return None

    async def mark_document_as_obsolete(
        self, 
        enovia_id: str, 
        revision: str
    ) -> bool:
        """
        Mark specific document revision as obsolete
        """
        try:
            document = self.db.query(Document).filter(
                and_(
                    Document.enovia_id == enovia_id,
                    Document.revision == revision
                )
            ).first()
            
            if document:
                document.is_actual = False
                self.db.commit()
                
                logger.info(f"Marked document as obsolete", 
                           enovia_id=enovia_id,
                           revision=revision)
                
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error marking document as obsolete", error=str(e))
            return False

    async def create_document_with_qr_codes(
        self,
        db: Session,
        enovia_id: str,
        title: str,
        revision: str,
        creator_id: str,
        qr_codes_data: list[dict],
    ) -> Document:
        """
        Creates a new document revision and associated QR codes in the database.
        If document with same enovia_id exists, creates a new revision.
        Sets previous revisions of the same enovia_id to is_actual=False.
        """
        try:
            # 1. Check if document with same enovia_id exists
            existing_document = db.query(Document).filter(
                Document.enovia_id == enovia_id
            ).first()

            if existing_document:
                # Mark all existing documents with this enovia_id as not actual
                await self._supersede_previous_revisions(db, enovia_id)
                
                # Update existing document with new revision
                existing_document.title = title
                existing_document.revision = revision
                existing_document.is_actual = True
                existing_document.updated_at = func.now()
                existing_document.created_by = creator_id
                
                # Delete old QR codes for this document
                db.query(QRCode).filter(
                    QRCode.document_id == existing_document.id
                ).delete()
                
                document = existing_document
                db.flush()  # Flush to get the document.id
                
                logger.info(
                    "Updated existing document with new revision",
                    document_id=document.id,
                    enovia_id=enovia_id,
                    revision=revision,
                )
            else:
                # Create new document
                new_document = Document(
                    enovia_id=enovia_id,
                    title=title,
                    revision=revision,
                    created_by=creator_id,
                    is_actual=True,
                    document_type="PDF",
                    business_status="DRAFT",
                    enovia_state="In Work",
                    current_page=1,
                    released_at=None,
                )
                db.add(new_document)
                db.flush()  # Flush to get the new_document.id
                document = new_document
                
                logger.info(
                    "Created new document",
                    document_id=document.id,
                    enovia_id=enovia_id,
                    revision=revision,
                )

            # 2. Create QR codes for the document
            for qr_data_item in qr_codes_data:
                new_qr_code = QRCode(
                    enovia_id=enovia_id,
                    document_id=document.id,
                    revision=revision,
                    page_number=qr_data_item["page_number"],
                    qr_data=qr_data_item["qr_data"],
                    created_by=creator_id,
                    expires_at=None,
                )
                db.add(new_qr_code)

            db.commit()
            db.refresh(document)
            logger.info(
                "Document and QR codes processed successfully",
                document_id=document.id,
                enovia_id=enovia_id,
                revision=revision,
                qr_codes_count=len(qr_codes_data),
            )
            return document
        except Exception as e:
            db.rollback()
            logger.error(
                "Error processing document with QR codes",
                enovia_id=enovia_id,
                revision=revision,
                error=str(e),
            )
            raise

    async def _supersede_previous_revisions(self, db: Session, enovia_id: str):
        """
        Marks all previous revisions of a document with the given enovia_id as not actual.
        """
        try:
            db.query(Document).filter(Document.enovia_id == enovia_id).update(
                {"is_actual": False}
            )
            db.flush()
            logger.info(
                "Superseded previous document revisions", enovia_id=enovia_id
            )
        except Exception as e:
            logger.error(
                "Error superseding previous document revisions",
                enovia_id=enovia_id,
                error=str(e),
            )
            raise
