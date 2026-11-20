from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
import asyncio
import cv2
from datetime import datetime
import json
import logging
from ..database import get_db, SessionLocal
from ..models import Shelf
from ..services.video_streamer import video_streamer
from ..services.cv_engine import cv_engine
from ..services.anomaly_detector import anomaly_detector
from ..services.health_calculator import health_calculator

router = APIRouter(prefix="/stream", tags=["Streaming"])
logger = logging.getLogger(__name__)

@router.get("/video_feed/{shelf_id}")
def video_feed(shelf_id: str):
    """
    HTTP MJPEG multipart video feed. Renderable directly inside standard <img src="..."> tags.
    """
    return StreamingResponse(
        video_streamer.stream_mjpeg(shelf_id),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.get("/snapshot/{shelf_id}")
def get_snapshot(shelf_id: str, db: Session = Depends(get_db)):
    shelf = db.query(Shelf).filter(Shelf.id == shelf_id).first()
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")

    frame = video_streamer.get_frame(shelf.camera_source or "0")
    detections = cv_engine.detect_products(frame)
    if not detections:
        detections = video_streamer._generate_simulated_detections(frame)

    sections_status, enriched_dets = anomaly_detector.analyze_shelf(
        shelf=shelf,
        detections=detections,
        db=db,
        create_alerts=False
    )

    annotated = cv_engine.draw_shelf_overlay(frame, sections_status, enriched_dets)
    ret, buffer = cv2.imencode('.jpg', annotated)
    if not ret:
        raise HTTPException(status_code=500, detail="Failed to encode frame")

    return Response(content=buffer.tobytes(), media_type="image/jpeg")

@router.websocket("/ws/{shelf_id}")
async def websocket_shelf_live(websocket: WebSocket, shelf_id: str):
    """
    High-frequency WebSocket channel pushing live detections, section status, and health score.
    """
    await websocket.accept()
    db = SessionLocal()
    try:
        shelf = db.query(Shelf).filter(Shelf.id == shelf_id).first()
        if not shelf:
            await websocket.send_json({"error": "Shelf not found"})
            await websocket.close()
            return

        while True:
            frame = video_streamer.get_frame(shelf.camera_source or "0")
            detections = cv_engine.detect_products(frame)
            if not detections:
                detections = video_streamer._generate_simulated_detections(frame)

            sections_status, enriched_dets = anomaly_detector.analyze_shelf(
                shelf=shelf,
                detections=detections,
                db=db,
                create_alerts=False
            )

            metrics = health_calculator.calculate_score(sections_status)

            payload = {
                "shelf_id": shelf.id,
                "timestamp": datetime.utcnow().isoformat(),
                "health_score": metrics["health_score"],
                "metrics": metrics,
                "sections": sections_status,
                "detections": enriched_dets,
                "total_detected": len(enriched_dets)
            }

            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(0.4) # Push every 400ms
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for shelf {shelf_id}")
    except Exception as e:
        logger.error(f"WebSocket streaming error: {e}")
    finally:
        db.close()
