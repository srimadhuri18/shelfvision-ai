from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any, List
from ..database import get_db
from ..models import Shelf, Alert, HealthLog

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/overview")
def get_store_overview(db: Session = Depends(get_db)):
    shelves = db.query(Shelf).all()
    total_shelves = len(shelves)
    
    active_alerts = db.query(Alert).filter(Alert.is_acknowledged == False).all()
    
    empty_alerts = sum(1 for a in active_alerts if a.alert_type == "EMPTY")
    low_stock_alerts = sum(1 for a in active_alerts if a.alert_type == "LOW_STOCK")
    misplaced_alerts = sum(1 for a in active_alerts if a.alert_type == "MISPLACED")

    return {
        "total_shelves": total_shelves,
        "critical_issues": empty_alerts,
        "warning_issues": low_stock_alerts + misplaced_alerts,
        "empty_shelves_count": empty_alerts,
        "low_stock_shelves_count": low_stock_alerts,
        "misplacement_alerts_count": misplaced_alerts,
        "average_health_score": 88.5 if total_shelves > 0 else 100.0,
        "total_unacknowledged_alerts": len(active_alerts)
    }

@router.get("/health-trends")
def get_health_trends():
    """Returns simulated hourly trend data for visual charts."""
    now = datetime.utcnow()
    points = []
    base_scores = [94, 91, 88, 82, 85, 90, 89, 93, 86, 92]
    
    for i, score in enumerate(base_scores):
        t = now - timedelta(hours=(len(base_scores) - i))
        points.append({
            "timestamp": t.strftime("%H:%M"),
            "health_score": score,
            "availability": round(score * 0.96, 1),
            "stock_level": round(score * 0.92, 1)
        })
    return points
