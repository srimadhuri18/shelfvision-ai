from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models import Shelf, Section, Alert
from ..config import settings

class AnomalyDetector:
    def __init__(self):
        self.empty_threshold = settings.EMPTY_THRESHOLD_RATIO
        self.low_stock_ratio = settings.LOW_STOCK_RATIO

    def analyze_shelf(
        self,
        shelf: Shelf,
        detections: List[Dict[str, Any]],
        db: Session = None,
        create_alerts: bool = True
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Maps detections into sections, computes status, and triggers alerts in DB.
        Returns:
            sections_status: List of section status dicts
            enriched_detections: Detections with section_id and is_misplaced marked
        """
        sections_status = []
        enriched_detections = [dict(d) for d in detections]

        for sec in shelf.sections:
            x1, y1, x2, y2 = sec.roi_x1, sec.roi_y1, sec.roi_x2, sec.roi_y2
            sec_area = max(0.001, (x2 - x1) * (y2 - y1))

            items_in_section = []
            misplaced_in_section = []
            total_box_area = 0.0

            for det in enriched_detections:
                cx, cy = det["center"]
                if x1 <= cx <= x2 and y1 <= cy <= y2:
                    det["section_id"] = sec.id
                    items_in_section.append(det)

                    # Compute intersection area approximately
                    bx1, by1, bx2, by2 = det["normalized_bbox"]
                    bw = max(0.0, min(x2, bx2) - max(x1, bx1))
                    bh = max(0.0, min(y2, by2) - max(y1, by1))
                    total_box_area += (bw * bh)

                    # Check product misplacement
                    # Compare with expected category or name
                    det_cat = det.get("category", "").lower()
                    det_cls = det.get("class_name", "").lower()
                    exp_cat = sec.expected_category.lower()
                    exp_prod = sec.expected_product_name.lower()

                    # Direct match or category match
                    is_match = (
                        exp_cat in det_cat or det_cat in exp_cat or
                        exp_prod in det_cls or det_cls in exp_prod or
                        det_cls in exp_cat
                    )

                    if not is_match and det.get("confidence", 0) >= settings.DEFAULT_CONFIDENCE:
                        det["is_misplaced"] = True
                        misplaced_in_section.append(det)
                    else:
                        det["is_misplaced"] = False

            detected_count = len(items_in_section)
            misplaced_count = len(misplaced_in_section)
            occupancy_ratio = min(1.0, round(total_box_area / sec_area, 2))

            # Determine Section Status
            if detected_count == 0 or occupancy_ratio < self.empty_threshold:
                status = "EMPTY"
                severity = "CRITICAL"
                alert_type = "EMPTY"
                msg = f"Empty shelf space detected at {sec.label} (Expected: {sec.expected_product_name})."
            elif misplaced_count > 0:
                status = "MISPLACED"
                severity = "WARNING"
                alert_type = "MISPLACED"
                misplaced_names = ", ".join(set(d["class_name"] for d in misplaced_in_section))
                msg = f"Incorrect product placement in {sec.label}: Found '{misplaced_names}' (Expected: '{sec.expected_product_name}')."
            elif detected_count <= sec.low_stock_threshold:
                status = "LOW_STOCK"
                severity = "WARNING"
                alert_type = "LOW_STOCK"
                msg = f"Low stock alert on {sec.label}: {detected_count}/{sec.capacity} items remaining (Threshold: {sec.low_stock_threshold})."
            else:
                status = "NORMAL"
                severity = None
                alert_type = None
                msg = None

            sec_info = {
                "section_id": sec.id,
                "label": sec.label,
                "expected_product": sec.expected_product_name,
                "expected_category": sec.expected_category,
                "detected_count": detected_count,
                "capacity": sec.capacity,
                "low_stock_threshold": sec.low_stock_threshold,
                "status": status,
                "misplaced_count": misplaced_count,
                "occupancy_ratio": occupancy_ratio,
                "roi_x1": sec.roi_x1,
                "roi_y1": sec.roi_y1,
                "roi_x2": sec.roi_x2,
                "roi_y2": sec.roi_y2
            }
            sections_status.append(sec_info)

            # Persist alert in DB if anomaly detected and not duplicated
            if create_alerts and db is not None and alert_type is not None:
                self._dispatch_alert(
                    db=db,
                    shelf_id=shelf.id,
                    section_id=sec.id,
                    section_label=sec.label,
                    alert_type=alert_type,
                    severity=severity,
                    message=msg
                )

        return sections_status, enriched_detections

    def _dispatch_alert(
        self,
        db: Session,
        shelf_id: str,
        section_id: str,
        section_label: str,
        alert_type: str,
        severity: str,
        message: str
    ):
        """Dispatches an alert ensuring no duplicate unacknowledged alerts within a cooldown period."""
        cooldown = datetime.utcnow() - timedelta(minutes=3)
        existing = db.query(Alert).filter(
            Alert.section_id == section_id,
            Alert.alert_type == alert_type,
            Alert.is_acknowledged == False,
            Alert.created_at >= cooldown
        ).first()

        if not existing:
            alert = Alert(
                shelf_id=shelf_id,
                section_id=section_id,
                section_label=section_label,
                alert_type=alert_type,
                severity=severity,
                message=message,
                is_acknowledged=False
            )
            db.add(alert)
            db.commit()

anomaly_detector = AnomalyDetector()
