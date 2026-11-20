from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Shelf, Section, Alert
from ..schemas import ShelfResponse, ShelfDetailResponse, ShelfCreate, SectionUpdateROI, ShelfHealthResponse
from ..services.health_calculator import health_calculator
from ..services.anomaly_detector import anomaly_detector
from ..services.cv_engine import cv_engine
from ..services.video_streamer import video_streamer

router = APIRouter(prefix="/shelves", tags=["Shelves"])

@router.get("", response_model=List[ShelfResponse])
def get_all_shelves(db: Session = Depends(get_db)):
    shelves = db.query(Shelf).all()
    if not shelves:
        # Seed default demonstration shelf if empty
        seed_default_shelf(db)
        shelves = db.query(Shelf).all()
    return shelves

@router.get("/{shelf_id}", response_model=ShelfDetailResponse)
def get_shelf_details(shelf_id: str, db: Session = Depends(get_db)):
    shelf = db.query(Shelf).filter(Shelf.id == shelf_id).first()
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")
    return shelf

@router.post("", response_model=ShelfDetailResponse)
def create_shelf(payload: ShelfCreate, db: Session = Depends(get_db)):
    shelf = Shelf(
        name=payload.name,
        code=payload.code,
        camera_source=payload.camera_source,
        rows=payload.rows,
        cols=payload.cols
    )
    db.add(shelf)
    db.flush()

    if payload.sections:
        for s in payload.sections:
            sec = Section(
                shelf_id=shelf.id,
                row_index=s.row_index,
                col_index=s.col_index,
                label=s.label,
                expected_product_name=s.expected_product_name,
                expected_category=s.expected_category,
                capacity=s.capacity,
                low_stock_threshold=s.low_stock_threshold,
                roi_x1=s.roi_x1,
                roi_y1=s.roi_y1,
                roi_x2=s.roi_x2,
                roi_y2=s.roi_y2
            )
            db.add(sec)
    db.commit()
    db.refresh(shelf)
    return shelf

@router.put("/sections/{section_id}/roi")
def update_section_roi(section_id: str, payload: SectionUpdateROI, db: Session = Depends(get_db)):
    section = db.query(Section).filter(Section.id == section_id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    section.roi_x1 = payload.roi_x1
    section.roi_y1 = payload.roi_y1
    section.roi_x2 = payload.roi_x2
    section.roi_y2 = payload.roi_y2
    db.commit()
    return {"message": "ROI updated successfully", "section_id": section_id}

@router.get("/{shelf_id}/health", response_model=ShelfHealthResponse)
def get_shelf_health(shelf_id: str, db: Session = Depends(get_db)):
    shelf = db.query(Shelf).filter(Shelf.id == shelf_id).first()
    if not shelf:
        raise HTTPException(status_code=404, detail="Shelf not found")

    # Sample a live frame and analyze
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
    active_alerts = db.query(Alert).filter(Alert.shelf_id == shelf.id, Alert.is_acknowledged == False).count()

    empty_count = sum(1 for s in sections_status if s["status"] == "EMPTY")
    low_stock_count = sum(1 for s in sections_status if s["status"] == "LOW_STOCK")
    misplaced_count = sum(s["misplaced_count"] for s in sections_status)

    return {
        "shelf_id": shelf.id,
        "shelf_name": shelf.name,
        "metrics": metrics,
        "total_sections": len(sections_status),
        "empty_sections": empty_count,
        "low_stock_sections": low_stock_count,
        "misplaced_items_count": misplaced_count,
        "active_alerts_count": active_alerts
    }

def seed_default_shelf(db: Session):
    """Pre-seeds default standard 2x2 retail shelf for instant plug-and-play operation."""
    default_shelf = Shelf(
        name="Main Beverage & Grocery Shelf A1",
        code="SHELF-A1",
        camera_source="0",
        rows=2,
        cols=2
    )
    db.add(default_shelf)
    db.flush()

    sections_data = [
        {
            "row": 0, "col": 0, "label": "Tier 1 - Slot 1 (Soft Drinks)",
            "product": "Coca-Cola Can", "cat": "Beverages", "cap": 8, "low": 3,
            "x1": 0.0, "y1": 0.0, "x2": 0.5, "y2": 0.5
        },
        {
            "row": 0, "col": 1, "label": "Tier 1 - Slot 2 (Fresh Fruits)",
            "product": "Fresh Green Apples", "cat": "Produce", "cap": 8, "low": 2,
            "x1": 0.5, "y1": 0.0, "x2": 1.0, "y2": 0.5
        },
        {
            "row": 1, "col": 0, "label": "Tier 2 - Slot 1 (Packaged Snacks)",
            "product": "Potato Chips Bags", "cat": "Snacks", "cap": 10, "low": 4,
            "x1": 0.0, "y1": 0.5, "x2": 0.5, "y2": 1.0
        },
        {
            "row": 1, "col": 1, "label": "Tier 2 - Slot 2 (Mineral Water)",
            "product": "Spring Water Bottle", "cat": "Beverages", "cap": 8, "low": 3,
            "x1": 0.5, "y1": 0.5, "x2": 1.0, "y2": 1.0
        }
    ]

    for s in sections_data:
        sec = Section(
            shelf_id=default_shelf.id,
            row_index=s["row"],
            col_index=s["col"],
            label=s["label"],
            expected_product_name=s["product"],
            expected_category=s["cat"],
            capacity=s["cap"],
            low_stock_threshold=s["low"],
            roi_x1=s["x1"],
            roi_y1=s["y1"],
            roi_x2=s["x2"],
            roi_y2=s["y2"]
        )
        db.add(sec)
    db.commit()
