from typing import List, Dict, Any
from ..config import settings

class ShelfHealthCalculator:
    def __init__(self):
        self.w_avail = settings.WEIGHT_AVAILABILITY
        self.w_place = settings.WEIGHT_PLACEMENT
        self.w_stock = settings.WEIGHT_STOCK_LEVEL

    def calculate_score(self, sections_status: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates the AI Shelf Health Score (SHS) from live section statuses.
        Returns a breakdown with percentages and category status.
        """
        if not sections_status:
            return {
                "availability_pct": 100.0,
                "placement_accuracy_pct": 100.0,
                "stock_level_pct": 100.0,
                "health_score": 100.0,
                "status_label": "EXCELLENT"
            }

        total_sections = len(sections_status)
        active_sections = sum(1 for s in sections_status if s["detected_count"] > 0)
        availability_pct = round((active_sections / total_sections) * 100.0, 1)

        total_detected = sum(s["detected_count"] for s in sections_status)
        total_misplaced = sum(s["misplaced_count"] for s in sections_status)

        if total_detected > 0:
            correct_items = max(0, total_detected - total_misplaced)
            placement_accuracy_pct = round((correct_items / total_detected) * 100.0, 1)
        else:
            placement_accuracy_pct = 100.0

        total_capacity = sum(s["capacity"] for s in sections_status)
        if total_capacity > 0:
            capped_stock = sum(min(s["detected_count"], s["capacity"]) for s in sections_status)
            stock_level_pct = round((capped_stock / total_capacity) * 100.0, 1)
        else:
            stock_level_pct = 100.0

        # Weighted combination (0 - 100)
        raw_score = (
            (self.w_avail * availability_pct) +
            (self.w_place * placement_accuracy_pct) +
            (self.w_stock * stock_level_pct)
        ) / 100.0

        health_score = round(min(100.0, max(0.0, raw_score)), 1)

        if health_score >= 85.0:
            status_label = "EXCELLENT"
        elif health_score >= 70.0:
            status_label = "GOOD"
        elif health_score >= 50.0:
            status_label = "WARNING"
        else:
            status_label = "CRITICAL"

        return {
            "availability_pct": availability_pct,
            "placement_accuracy_pct": placement_accuracy_pct,
            "stock_level_pct": stock_level_pct,
            "health_score": health_score,
            "status_label": status_label
        }

health_calculator = ShelfHealthCalculator()
