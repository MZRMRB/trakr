from pydantic import BaseModel, validator, Field, constr
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum

class WarnType(str, Enum):
    """Enum for alarm warning types"""
    GEOFENCE = "geofence"
    LOW_BATTERY = "low_battery"
    UNEXPECTED_MOVEMENT = "unexpected_movement"

class Alarm(BaseModel):
    """Schema for alarm response"""
    sn: int
    organization: str
    imei: str
    tracking_object: str
    warn_type: str
    time: datetime
    check_the_time: Optional[datetime]
    check_time: Optional[str]
    is_handled: Optional[bool] = False
    handled_by: Optional[str] = None
    handled_at: Optional[datetime] = None
    handle_reason: Optional[str] = None

class AlarmFilter(BaseModel):
    """Schema for alarm filtering and pagination"""
    organization: str
    warn_type: Optional[WarnType] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

    @validator('end_time')
    def validate_time_range(cls, v, values):
        if v and 'start_time' in values and values['start_time']:
            if v <= values['start_time']:
                raise ValueError('End time must be after start time')
        return v

class AlarmExportRequest(BaseModel):
    """Schema for alarm export request"""
    organization: str
    warn_type: Optional[WarnType] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    format: Literal["csv", "xlsx"] = "csv"

    @validator('end_time')
    def validate_time_range(cls, v, values):
        if v and 'start_time' in values and values['start_time']:
            if v <= values['start_time']:
                raise ValueError('End time must be after start time')
        return v

class AlarmHandleRequest(BaseModel):
    """Schema for alarm handle request"""
    alarm_ids: List[int]
    reason: Optional[constr(max_length=500)] = None

    @validator('alarm_ids')
    def validate_alarm_ids(cls, v):
        if not v:
            raise ValueError('At least one alarm ID must be provided')
        if len(v) > 100:
            raise ValueError('Cannot handle more than 100 alarms at once')
        if len(set(v)) != len(v):
            raise ValueError('Duplicate alarm IDs are not allowed')
        return v

    @validator('reason')
    def validate_reason(cls, v):
        if v is not None and len(v.strip()) > 500:
            raise ValueError('Handle reason cannot exceed 500 characters')
        return v.strip() if v else v

class AlarmListResponse(BaseModel):
    """Schema for alarm list response with pagination info"""
    alarms: List[Alarm]
    pagination: dict

class AlarmExportResponse(BaseModel):
    """Schema for alarm export response"""
    message: str
    filename: str
    record_count: int
    export_time: datetime

class AlarmHandleResponse(BaseModel):
    """Schema for alarm handle response"""
    message: str
    handled_count: int
    failed_count: int
    failed_alarm_ids: List[int]
    handle_time: datetime

class Organization(BaseModel):
    """Schema for organization response"""
    id: int
    organization_name: str
    title: Optional[str] 