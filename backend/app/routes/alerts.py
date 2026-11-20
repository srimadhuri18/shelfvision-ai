from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Alert
from ..schemas import AlertResponse, AlertAckRequest

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertResponse])
def get_alerts(
    shelf_id: Optional[str] = None,
    unacknowledged_only: bool = Query(True),
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Alert)
    if shelf_id:
        query = query.filter(Alert.shelf_id == shelf_id)
    if unacknowledged_only:
        query = query.filter(Alert.is_acknowledged == False)
    
    return query.order_by(Alert.created_at.desc()).limit(limit).all()

@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: str,
    payload: AlertAckRequest = AlertAckRequest(),
    db: Session = Depends(get_db)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_acknowledged = payload.is_acknowledged
    db.commit()
    db.refresh(alert)
    return alert

@router.post("/acknowledge-all")
def acknowledge_all_alerts(shelf_id: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Alert).filter(Alert.is_acknowledged == False)
    if shelf_id:
        query = query.filter(Alert.shelf_id == shelf_id)
    
    updated_count = query.update({"is_acknowledged": True})
    db.commit()
    return {"message": f"Acknowledged {updated_count} alerts"}
