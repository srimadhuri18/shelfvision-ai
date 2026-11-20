from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# --- Product Schemas ---
class ProductBase(BaseModel):
    sku: str
    name: str
    category: str
    yolo_class: str
    price: float = 0.0

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: str
    created_at: datetime
    class Config:
        from_attributes = True


# --- Section Schemas ---
class SectionBase(BaseModel):
    row_index: int
    col_index: int
    label: str
    expected_product_name: str
    expected_category: str
    capacity: int = 10
    low_stock_threshold: int = 3
    roi_x1: float = 0.0
    roi_y1: float = 0.0
    roi_x2: float = 1.0
    roi_y2: float = 1.0

class SectionCreate(SectionBase):
    pass

class SectionUpdateROI(BaseModel):
    roi_x1: float
    roi_y1: float
    roi_x2: float
    roi_y2: float

class SectionResponse(SectionBase):
    id: str
    shelf_id: str
    class Config:
        from_attributes = True


# --- Shelf Schemas ---
class ShelfBase(BaseModel):
    name: str
    code: str
    camera_source: str = "0"
    rows: int = 2
    cols: int = 2

class ShelfCreate(ShelfBase):
    sections: Optional[List[SectionCreate]] = None

class ShelfResponse(ShelfBase):
    id: str
    created_at: datetime
    class Config:
        from_attributes = True

class ShelfDetailResponse(ShelfResponse):
    sections: List[SectionResponse] = []


# --- Alert Schemas ---
class AlertResponse(BaseModel):
    id: str
    shelf_id: str
    section_id: Optional[str]
    section_label: Optional[str]
    alert_type: str # EMPTY, LOW_STOCK, MISPLACED
    severity: str # CRITICAL, WARNING, INFO
    message: str
    is_acknowledged: bool
    created_at: datetime
    class Config:
        from_attributes = True

class AlertAckRequest(BaseModel):
    is_acknowledged: bool = True


# --- Health & Analytics Schemas ---
class HealthScoreBreakdown(BaseModel):
    availability_pct: float
    placement_accuracy_pct: float
    stock_level_pct: float
    health_score: float # 0 - 100
    status_label: str # "EXCELLENT", "GOOD", "WARNING", "CRITICAL"

class ShelfHealthResponse(BaseModel):
    shelf_id: str
    shelf_name: str
    metrics: HealthScoreBreakdown
    total_sections: int
    empty_sections: int
    low_stock_sections: int
    misplaced_items_count: int
    active_alerts_count: int

class HealthHistoryPoint(BaseModel):
    timestamp: datetime
    health_score: float
    availability_pct: float
    stock_pct: float

# --- CV Detection Live Schemas ---
class DetectedObject(BaseModel):
    class_name: str
    confidence: float
    bbox: List[int] # [x1, y1, x2, y2]
    center: List[float] # [cx, cy] normalized
    section_id: Optional[str] = None
    is_misplaced: bool = False

class SectionLiveStatus(BaseModel):
    section_id: str
    label: str
    expected_product: str
    expected_category: str
    detected_count: int
    capacity: int
    status: str # "NORMAL", "LOW_STOCK", "EMPTY", "MISPLACED"
    misplaced_count: int
    occupancy_ratio: float

class LiveShelfAnalysis(BaseModel):
    shelf_id: str
    timestamp: datetime
    total_detected: int
    health_score: float
    sections: List[SectionLiveStatus]
    detections: List[DetectedObject]
