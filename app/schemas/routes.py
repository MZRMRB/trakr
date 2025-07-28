from pydantic import BaseModel, validator, Field
from typing import Optional, List, Literal
from datetime import datetime

class Route(BaseModel):
    """Schema for route response"""
    sn: int
    terminal_id: str
    tracking_object: str
    tracking_time: datetime
    gps_x: Optional[float]
    gps_y: Optional[float]

class RouteFilter(BaseModel):
    """Schema for route filtering and pagination"""
    organization: str
    start_time: datetime
    end_time: datetime
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

    @validator('end_time')
    def validate_time_range(cls, v, values):
        if v and 'start_time' in values and values['start_time']:
            if v <= values['start_time']:
                raise ValueError('End time must be after start time')
        return v

class RouteExportRequest(BaseModel):
    """Schema for route export request"""
    organization: str
    start_time: datetime
    end_time: datetime
    format: Literal["csv", "xlsx"] = "csv"

    @validator('end_time')
    def validate_time_range(cls, v, values):
        if v and 'start_time' in values and values['start_time']:
            if v <= values['start_time']:
                raise ValueError('End time must be after start time')
        return v

class RouteListResponse(BaseModel):
    """Schema for route list response with pagination info"""
    routes: List[Route]
    pagination: dict
    message: Optional[str] = None

class RouteExportResponse(BaseModel):
    """Schema for route export response"""
    message: str
    filename: str
    record_count: int
    export_time: datetime

class Organization(BaseModel):
    """Schema for organization response"""
    id: int
    organization_name: str
    title: Optional[str] 