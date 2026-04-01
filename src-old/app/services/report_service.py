"""
Report Service for PMKT Warehouse Management System.
Orchestrates comprehensive report generation with business logic and data aggregation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from app.exceptions.business_exceptions import (
    ReportGenerationError,
    InvalidReportParametersError,
)
from app.repositories.interfaces.interfaces import (
    IProductRepo,
    IDocumentRepo,
    IWarehouseRepo,
    IInventoryRepo,
)
from app.models.document_domain import DocumentType, DocumentStatus, Document
from app.models.product_domain import Product
from app.services.document_report import DocumentReport, DocumentReportItem


class ReportService:
    """
    Orchestrates report generation with comprehensive business logic.
    Handles data aggregation, calculations, and business insights.
    """

    def __init__(
        self,
        product_repo: IProductRepo,
        document_repo: IDocumentRepo,
        warehouse_repo: IWarehouseRepo,
        inventory_repo: IInventoryRepo,
    ):
        self.product_repo = product_repo
        self.document_repo = document_repo
        self.warehouse_repo = warehouse_repo
        self.inventory_repo = inventory_repo

    def generate_inventory_report(
        self, warehouse_id: Optional[int] = None, low_stock_threshold: int = 10
    ) -> Dict[str, Any]:
        """
        Generate comprehensive inventory report with business insights.

        Orchestrates:
        1. Aggregate inventory data across warehouses or for specific warehouse
        2. Calculate business metrics (value, turnover, etc.)
        3. Identify low stock items
        4. Provide recommendations
        """
        try:
            if warehouse_id:
                return self._generate_warehouse_inventory_report(
                    warehouse_id, low_stock_threshold
                )
            else:
                return self._generate_total_inventory_report(low_stock_threshold)
        except Exception as e:
            raise ReportGenerationError(
                f"Failed to generate inventory report: {str(e)}"
            )

    def generate_product_movement_report(
        self,
        product_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Generate product movement report showing inflows and outflows.

        Orchestrates:
        1. Analyze document history for product movements
        2. Calculate net movement and trends
        3. Identify seasonal patterns
        4. Provide forecasting insights
        """
        try:
            # Set default date range (last 30 days)
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)

            documents = self.document_repo.get_all()
            filtered_docs = self._filter_documents_by_date(
                documents, start_date, end_date
            )

            if product_id:
                return self._generate_single_product_movement_report(
                    product_id, filtered_docs, start_date, end_date
                )
            else:
                return self._generate_all_products_movement_report(
                    filtered_docs, start_date, end_date
                )

        except Exception as e:
            raise ReportGenerationError(
                f"Failed to generate product movement report: {str(e)}"
            )

    def generate_warehouse_performance_report(
        self,
        warehouse_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """
        Generate warehouse performance report with KPIs.

        Orchestrates:
        1. Analyze warehouse operations efficiency
        2. Calculate throughput and utilization metrics
        3. Identify bottlenecks and optimization opportunities
        4. Compare performance across warehouses
        """
        try:
            # Set default date range
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)

            documents = self.document_repo.get_all()
            filtered_docs = self._filter_documents_by_date(
                documents, start_date, end_date
            )

            if warehouse_id:
                return self._generate_single_warehouse_performance_report(
                    warehouse_id, filtered_docs, start_date, end_date
                )
            else:
                return self._generate_all_warehouses_performance_report(
                    filtered_docs, start_date, end_date
                )

        except Exception as e:
            raise ReportGenerationError(
                f"Failed to generate warehouse performance report: {str(e)}"
            )

    def generate_business_overview_report(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive business overview report.

        Orchestrates:
        1. Aggregate all key business metrics
        2. Provide executive summary
        3. Identify trends and alerts
        4. Generate actionable insights
        """
        try:
            # Set default date range (last 30 days)
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=30)

            # Gather all data sources
            documents = self.document_repo.get_all()
            filtered_docs = self._filter_documents_by_date(
                documents, start_date, end_date
            )

            inventory_data = self._calculate_inventory_metrics()
            document_metrics = self._calculate_document_metrics(filtered_docs)
            warehouse_metrics = self._calculate_warehouse_metrics()

            # Generate insights
            insights = self._generate_business_insights(
                inventory_data, document_metrics, warehouse_metrics
            )

            return {
                "report_type": "business_overview",
                "period": {"start_date": start_date, "end_date": end_date},
                "generated_at": datetime.now(),
                "inventory_summary": inventory_data,
                "operations_summary": document_metrics,
                "warehouse_summary": warehouse_metrics,
                "key_insights": insights,
                "recommendations": self._generate_recommendations(insights),
            }

        except Exception as e:
            raise ReportGenerationError(
                f"Failed to generate business overview report: {str(e)}"
            )

    def _generate_warehouse_inventory_report(
        self, warehouse_id: int, low_stock_threshold: int
    ) -> Dict[str, Any]:
        """Generate inventory report for specific warehouse."""
        warehouse = self.warehouse_repo.get(warehouse_id)
        if not warehouse:
            raise InvalidReportParametersError(f"Warehouse {warehouse_id} not found")

        inventory_items = self.warehouse_repo.get_warehouse_inventory(warehouse_id)
        products = self._get_products_dict()

        report_items = []
        total_value = 0
        low_stock_items = []

        for item in inventory_items:
            product = products.get(item.product_id)
            if product:
                item_value = product.price * item.quantity
                total_value += item_value

                report_item = {
                    "product_id": item.product_id,
                    "product_name": product.name,
                    "quantity": item.quantity,
                    "unit_price": product.price,
                    "total_value": item_value,
                }
                report_items.append(report_item)

                if item.quantity <= low_stock_threshold:
                    low_stock_items.append(report_item)

        return {
            "report_type": "warehouse_inventory",
            "warehouse": {"id": warehouse.warehouse_id, "location": warehouse.location},
            "generated_at": datetime.now(),
            "total_items": len(report_items),
            "total_value": total_value,
            "inventory_items": report_items,
            "low_stock_items": low_stock_items,
            "low_stock_threshold": low_stock_threshold,
        }

    def _generate_total_inventory_report(
        self, low_stock_threshold: int
    ) -> Dict[str, Any]:
        """Generate total inventory report across all warehouses."""
        all_inventory = self.inventory_repo.get_all()
        products = self._get_products_dict()
        warehouses = self._get_warehouses_dict()

        report_items = []
        warehouse_breakdown = {}
        total_value = 0

        # Calculate total inventory by product
        for item in all_inventory:
            product = products.get(item.product_id)
            if product:
                item_value = product.price * item.quantity
                total_value += item_value

                report_items.append(
                    {
                        "product_id": item.product_id,
                        "product_name": product.name,
                        "total_quantity": item.quantity,
                        "unit_price": product.price,
                        "total_value": item_value,
                    }
                )

        # Calculate warehouse breakdown
        for warehouse_id, warehouse in warehouses.items():
            wh_inventory = self.warehouse_repo.get_warehouse_inventory(warehouse_id)
            wh_value = 0
            wh_items = []

            for item in wh_inventory:
                product = products.get(item.product_id)
                if product:
                    item_value = product.price * item.quantity
                    wh_value += item_value
                    wh_items.append(
                        {
                            "product_id": item.product_id,
                            "product_name": product.name,
                            "quantity": item.quantity,
                            "value": item_value,
                        }
                    )

            warehouse_breakdown[warehouse_id] = {
                "warehouse_location": warehouse.location,
                "total_items": len(wh_items),
                "total_value": wh_value,
                "inventory_items": wh_items,
            }

        return {
            "report_type": "total_inventory",
            "generated_at": datetime.now(),
            "total_products": len(report_items),
            "total_value": total_value,
            "products": report_items,
            "warehouse_breakdown": warehouse_breakdown,
            "low_stock_threshold": low_stock_threshold,
        }

    def _generate_single_product_movement_report(
        self,
        product_id: int,
        documents: List[Document],
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """Generate movement report for single product."""
        product = self.product_repo.get(product_id)
        if not product:
            raise InvalidReportParametersError(f"Product {product_id} not found")

        movements = []
        total_imported = 0
        total_exported = 0
        total_transferred_in = 0
        total_transferred_out = 0

        for doc in documents:
            if doc.status == DocumentStatus.POSTED:
                for item in doc.items:
                    if item.product_id == product_id:
                        movement = {
                            "document_id": doc.document_id,
                            "document_type": doc.doc_type.value,
                            "date": doc.posted_at.date()
                            if doc.posted_at
                            else doc.created_at.date(),
                            "quantity": item.quantity,
                            "warehouse_from": doc.from_warehouse_id,
                            "warehouse_to": doc.to_warehouse_id,
                        }
                        movements.append(movement)

                        if doc.doc_type == DocumentType.IMPORT:
                            total_imported += item.quantity
                        elif doc.doc_type in (DocumentType.EXPORT, DocumentType.SALE):
                            total_exported += item.quantity
                        elif doc.doc_type == DocumentType.TRANSFER:
                            if (
                                doc.from_warehouse_id
                            ):  # This product was transferred out
                                total_transferred_out += item.quantity
                            if doc.to_warehouse_id:  # This product was transferred in
                                total_transferred_in += item.quantity

        net_movement = (
            total_imported
            + total_transferred_in
            - total_exported
            - total_transferred_out
        )

        return {
            "report_type": "product_movement",
            "product": {
                "id": product.product_id,
                "name": product.name,
                "current_stock": self.inventory_repo.get_quantity(product_id),
            },
            "period": {"start_date": start_date, "end_date": end_date},
            "generated_at": datetime.now(),
            "summary": {
                "total_imported": total_imported,
                "total_exported": total_exported,
                "total_transferred_in": total_transferred_in,
                "total_transferred_out": total_transferred_out,
                "net_movement": net_movement,
            },
            "movements": movements,
        }

    def _generate_all_products_movement_report(
        self, documents: List[Document], start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Generate movement report for all products."""
        product_movements = {}
        products = self._get_products_dict()

        for doc in documents:
            if doc.status == DocumentStatus.POSTED:
                for item in doc.items:
                    product_id = item.product_id
                    if product_id not in product_movements:
                        product_movements[product_id] = {
                            "product_name": products.get(product_id).name
                            if products.get(product_id)
                            else f"Product {product_id}",
                            "total_imported": 0,
                            "total_exported": 0,
                            "total_transferred_in": 0,
                            "total_transferred_out": 0,
                            "movements": [],
                        }

                    movement = {
                        "document_id": doc.document_id,
                        "document_type": doc.doc_type.value,
                        "date": doc.posted_at.date()
                        if doc.posted_at
                        else doc.created_at.date(),
                        "quantity": item.quantity,
                    }
                    product_movements[product_id]["movements"].append(movement)

                    if doc.doc_type == DocumentType.IMPORT:
                        product_movements[product_id]["total_imported"] += item.quantity
                    elif doc.doc_type in (DocumentType.EXPORT, DocumentType.SALE):
                        product_movements[product_id]["total_exported"] += item.quantity
                    elif doc.doc_type == DocumentType.TRANSFER:
                        if doc.from_warehouse_id:
                            product_movements[product_id]["total_transferred_out"] += (
                                item.quantity
                            )
                        if doc.to_warehouse_id:
                            product_movements[product_id]["total_transferred_in"] += (
                                item.quantity
                            )

        # Calculate net movements
        for product_id, data in product_movements.items():
            data["net_movement"] = (
                data["total_imported"]
                + data["total_transferred_in"]
                - data["total_exported"]
                - data["total_transferred_out"]
            )

        return {
            "report_type": "all_products_movement",
            "period": {"start_date": start_date, "end_date": end_date},
            "generated_at": datetime.now(),
            "product_movements": product_movements,
        }

    def _generate_single_warehouse_performance_report(
        self,
        warehouse_id: int,
        documents: List[Document],
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """Generate performance report for single warehouse."""
        warehouse = self.warehouse_repo.get(warehouse_id)
        if not warehouse:
            raise InvalidReportParametersError(f"Warehouse {warehouse_id} not found")

        # Analyze documents involving this warehouse
        imports = [
            doc
            for doc in documents
            if doc.doc_type == DocumentType.IMPORT
            and doc.to_warehouse_id == warehouse_id
        ]
        exports = [
            doc
            for doc in documents
            if doc.doc_type in (DocumentType.EXPORT, DocumentType.SALE)
            and doc.from_warehouse_id == warehouse_id
        ]
        transfers_in = [
            doc
            for doc in documents
            if doc.doc_type == DocumentType.TRANSFER
            and doc.to_warehouse_id == warehouse_id
        ]
        transfers_out = [
            doc
            for doc in documents
            if doc.doc_type == DocumentType.TRANSFER
            and doc.from_warehouse_id == warehouse_id
        ]

        # Calculate metrics
        total_operations = (
            len(imports) + len(exports) + len(transfers_in) + len(transfers_out)
        )

        total_imported_items = sum(
            sum(item.quantity for item in doc.items) for doc in imports
        )
        total_exported_items = sum(
            sum(item.quantity for item in doc.items) for doc in exports
        )
        total_transferred_in_items = sum(
            sum(item.quantity for item in doc.items) for doc in transfers_in
        )
        total_transferred_out_items = sum(
            sum(item.quantity for item in doc.items) for doc in transfers_out
        )

        current_inventory = self.warehouse_repo.get_warehouse_inventory(warehouse_id)
        current_stock_value = self._calculate_inventory_value(current_inventory)

        return {
            "report_type": "warehouse_performance",
            "warehouse": {"id": warehouse.warehouse_id, "location": warehouse.location},
            "period": {"start_date": start_date, "end_date": end_date},
            "generated_at": datetime.now(),
            "operations_summary": {
                "total_operations": total_operations,
                "imports": len(imports),
                "exports": len(exports),
                "transfers_in": len(transfers_in),
                "transfers_out": len(transfers_out),
            },
            "items_summary": {
                "total_imported": total_imported_items,
                "total_exported": total_exported_items,
                "total_transferred_in": total_transferred_in_items,
                "total_transferred_out": total_transferred_out_items,
                "net_movement": total_imported_items
                + total_transferred_in_items
                - total_exported_items
                - total_transferred_out_items,
            },
            "current_inventory": {
                "total_items": len(current_inventory),
                "total_value": current_stock_value,
            },
        }

    def _generate_all_warehouses_performance_report(
        self, documents: List[Document], start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Generate performance report for all warehouses."""
        warehouses = self._get_warehouses_dict()
        warehouse_reports = {}

        for warehouse_id, warehouse in warehouses.items():
            warehouse_reports[warehouse_id] = (
                self._generate_single_warehouse_performance_report(
                    warehouse_id, documents, start_date, end_date
                )
            )

        # Calculate system-wide metrics
        total_operations = sum(
            report["operations_summary"]["total_operations"]
            for report in warehouse_reports.values()
        )
        total_value = sum(
            report["current_inventory"]["total_value"]
            for report in warehouse_reports.values()
        )

        return {
            "report_type": "all_warehouses_performance",
            "period": {"start_date": start_date, "end_date": end_date},
            "generated_at": datetime.now(),
            "system_summary": {
                "total_warehouses": len(warehouses),
                "total_operations": total_operations,
                "total_inventory_value": total_value,
            },
            "warehouse_reports": warehouse_reports,
        }

    def _calculate_inventory_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive inventory metrics."""
        all_inventory = self.inventory_repo.get_all()
        total_value = 0
        low_stock_items = []
        products = self._get_products_dict()

        for item in all_inventory:
            product = products.get(item.product_id)
            if product:
                total_value += product.price * item.quantity
                if item.quantity <= 10:  # Low stock threshold
                    low_stock_items.append(
                        {
                            "product_id": item.product_id,
                            "product_name": product.name,
                            "quantity": item.quantity,
                        }
                    )

        return {
            "total_products": len(all_inventory),
            "total_value": total_value,
            "low_stock_count": len(low_stock_items),
            "low_stock_items": low_stock_items,
        }

    def _calculate_document_metrics(self, documents: List[Document]) -> Dict[str, Any]:
        """Calculate document/operations metrics."""
        posted_docs = [doc for doc in documents if doc.status == DocumentStatus.POSTED]

        imports = [doc for doc in posted_docs if doc.doc_type == DocumentType.IMPORT]
        exports = [doc for doc in posted_docs if doc.doc_type in (DocumentType.EXPORT, DocumentType.SALE)]
        transfers = [
            doc for doc in posted_docs if doc.doc_type == DocumentType.TRANSFER
        ]

        total_items_moved = sum(
            sum(item.quantity for item in doc.items) for doc in posted_docs
        )

        return {
            "total_documents": len(posted_docs),
            "imports": len(imports),
            "exports": len(exports),
            "transfers": len(transfers),
            "total_items_moved": total_items_moved,
        }

    def _calculate_warehouse_metrics(self) -> Dict[str, Any]:
        """Calculate warehouse utilization metrics."""
        warehouses = self._get_warehouses_dict()
        warehouse_metrics = {}

        for warehouse_id, warehouse in warehouses.items():
            inventory = self.warehouse_repo.get_warehouse_inventory(warehouse_id)
            total_items = sum(item.quantity for item in inventory)
            total_value = self._calculate_inventory_value(inventory)
            unique_products = len(inventory)

            warehouse_metrics[warehouse_id] = {
                "location": warehouse.location,
                "total_items": total_items,
                "unique_products": unique_products,
                "total_value": total_value,
            }

        return warehouse_metrics

    def _generate_business_insights(
        self, inventory_data: Dict, document_metrics: Dict, warehouse_metrics: Dict
    ) -> List[str]:
        """Generate business insights based on aggregated data."""
        insights = []

        # Inventory insights
        if inventory_data["low_stock_count"] > 0:
            insights.append(
                f"{inventory_data['low_stock_count']} products are low in stock and need replenishment"
            )

        # Operations insights
        if document_metrics["total_documents"] == 0:
            insights.append("No operations recorded in the selected period")
        else:
            avg_items_per_doc = (
                document_metrics["total_items_moved"]
                / document_metrics["total_documents"]
            )
            insights.append(
                f"Average of {avg_items_per_doc:.1f} items moved per document"
            )

        # Warehouse insights
        if warehouse_metrics:
            max_value_wh = max(
                warehouse_metrics.items(), key=lambda x: x[1]["total_value"]
            )
            insights.append(
                f"Warehouse '{max_value_wh[1]['location']}' holds the highest value inventory"
            )

        return insights

    def _generate_recommendations(self, insights: List[str]) -> List[str]:
        """Generate actionable recommendations based on insights."""
        recommendations = []

        for insight in insights:
            if "low in stock" in insight:
                recommendations.append(
                    "Consider restocking low inventory items to prevent stockouts"
                )
            if "no operations" in insight:
                recommendations.append(
                    "Review warehouse operations - no activity detected"
                )
            if "highest value" in insight:
                recommendations.append(
                    "Focus security measures on high-value inventory locations"
                )

        if not recommendations:
            recommendations.append(
                "System operating normally - continue monitoring key metrics"
            )

        return recommendations

    def _filter_documents_by_date(
        self, documents: List[Document], start_date: date, end_date: date
    ) -> List[Document]:
        """Filter documents by date range."""
        return [
            doc
            for doc in documents
            if doc.created_at.date() >= start_date and doc.created_at.date() <= end_date
        ]

    def _get_products_dict(self) -> Dict[int, Product]:
        """Get all products as a dictionary for quick lookup."""
        products = {}
        all_products = self.product_repo.get_all()
        # Handle both dict and list return types
        if isinstance(all_products, dict):
            for product_id, product in all_products.items():
                products[product_id] = product
        else:
            for product in all_products:
                products[product.product_id] = product
        return products

    def _get_warehouses_dict(self) -> Dict[int, Any]:
        """Get all warehouses as a dictionary for quick lookup."""
        return self.warehouse_repo.get_all()

    def _calculate_inventory_value(self, inventory_items: List) -> float:
        """Calculate total value of inventory items."""
        products = self._get_products_dict()
        total_value = 0

        for item in inventory_items:
            product = products.get(item.product_id)
            if product:
                total_value += product.price * item.quantity

        return total_value

    def generate_document_report(
        self,
        doc_type: Optional[DocumentType] = None,
        status: Optional[DocumentStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> DocumentReport:
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
                report_items.append(
                    DocumentReportItem(
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
                        approved_by=doc.approved_by,
                    )
                )

            # Calculate summary
            type_summary = {}
            status_summary = {}

            for item in report_items:
                type_summary[item.doc_type.value] = (
                    type_summary.get(item.doc_type.value, 0) + 1
                )
                status_summary[item.status.value] = (
                    status_summary.get(item.status.value, 0) + 1
                )

            filters = {
                "doc_type": doc_type.value if doc_type else None,
                "status": status.value if status else None,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            }

            return DocumentReport(
                filters=filters,
                documents=report_items,
                type_summary=type_summary,
                status_summary=status_summary,
                generated_at=datetime.now(),
            )
        except Exception as e:
            raise ReportGenerationError(f"Failed to generate document report: {str(e)}")
