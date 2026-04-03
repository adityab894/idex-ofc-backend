from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SegmentStatus(str, enum.Enum):
    healthy = "healthy"
    degraded = "degraded"
    cut = "cut"


class WorkOrderStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class OFCSegment(Base):
    __tablename__ = "ofc_segments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    base_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    # GeoJSON LineString geometry: {"type":"LineString","coordinates":[[lng,lat],...]}
    route_geojson: Mapped[dict] = mapped_column(JSON, nullable=False)
    length_km: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[SegmentStatus] = mapped_column(
        Enum(SegmentStatus, native_enum=False, length=32),
        nullable=False,
        default=SegmentStatus.healthy,
    )
    availability_30d_pct: Mapped[float] = mapped_column(Float, nullable=False, default=99.95)

    alarms: Mapped[list["Alarm"]] = relationship("Alarm", back_populates="segment")
    work_orders: Mapped[list["WorkOrder"]] = relationship("WorkOrder", back_populates="segment")


class Alarm(Base):
    __tablename__ = "alarms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_id: Mapped[str] = mapped_column(String(36), ForeignKey("ofc_segments.id"), nullable=False)
    alarm_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="critical")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    acknowledged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    segment: Mapped["OFCSegment"] = relationship("OFCSegment", back_populates="alarms")
    work_orders: Mapped[list["WorkOrder"]] = relationship("WorkOrder", back_populates="alarm")


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alarm_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("alarms.id"), nullable=True)
    segment_id: Mapped[str] = mapped_column(String(36), ForeignKey("ofc_segments.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    assignee: Mapped[str] = mapped_column(String(255), nullable=False, default="Repair Team Alpha")
    status: Mapped[WorkOrderStatus] = mapped_column(
        Enum(WorkOrderStatus), nullable=False, default=WorkOrderStatus.open
    )
    instructions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )

    segment: Mapped[OFCSegment] = relationship("OFCSegment", back_populates="work_orders")
    alarm: Mapped[Alarm | None] = relationship("Alarm", back_populates="work_orders")
