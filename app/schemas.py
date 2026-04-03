from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .models import SegmentStatus, WorkOrderStatus


class GeoJSONLineString(BaseModel):
    type: str = "LineString"
    coordinates: list[list[float]]


class SegmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    base_code: str
    route_geojson: dict[str, Any]
    length_km: float
    status: SegmentStatus
    availability_30d_pct: float


class AlarmOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    segment_id: str
    alarm_type: str
    lat: float
    lng: float
    message: str
    severity: str
    created_at: datetime
    acknowledged: bool


class AlarmAckBody(BaseModel):
    acknowledged: bool = True


class SimulateCutIn(BaseModel):
    segment_id: str
    lat: float | None = None
    lng: float | None = None
    message: str | None = Field(
        default=None,
        description="Optional override for alarm text shown to operators.",
    )


class WorkOrderCreate(BaseModel):
    alarm_id: str | None = None
    segment_id: str
    title: str
    assignee: str = "Repair Team Alpha"
    instructions: str = ""


class WorkOrderPatch(BaseModel):
    status: WorkOrderStatus | None = None
    assignee: str | None = None
    instructions: str | None = None


class WorkOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    alarm_id: str | None
    segment_id: str
    title: str
    assignee: str
    status: WorkOrderStatus
    instructions: str
    created_at: datetime
    updated_at: datetime


class ReportSummaryOut(BaseModel):
    segment_count: int
    active_alarms: int
    open_work_orders: int
    avg_availability_30d_pct: float | None
    mean_time_to_repair_minutes: float | None
