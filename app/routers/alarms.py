from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alarm, OFCSegment, SegmentStatus, WorkOrder
from app.schemas import AlarmAckBody, AlarmOut, SimulateCutIn

router = APIRouter(prefix="/api/alarms", tags=["Alarms"])


@router.get("", response_model=list[AlarmOut])
def list_alarms(db: Session = Depends(get_db), active_only: bool = False):
    query = db.query(Alarm)
    if active_only:
        query = query.filter(Alarm.acknowledged == False)
    alarms = query.order_by(Alarm.created_at.desc()).all()
    return alarms


@router.patch("/{alarm_id}/acknowledge", response_model=AlarmOut)
def acknowledge_alarm(alarm_id: str, body: AlarmAckBody, db: Session = Depends(get_db)):
    alarm = db.query(Alarm).filter(Alarm.id == alarm_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    
    alarm.acknowledged = body.acknowledged
    db.commit()
    db.refresh(alarm)
    return alarm


@router.post("/simulate", response_model=AlarmOut)
def simulate_cut(payload: SimulateCutIn, db: Session = Depends(get_db)):
    segment = db.query(OFCSegment).filter(OFCSegment.id == payload.segment_id).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")

    # Update segment status to 'cut'
    segment.status = SegmentStatus.cut

    # If coordinates are missing, pick the first coordinate of the segment as mock
    lat = payload.lat
    lng = payload.lng
    if lat is None or lng is None:
        try:
            coords = segment.route_geojson.get("coordinates", [])
            lng, lat = coords[0][0], coords[0][1]
        except (IndexError, TypeError):
            # Fallback mock coordinates anywhere in India
            lat, lng = 28.6139, 77.2090

    # Create an alarm
    msg = payload.message or f"OFC Cut detected on link: {segment.name}"
    alarm = Alarm(
        segment_id=segment.id,
        alarm_type="FIBER_CUT",
        lat=lat,
        lng=lng,
        message=msg,
        severity="critical",
    )
    db.add(alarm)
    db.commit()
    db.refresh(alarm)
    
    # Optionally, we might auto-create a WorkOrder in real system, but let's keep it separate for now
    # or expose a specific real-time websocket alert here later.
    return alarm
