import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    PROJECT_NAME: str = "ShelfVision AI"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'data' / 'shelfvision.db'}")
    
    # Computer Vision
    YOLO_MODEL_PATH: str = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
    DEFAULT_CAMERA_INDEX: int = int(os.getenv("CAMERA_INDEX", "0"))
    DEFAULT_CONFIDENCE: float = 0.40
    
    # Anomaly Thresholds
    EMPTY_THRESHOLD_RATIO: float = 0.15
    LOW_STOCK_RATIO: float = 0.45
    
    # Shelf Health Score Weights (Sum = 100)
    WEIGHT_AVAILABILITY: float = 40.0
    WEIGHT_PLACEMENT: float = 35.0
    WEIGHT_STOCK_LEVEL: float = 25.0

settings = Settings()
