from pydantic import BaseModel, validator, conint, constr
from typing import Optional, List, Literal
from datetime import datetime
import re

class Tag(BaseModel):
    """Schema for tag response"""
    sn: int
    organization: str
    imei: str
    signal: Optional[int]
    power: Optional[int]
    charge_status: Optional[str]
    tracking_update_time: Optional[datetime]
    data_update_time: Optional[datetime]
    bluetooth_mark: Optional[str]

class TagFilter(BaseModel):
    """Schema for tag filtering and pagination"""
    organization: Optional[str] = None
    model: Optional[str] = None
    page: conint(ge=1) = 1
    page_size: conint(ge=1, le=100) = 10

    @validator('model')
    def validate_model(cls, v):
        if v is not None and len(v.strip()) > 100:
            raise ValueError('Model filter cannot exceed 100 characters')
        return v.strip() if v else v

class TagExportRequest(BaseModel):
    """Schema for tag export request"""
    organization: Optional[str] = None
    model: Optional[str] = None
    format: Literal["csv", "xlsx"] = "csv"

    @validator('model')
    def validate_model(cls, v):
        if v is not None and len(v.strip()) > 100:
            raise ValueError('Model filter cannot exceed 100 characters')
        return v.strip() if v else v

class TagTransferRequest(BaseModel):
    """Schema for tag transfer request"""
    tag_ids: List[int]
    new_organization_id: int
    reason: Optional[constr(max_length=500)] = None

    @validator('tag_ids')
    def validate_tag_ids(cls, v):
        if not v:
            raise ValueError('At least one tag ID must be provided')
        if len(v) > 100:
            raise ValueError('Cannot transfer more than 100 tags at once')
        return v

    @validator('reason')
    def validate_reason(cls, v):
        if v is not None and len(v.strip()) > 500:
            raise ValueError('Transfer reason cannot exceed 500 characters')
        return v.strip() if v else v

class TagListResponse(BaseModel):
    """Schema for tag list response with pagination info"""
    tags: List[Tag]
    total_count: int
    page: int
    page_size: int

class TagExportResponse(BaseModel):
    """Schema for tag export response"""
    message: str
    filename: str
    record_count: int
    export_time: datetime

class TagTransferResponse(BaseModel):
    """Schema for tag transfer response"""
    message: str
    transferred_count: int
    failed_count: int
    failed_tag_ids: List[int]
    transfer_time: datetime

class Organization(BaseModel):
    """Schema for organization response"""
    id: int
    organization_name: str
    title: Optional[str] 