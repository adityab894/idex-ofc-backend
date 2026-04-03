from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import OFCSegment
from app.schemas import SegmentOut

router = APIRouter(prefix="/api/segments", tags=["Segments"])


@router.get("", response_model=list[SegmentOut])
def list_segments(db: Session = Depends(get_db)):
    segments = db.query(OFCSegment).all()
    return segments


@router.get("/{segment_id}", response_model=SegmentOut)
def get_segment(segment_id: str, db: Session = Depends(get_db)):
    segment = db.query(OFCSegment).filter(OFCSegment.id == segment_id).first()
    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found")
    return segment
