from pydantic import BaseModel, validator
from typing import Optional, List
import re

class TrackingObject(BaseModel):
    """Schema for tracking object response"""
    sn: int
    organization: str
    name: str
    role: Optional[str]
    mac: Optional[str]

class TrackingObjectCreate(BaseModel):
    """Schema for creating a new tracking object"""
    organization: str
    name: str
    role: Optional[str] = None
    mac: Optional[str] = None

    @validator('mac')
    def validate_mac_address(cls, v):
        if v is not None:
            # MAC address regex pattern (supports various formats)
            mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
            if not mac_pattern.match(v):
                raise ValueError('Invalid MAC address format. Use format: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX')
        return v

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        if len(v.strip()) > 100:
            raise ValueError('Name cannot exceed 100 characters')
        return v.strip()

class TrackingObjectUpdate(BaseModel):
    """Schema for updating a tracking object"""
    name: Optional[str] = None
    role: Optional[str] = None
    mac: Optional[str] = None

    @validator('mac')
    def validate_mac_address(cls, v):
        if v is not None:
            mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
            if not mac_pattern.match(v):
                raise ValueError('Invalid MAC address format. Use format: XX:XX:XX:XX:XX:XX or XX-XX-XX-XX-XX-XX')
        return v

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Name cannot be empty')
            if len(v.strip()) > 100:
                raise ValueError('Name cannot exceed 100 characters')
            return v.strip()
        return v

class Organization(BaseModel):
    """Schema for organization response"""
    id: int
    organization_name: str
    title: Optional[str]

class ImportResponse(BaseModel):
    """Schema for import operation response"""
    message: str
    imported_count: int
    errors: List[str] = []

class PhotoUploadResponse(BaseModel):
    """Schema for photo upload response"""
    message: str
    uploaded_count: int
    file_names: List[str] = [] 