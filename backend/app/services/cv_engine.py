import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

# COCO to Retail Category Mapping helper
COCO_RETAIL_MAP = {
    "bottle": "Beverages",
    "cup": "Dairy & Yogurts",
    "wine glass": "Beverages",
    "banana": "Produce",
    "apple": "Produce",
    "sandwich": "Snacks",
    "orange": "Produce",
    "broccoli": "Produce",
    "carrot": "Produce",
    "pizza": "Frozen Foods",
    "donut": "Bakery",
    "cake": "Bakery",
    "book": "Stationery",
    "cell phone": "Electronics",
    "remote": "Electronics",
    "bowl": "Kitchenware",
    "vase": "Home & Decor",
    "toothbrush": "Personal Care"
}

class CVEngine:
    def __init__(self, model_name: str = "yolov8n.pt", confidence: float = 0.35):
        self.model_name = model_name
        self.confidence = confidence
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from ultralytics import YOLO
            logger.info(f"Loading YOLO model: {self.model_name}")
            self.model = YOLO(self.model_name)
            logger.info("YOLO model loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load YOLO model ({e}). Fallback to simulation/mock detector.")
            self.model = None

    def detect_products(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Runs object detection on a BGR image frame.
        Returns list of detected objects with bounding boxes and normalized coords.
        """
        h, w = frame.shape[:2]
        detections = []

        if self.model is not None:
            try:
                results = self.model(frame, conf=self.confidence, verbose=False)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        cls_id = int(box.cls[0].item())
                        cls_name = r.names[cls_id]
                        conf = float(box.conf[0].item())
                        
                        cx = ((x1 + x2) / 2.0) / w
                        cy = ((y1 + y2) / 2.0) / h
                        retail_category = COCO_RETAIL_MAP.get(cls_name.lower(), "General Merchandise")

                        detections.append({
                            "class_name": cls_name,
                            "category": retail_category,
                            "confidence": round(conf, 2),
                            "bbox": [x1, y1, x2, y2],
                            "center": [round(cx, 4), round(cy, 4)],
                            "normalized_bbox": [
                                round(x1 / w, 4), round(y1 / h, 4),
                                round(x2 / w, 4), round(y2 / h, 4)
                            ]
                        })
                return detections
            except Exception as e:
                logger.error(f"Error during YOLO inference: {e}")

        # Fallback heuristic / mock detector for demonstration if YOLO is loading
        return detections

    def draw_shelf_overlay(
        self,
        frame: np.ndarray,
        sections: List[Dict[str, Any]],
        detections: List[Dict[str, Any]]
    ) -> np.ndarray:
        """
        Draws shelf section boundaries, status color codes, and product bounding boxes.
        """
        overlay = frame.copy()
        h, w = frame.shape[:2]

        # 1. Draw shelf ROI zones
        for sec in sections:
            x1 = int(sec["roi_x1"] * w)
            y1 = int(sec["roi_y1"] * h)
            x2 = int(sec["roi_x2"] * w)
            y2 = int(sec["roi_y2"] * h)

            status = sec.get("status", "NORMAL")
            # Color coding (BGR):
            # Normal: Green (46, 204, 113)
            # Low Stock: Amber (39, 174, 96 -> or 0, 165, 255)
            # Empty / Critical: Red (46, 46, 231)
            # Misplaced: Purple (200, 50, 200)
            if status == "EMPTY":
                color = (0, 0, 230) # Red
            elif status == "LOW_STOCK":
                color = (0, 165, 255) # Orange
            elif status == "MISPLACED":
                color = (212, 75, 147) # Violet/Purple
            else:
                color = (0, 200, 80) # Green

            # Draw semi-transparent rectangle
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
            
            # Header tag for section
            header_text = f"{sec['label']} ({status})"
            sub_text = f"Count: {sec.get('detected_count', 0)}/{sec.get('capacity', 10)}"
            
            cv2.rectangle(overlay, (x1, y1 - 24), (x1 + len(header_text) * 10 + 20, y1), color, -1)
            cv2.putText(overlay, header_text, (x1 + 5, y1 - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
            
            cv2.putText(overlay, sub_text, (x1 + 8, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (240, 240, 240), 1)

        # 2. Draw detected product boxes
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            is_misplaced = det.get("is_misplaced", False)
            box_color = (0, 0, 255) if is_misplaced else (255, 200, 0) # Cyan/Yellow vs Red
            
            cv2.rectangle(overlay, (x1, y1), (x2, y2), box_color, 2)
            label = f"{det['class_name']} {int(det['confidence']*100)}%"
            if is_misplaced:
                label += " [MISPLACED]"
                
            cv2.putText(overlay, label, (x1, max(y1 - 6, 12)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, box_color, 1)

        # Blend overlay
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        return frame

cv_engine = CVEngine()
