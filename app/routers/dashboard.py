from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.database import get_db
from app.models import Alarm, OFCSegment, SegmentStatus, WorkOrder
from app.schemas import ReportSummaryOut

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=ReportSummaryOut)
def get_dashboard_stats(db: Session = Depends(get_db)):
    segment_count = db.query(OFCSegment).count()
    active_alarms = db.query(Alarm).filter(Alarm.acknowledged == False).count()
    open_work_orders = db.query(WorkOrder).filter(WorkOrder.status != "closed").count()
    
    avg_availability = db.query(func.avg(OFCSegment.availability_30d_pct)).scalar()
    
    return ReportSummaryOut(
        segment_count=segment_count,
        active_alarms=active_alarms,
        open_work_orders=open_work_orders,
        avg_availability_30d_pct=float(avg_availability) if avg_availability else 100.0,
        mean_time_to_repair_minutes=45.5 # Mock metric for now
    )
