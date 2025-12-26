"""
Report Service for PMKT Warehouse Management System.
Provides various report generation functionalities.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from app.exceptions.business_exceptions import ReportGenerationError, InvalidReportParametersError
from app.repositories.interfaces.interfaces import IProductRepo, IDocumentRepo, IWarehouseRepo, IInventoryRepo
from app.models.models import DocumentType, DocumentStatus
from app.services.inventory_report import WarehouseInventoryReport, TotalInventoryReport, InventoryReportItem
from app.services.document_report import DocumentReport, DocumentReportItem
from app.services.product_report import ProductMovementReport, ProductMovementItem
from app.services.warehouse_report import WarehousePerformanceReport, WarehousePerformanceItem
from app.models.product_domain import Product

class ReportService:
    """Service for generating various reports."""

    def __init__(self, product_repo: IProductRepo, document_repo: IDocumentRepo,
                 warehouse_repo: IWarehouseRepo, inventory_repo: IInventoryRepo):
        self.product_repo = product_repo
        self.document_repo = document_repo
        self.warehouse_repo = warehouse_repo
        self.inventory_repo = inventory_repo

    def generate_inventory_report(self, warehouse_id: Optional[int] = None,
                                low_stock_threshold: int = 10) -> Any:
        """
        Generate inventory report.

        Args:
            warehouse_id: If provided, report for specific warehouse, else total inventory
            low_stock_threshold: Threshold for low stock alerts

        Returns:
            WarehouseInventoryReport or TotalInventoryReport
        """
        try:
            if warehouse_id:
                warehouse = self.warehouse_repo.get(warehouse_id)
                if not warehouse:
                    raise InvalidReportParametersError(f"Warehouse {warehouse_id} not found")

                products = self._get_products_dict()
                items = [InventoryReportItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    product_name=products.get(item.product_id).name if products.get(item.product_id) else None,
                    unit_value=products.get(item.product_id).price if products.get(item.product_id) else None
                ) for item in warehouse.inventory]

                low_stock_items = [item for item in items if item.quantity < low_stock_threshold]

                return WarehouseInventoryReport(
                    warehouse_id=warehouse_id,
                    warehouse_location=warehouse.location,
                    items=items,
                    low_stock_items=low_stock_items,
                    generated_at=datetime.now()
                )
            else:
                # Total inventory report
                all_items = []
                products = self._get_products_dict()

                for warehouse in self.warehouse_repo.warehouses.values():
                    for item in warehouse.inventory:
                        all_items.append(InventoryReportItem(
                            product_id=item.product_id,
                            quantity=item.quantity,
                            product_name=products.get(item.product_id).name if products.get(item.product_id) else None,
                            unit_value=products.get(item.product_id).price if products.get(item.product_id) else None
                        ))

                # Aggregate by product
                product_totals = {}
                for item in all_items:
                    if item.product_id in product_totals:
                        existing = product_totals[item.product_id]
                        product_totals[item.product_id] = InventoryReportItem(
                            product_id=item.product_id,
                            quantity=existing.quantity + item.quantity,
                            product_name=item.product_name,
                            unit_value=item.unit_value
                        )
                    else:
                        product_totals[item.product_id] = item

                low_stock_items = [item for item in product_totals.values() if item.quantity < low_stock_threshold]

                return TotalInventoryReport(
                    product_totals=list(product_totals.values()),
                    low_stock_items=low_stock_items,
                    generated_at=datetime.now()
                )
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate inventory report: {str(e)}")

    def generate_document_report(self, doc_type: Optional[DocumentType] = None,
                               status: Optional[DocumentStatus] = None,
                               start_date: Optional[date] = None,
                               end_date: Optional[date] = None) -> DocumentReport:
        """
        Generate document report.

        Args:
            doc_type: Filter by document type
            status: Filter by document status
            start_date: Filter documents from this date
            end_date: Filter documents to this date

        Returns:
            DocumentReport instance
        """
        try:
            all_docs = self.document_repo.get_all()

            # Apply filters
            filtered_docs = []
            for doc in all_docs:
                if doc_type and doc.doc_type != doc_type:
                    continue
                if status and doc.status != status:
                    continue
                if start_date and doc.date.date() < start_date:
                    continue
                if end_date and doc.date.date() > end_date:
                    continue
                filtered_docs.append(doc)

            # Create report items
            report_items = []
            for doc in filtered_docs:
                report_items.append(DocumentReportItem(
                    document_id=doc.document_id,
                    doc_type=doc.doc_type,
                    status=doc.status,
                    date=doc.date,
                    from_warehouse_id=doc.from_warehouse_id,
                    to_warehouse_id=doc.to_warehouse_id,
                    total_items=len(doc.items),
                    total_quantity=sum(item.quantity for item in doc.items),
                    total_value=doc.calculate_total_value(),
                    created_by=doc.created_by,
                    approved_by=doc.approved_by
                ))

            # Calculate summary
            type_summary = {}
            status_summary = {}

            for item in report_items:
                type_summary[item.doc_type.value] = type_summary.get(item.doc_type.value, 0) + 1
                status_summary[item.status.value] = status_summary.get(item.status.value, 0) + 1

            filters = {
                'doc_type': doc_type.value if doc_type else None,
                'status': status.value if status else None,
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            }

            return DocumentReport(
                filters=filters,
                documents=report_items,
                type_summary=type_summary,
                status_summary=status_summary,
                generated_at=datetime.now()
            )
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate document report: {str(e)}")

    def generate_product_movement_report(self, product_id: int,
                                       start_date: Optional[date] = None,
                                       end_date: Optional[date] = None) -> ProductMovementReport:
        """
        Generate product movement report showing all documents affecting a product.

        Args:
            product_id: Product ID to report on
            start_date: Start date for the report
            end_date: End date for the report

        Returns:
            ProductMovementReport instance
        """
        try:
            product = self.product_repo.get(product_id)
            if not product:
                raise InvalidReportParametersError(f"Product {product_id} not found")

            all_docs = self.document_repo.get_all()
            movements = []

            for doc in all_docs:
                if start_date and doc.date.date() < start_date:
                    continue
                if end_date and doc.date.date() > end_date:
                    continue

                # Check if document contains the product
                for item in doc.items:
                    if item.product_id == product_id:
                        movements.append(ProductMovementItem(
                            document_id=doc.document_id,
                            doc_type=doc.doc_type.value,
                            status=doc.status.value,
                            date=doc.date.isoformat(),
                            quantity=item.quantity,
                            unit_price=item.unit_price,
                            total_value=item.calculate_total_value(),
                            from_warehouse=doc.from_warehouse_id,
                            to_warehouse=doc.to_warehouse_id
                        ))
                        break

            filters = {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            }

            return ProductMovementReport(
                product_id=product_id,
                product_name=product.name,
                filters=filters,
                movements=movements,
                generated_at=datetime.now()
            )
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate product movement report: {str(e)}")

    def generate_warehouse_performance_report(self) -> WarehousePerformanceReport:
        """
        Generate warehouse performance report.

        Returns:
            WarehousePerformanceReport instance
        """
        try:
            warehouses = []
            products = self._get_products_dict()

            for warehouse in self.warehouse_repo.warehouses.values():
                total_value = warehouse.calculate_total_value(products)
                item_count = len(warehouse.inventory)
                total_quantity = sum(item.quantity for item in warehouse.inventory)

                warehouses.append(WarehousePerformanceItem(
                    warehouse_id=warehouse.warehouse_id,
                    location=warehouse.location,
                    item_count=item_count,
                    total_quantity=total_quantity,
                    total_value=total_value
                ))

            return WarehousePerformanceReport(
                warehouses=warehouses,
                generated_at=datetime.now()
            )
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate warehouse performance report: {str(e)}")

    def _get_products_dict(self) -> Dict[int, Product]:
        """Helper method to get all products as a dict."""
        products = {}
        for product in self.product_repo.products.values():
            products[product.product_id] = product
        return products