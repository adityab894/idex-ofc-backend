from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import OFCSegment, SegmentStatus, WorkOrder, WorkOrderStatus
from app.schemas import WorkOrderCreate, WorkOrderOut, WorkOrderPatch
from app.websocket_manager import manager

router = APIRouter(prefix="/api/work_orders", tags=["Work Orders"])

@router.get("", response_model=list[WorkOrderOut])
def list_work_orders(db: Session = Depends(get_db)):
    return db.query(WorkOrder).order_by(WorkOrder.created_at.desc()).all()

@router.post("", response_model=WorkOrderOut)
def create_work_order(payload: WorkOrderCreate, db: Session = Depends(get_db)):
    wo = WorkOrder(
        alarm_id=payload.alarm_id,
        segment_id=payload.segment_id,
        title=payload.title,
        assignee=payload.assignee,
        instructions=payload.instructions,
    )
    db.add(wo)
    db.commit()
    db.refresh(wo)
    return wo

@router.patch("/{wo_id}", response_model=WorkOrderOut)
async def update_work_order(wo_id: str, payload: WorkOrderPatch, db: Session = Depends(get_db)):
    wo = db.query(WorkOrder).filter(WorkOrder.id == wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work Order not found")

    segment_restored = False

    if payload.status is not None:
        wo.status = payload.status
        # Logic to "heal" the cable once work order is closed
        if payload.status == WorkOrderStatus.closed:
            segment = db.query(OFCSegment).filter(OFCSegment.id == wo.segment_id).first()
            if segment and segment.status == SegmentStatus.cut:
                segment.status = SegmentStatus.healthy
                segment_restored = True

    if payload.assignee is not None:
        wo.assignee = payload.assignee
    if payload.instructions is not None:
        wo.instructions = payload.instructions

    db.commit()
    db.refresh(wo)

    if segment_restored:
        await manager.broadcast({
            "type": "FIBER_RESTORED",
            "data": {
                "segment_id": wo.segment_id,
                "message": f"Repair absolute. Fiber restored."
            }
        })

    return wo
