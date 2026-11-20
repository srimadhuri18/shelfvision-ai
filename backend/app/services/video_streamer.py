import cv2
import numpy as np
import time
import math
from typing import Generator, Dict, Any, List
import logging
from .cv_engine import cv_engine
from .anomaly_detector import anomaly_detector
from .health_calculator import health_calculator
from ..database import SessionLocal
from ..models import Shelf

logger = logging.getLogger(__name__)

class VideoStreamer:
    def __init__(self):
        self.active_sources = {}
        self.simulation_step = 0

    def generate_synthetic_shelf_frame(self, width: int = 640, height: int = 480) -> np.ndarray:
        """
        Generates a synthetic realistic retail shelf visual with shelves, products, and labels.
        Dynamically simulates customer picking up items or restocking over time.
        """
        self.simulation_step += 1
        t = self.simulation_step * 0.05
        
        # Base supermarket shelf background (clean dark steel/wood shelf)
        frame = np.full((height, width, 3), (35, 38, 42), dtype=np.uint8)
        
        # Shelf divider lines (2 rows x 2 cols)
        row_split = height // 2
        col_split = width // 2

        # Shelf rails
        cv2.rectangle(frame, (0, row_split - 8), (width, row_split + 4), (70, 75, 82), -1)
        cv2.rectangle(frame, (0, height - 12), (width, height), (70, 75, 82), -1)
        cv2.line(frame, (col_split, 0), (col_split, height), (55, 60, 68), 2)

        # Section 1 (Top Left): Beverages (Coke / Soda bottles)
        # Periodic stock reduction to trigger Low Stock
        coke_count = max(2, int(6 + 2 * math.sin(t * 0.8)))
        for i in range(coke_count):
            bx = 35 + (i * 42)
            by = row_split - 120
            # Red soda can / bottle
            cv2.rectangle(frame, (bx, by), (bx + 30, row_split - 10), (30, 30, 210), -1)
            cv2.circle(frame, (bx + 15, by - 6), 6, (200, 200, 200), -1)
            cv2.putText(frame, "COLA", (bx + 2, by + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (255, 255, 255), 1)

        # Section 2 (Top Right): Dairy / Fruit (Apples/Produce)
        # Periodically drops to 0 to demonstrate EMPTY shelf detection!
        apple_phase = math.sin(t * 0.5)
        apple_count = 0 if apple_phase < -0.4 else int(4 + 2 * math.cos(t * 0.5))
        for i in range(apple_count):
            ax = col_split + 40 + (i * 50)
            ay = row_split - 70
            cv2.circle(frame, (ax + 18, ay), 20, (30, 180, 50), -1) # Green apple
            cv2.putText(frame, "APPLE", (ax + 2, ay + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (255, 255, 255), 1)

        # Section 3 (Bottom Left): Snacks / Chips
        # Simulated misplaced item: an apple or soda bottle placed here!
        chips_count = 5
        for i in range(chips_count):
            cx = 40 + (i * 48)
            cy = height - 130
            cv2.rectangle(frame, (cx, cy), (cx + 36, height - 20), (10, 140, 220), -1) # Yellow chips bag
            cv2.putText(frame, "CHIPS", (cx + 3, cy + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.28, (10, 10, 10), 1)

        # Introduce a misplaced bottle in chips section if sin wave peak
        if math.sin(t * 0.7) > 0.2:
            mx = 40 + (chips_count * 48)
            my = height - 120
            cv2.rectangle(frame, (mx, my), (mx + 30, height - 20), (30, 30, 210), -1) # Misplaced Coke!
            cv2.putText(frame, "COLA", (mx + 2, my + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 255, 255), 1)

        # Section 4 (Bottom Right): Personal Care / Bottles
        water_count = 4
        for i in range(water_count):
            wx = col_split + 45 + (i * 45)
            wy = height - 135
            cv2.rectangle(frame, (wx, wy), (wx + 28, height - 20), (220, 160, 40), -1) # Blue water bottle
            cv2.putText(frame, "WATER", (wx + 1, wy + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 255, 255), 1)

        return frame

    def get_frame(self, camera_source: str) -> np.ndarray:
        """
        Reads from actual camera if numeric/path, else falls back to synthetic frame generator.
        """
        if camera_source.isdigit():
            idx = int(camera_source)
            if idx not in self.active_sources:
                cap = cv2.VideoCapture(idx)
                if not cap.isOpened():
                    logger.warning(f"Webcam index {idx} not available. Using synthetic shelf simulator.")
                    self.active_sources[idx] = None
                else:
                    self.active_sources[idx] = cap
            
            cap = self.active_sources[idx]
            if cap is not None and cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    return frame

        # Fallback to synthetic generator
        return self.generate_synthetic_shelf_frame()

    def stream_mjpeg(self, shelf_id: str) -> Generator[bytes, None, None]:
        """
        Yields MJPEG multipart frame stream with live bounding boxes and ROI overlays.
        """
        db = SessionLocal()
        try:
            shelf = db.query(Shelf).filter(Shelf.id == shelf_id).first()
            if not shelf:
                return

            camera_source = shelf.camera_source or "0"
            frame_counter = 0

            while True:
                frame = self.get_frame(camera_source)
                frame_counter += 1

                # Every 3 frames run detection & analysis
                detections = cv_engine.detect_products(frame)
                
                # If synthetic frame without YOLO detections, generate simulated detections
                if not detections:
                    detections = self._generate_simulated_detections(frame)

                sections_status, enriched_dets = anomaly_detector.analyze_shelf(
                    shelf=shelf,
                    detections=detections,
                    db=db if (frame_counter % 30 == 0) else None,
                    create_alerts=(frame_counter % 30 == 0)
                )

                # Render overlay on frame
                annotated_frame = cv_engine.draw_shelf_overlay(
                    frame=frame,
                    sections=sections_status,
                    detections=enriched_dets
                )

                ret, buffer = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if not ret:
                    continue

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                time.sleep(0.04) # ~25 FPS
        finally:
            db.close()

    def _generate_simulated_detections(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Generates simulated bounding boxes matching the synthetic shelf visual.
        """
        h, w = frame.shape[:2]
        t = self.simulation_step * 0.05
        detections = []

        # Sec 1 (Top Left): 0.0 to 0.5 x, 0.0 to 0.5 y -> Bottles
        coke_count = max(2, int(6 + 2 * math.sin(t * 0.8)))
        for i in range(coke_count):
            bx = 35 + (i * 42)
            by = (h // 2) - 120
            detections.append({
                "class_name": "bottle",
                "category": "Beverages",
                "confidence": 0.94,
                "bbox": [bx, by, bx + 30, (h // 2) - 10],
                "center": [round((bx + 15) / w, 4), round(((h // 2) - 65) / h, 4)],
                "normalized_bbox": [round(bx / w, 4), round(by / h, 4), round((bx + 30) / w, 4), round(((h // 2) - 10) / h, 4)]
            })

        # Sec 2 (Top Right): 0.5 to 1.0 x, 0.0 to 0.5 y -> Apples
        apple_phase = math.sin(t * 0.5)
        apple_count = 0 if apple_phase < -0.4 else int(4 + 2 * math.cos(t * 0.5))
        for i in range(apple_count):
            ax = (w // 2) + 40 + (i * 50)
            ay = (h // 2) - 70
            detections.append({
                "class_name": "apple",
                "category": "Produce",
                "confidence": 0.91,
                "bbox": [ax, ay - 20, ax + 36, ay + 20],
                "center": [round((ax + 18) / w, 4), round(ay / h, 4)],
                "normalized_bbox": [round(ax / w, 4), round((ay - 20) / h, 4), round((ax + 36) / w, 4), round((ay + 20) / h, 4)]
            })

        # Sec 3 (Bottom Left): 0.0 to 0.5 x, 0.5 to 1.0 y -> Chips
        chips_count = 5
        for i in range(chips_count):
            cx = 40 + (i * 48)
            cy = h - 130
            detections.append({
                "class_name": "sandwich", # mapping to snacks
                "category": "Snacks",
                "confidence": 0.88,
                "bbox": [cx, cy, cx + 36, h - 20],
                "center": [round((cx + 18) / w, 4), round((cy + 55) / h, 4)],
                "normalized_bbox": [round(cx / w, 4), round(cy / h, 4), round((cx + 36) / w, 4), round((h - 20) / h, 4)]
            })

        # Misplaced item in chips section
        if math.sin(t * 0.7) > 0.2:
            mx = 40 + (chips_count * 48)
            my = h - 120
            detections.append({
                "class_name": "bottle",
                "category": "Beverages", # Expecting Snacks!
                "confidence": 0.95,
                "bbox": [mx, my, mx + 30, h - 20],
                "center": [round((mx + 15) / w, 4), round((my + 50) / h, 4)],
                "normalized_bbox": [round(mx / w, 4), round(my / h, 4), round((mx + 30) / w, 4), round((h - 20) / h, 4)]
            })

        # Sec 4 (Bottom Right): 0.5 to 1.0 x, 0.5 to 1.0 y -> Water bottles
        water_count = 4
        for i in range(water_count):
            wx = (w // 2) + 45 + (i * 45)
            wy = h - 135
            detections.append({
                "class_name": "bottle",
                "category": "Beverages",
                "confidence": 0.96,
                "bbox": [wx, wy, wx + 28, h - 20],
                "center": [round((wx + 14) / w, 4), round((wy + 55) / h, 4)],
                "normalized_bbox": [round(wx / w, 4), round(wy / h, 4), round((wx + 28) / w, 4), round((h - 20) / h, 4)]
            })

        return detections

video_streamer = VideoStreamer()
