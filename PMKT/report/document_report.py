"""
Document Report classes for PMKT Warehouse Management System.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from dataclasses import dataclass
from ..module.models import DocumentType, DocumentStatus

@dataclass
class DocumentReportItem:
    """Represents a document in report."""
    document_id: int
    doc_type: DocumentType
    status: DocumentStatus
    date: datetime
    from_warehouse_id: Optional[int]
    to_warehouse_id: Optional[int]
    total_items: int
    total_quantity: int
    total_value: float
    created_by: str
    approved_by: Optional[str]

@dataclass
class DocumentReport:
    """Document report with filters and summary."""
    filters: Dict[str, Any]
    documents: List[DocumentReportItem]
    type_summary: Dict[str, int]
    status_summary: Dict[str, int]
    generated_at: datetime

    @property
    def total_documents(self) -> int:
        return len(self.documents)

    @property
    def total_value(self) -> float:
        return sum(doc.total_value for doc in self.documents)