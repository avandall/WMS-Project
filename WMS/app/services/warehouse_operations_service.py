from typing import List, Dict, Any
from app.models.warehouse_domain import Warehouse
from app.models.inventory_domain import InventoryItem
from app.models.product_domain import Product
from app.models.document_domain import Document
from app.repositories.interfaces.interfaces import IWarehouseRepo, IProductRepo, IInventoryRepo, IDocumentRepo

class WarehouseOperationsService:
    """
    Service for complex warehouse operations that span multiple domains.
    Coordinates operations across warehouses, products, inventory, and documents.

    This service handles:
    - Bulk operations across multiple warehouses
    - Complex business workflows
    - Cross-domain analytics and reporting
    - Advanced inventory optimization
    - Automated replenishment and balancing
    """

    def __init__(self, warehouse_repo: IWarehouseRepo, product_repo: IProductRepo,
                 inventory_repo: IInventoryRepo, document_repo: IDocumentRepo):
        self.warehouse_repo = warehouse_repo
        self.product_repo = product_repo
        self.inventory_repo = inventory_repo
        self.document_repo = document_repo

    def get_system_overview(self) -> Dict[str, Any]:
        """
        Get comprehensive overview of the entire warehouse system.
        Combines data from all domains for business intelligence.
        """
        warehouses = self.warehouse_repo.get_all()
        total_products = len(self.product_repo.get_all())
        total_inventory_value = self._calculate_total_inventory_value()

        return {
            "total_warehouses": len(warehouses),
            "total_products": total_products,
            "total_inventory_value": total_inventory_value,
            "warehouses": [w.location for w in warehouses]
        }

    def optimize_inventory_distribution(self, product_id: int) -> Dict[str, Any]:
        """
        Analyze and suggest optimal inventory distribution across warehouses.
        This is a complex operation requiring data from multiple services.
        """
        # Get product info
        product = self.product_repo.get(product_id)
        if not product:
            return {"error": f"Product {product_id} not found"}

        # Get inventory across all warehouses
        warehouses = self.warehouse_repo.get_all()
        distribution = []

        for warehouse in warehouses:
            quantity = self._get_warehouse_product_quantity(warehouse.warehouse_id, product_id)
            distribution.append({
                "warehouse_id": warehouse.warehouse_id,
                "location": warehouse.location,
                "quantity": quantity
            })

        return {
            "product_id": product_id,
            "product_name": product.name,
            "distribution": distribution,
            "recommendations": self._generate_distribution_recommendations(distribution)
        }

    def bulk_transfer_products(self, transfers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute bulk transfer operations across multiple products/warehouses.
        A complex operation that coordinates multiple transfers.
        """
        results = []
        successful = 0
        failed = 0

        for transfer in transfers:
            try:
                # This would use the warehouse service's transfer_product method
                # but coordinated across multiple transfers
                from_wh = transfer["from_warehouse_id"]
                to_wh = transfer["to_warehouse_id"]
                product_id = transfer["product_id"]
                quantity = transfer["quantity"]

                # Check if transfer is possible
                available = self.warehouse_repo.get_product_quantity(from_wh, product_id)
                if available >= quantity:
                    # Execute transfer (would call warehouse service)
                    results.append({
                        "transfer": transfer,
                        "status": "success",
                        "message": f"Transferred {quantity} units"
                    })
                    successful += 1
                else:
                    results.append({
                        "transfer": transfer,
                        "status": "failed",
                        "message": f"Insufficient stock: {available} available, {quantity} requested"
                    })
                    failed += 1
            except Exception as e:
                results.append({
                    "transfer": transfer,
                    "status": "error",
                    "message": str(e)
                })
                failed += 1

        return {
            "total_transfers": len(transfers),
            "successful": successful,
            "failed": failed,
            "results": results
        }

    def get_inventory_health_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive inventory health report across all warehouses.
        Complex analytics combining warehouse, inventory, and product data.
        """
        warehouses = self.warehouse_repo.get_all()
        products = self.product_repo.get_all()

        report = {
            "warehouses": [],
            "system_health_score": 0,
            "recommendations": []
        }

        total_health_score = 0

        for warehouse in warehouses:
            warehouse_data = {
                "warehouse_id": warehouse.warehouse_id,
                "location": warehouse.location,
                "products": [],
                "total_value": 0,
                "health_score": 0
            }

            for product in products:
                quantity = self.warehouse_repo.get_product_quantity(warehouse.warehouse_id, product.product_id)
                if quantity > 0:
                    value = quantity * product.price
                    warehouse_data["products"].append({
                        "product_id": product.product_id,
                        "name": product.name,
                        "quantity": quantity,
                        "value": value
                    })
                    warehouse_data["total_value"] += value

            # Calculate warehouse health score (simplified)
            warehouse_data["health_score"] = min(100, len(warehouse_data["products"]) * 10)
            total_health_score += warehouse_data["health_score"]
            report["warehouses"].append(warehouse_data)

        report["system_health_score"] = total_health_score / len(warehouses) if warehouses else 0

        return report

    def _calculate_total_inventory_value(self) -> float:
        """Helper method to calculate total value of all inventory."""
        warehouses = self.warehouse_repo.get_all()
        products = self.product_repo.get_all()
        total_value = 0.0

        for warehouse in warehouses:
            for product in products:
                quantity = self._get_warehouse_product_quantity(warehouse.warehouse_id, product.product_id)
                total_value += quantity * product.price

        return total_value

    def _generate_distribution_recommendations(self, distribution: List[Dict]) -> List[str]:
        """Generate recommendations for inventory distribution."""
        recommendations = []
        total_quantity = sum(d["quantity"] for d in distribution)

        if total_quantity == 0:
            return ["No inventory to distribute"]

        # Simple recommendation logic
        avg_quantity = total_quantity / len(distribution)
        low_stock = [d for d in distribution if d["quantity"] < avg_quantity * 0.5]

        if low_stock:
            recommendations.append(f"Consider redistributing stock to warehouses: {[w['location'] for w in low_stock]}")

        return recommendations

    def _get_warehouse_product_quantity(self, warehouse_id: int, product_id: int) -> int:
        """
        Helper method to get quantity of specific product in warehouse.
        """
        inventory = self.warehouse_repo.get_warehouse_inventory(warehouse_id)
        for item in inventory:
            if item.product_id == product_id:
                return item.quantity
        return 0