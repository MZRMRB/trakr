from pydantic import BaseModel, validator, constr
from typing import Optional, List
from datetime import datetime
import re

class Organization(BaseModel):
    """Schema for organization response"""
    id: int
    organization_name: str
    title: str
    product_type: Optional[str]
    create_time: Optional[datetime]

class OrganizationCreate(BaseModel):
    """Schema for creating a new organization"""
    organization_name: str
    title: str
    product_type: Optional[str] = None

    @validator('organization_name')
    def validate_organization_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Organization name cannot be empty')
        if len(v.strip()) < 3:
            raise ValueError('Organization name must be at least 3 characters')
        if len(v.strip()) > 50:
            raise ValueError('Organization name cannot exceed 50 characters')
        # Only lowercase letters, numbers, underscore, hyphen
        if not re.match(r'^[a-z0-9_-]+$', v.strip()):
            raise ValueError('Organization name can only contain lowercase letters, numbers, underscores, and hyphens')
        return v.strip()

    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        if len(v.strip()) > 100:
            raise ValueError('Title cannot exceed 100 characters')
        return v.strip()

    @validator('product_type')
    def validate_product_type(cls, v):
        if v is not None:
            if len(v.strip()) > 100:
                raise ValueError('Product type cannot exceed 100 characters')
            return v.strip()
        return v

class OrganizationUpdate(BaseModel):
    """Schema for updating an organization"""
    organization_name: Optional[str] = None
    title: Optional[str] = None
    product_type: Optional[str] = None

    @validator('organization_name')
    def validate_organization_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Organization name cannot be empty')
            if len(v.strip()) < 3:
                raise ValueError('Organization name must be at least 3 characters')
            if len(v.strip()) > 50:
                raise ValueError('Organization name cannot exceed 50 characters')
            if not re.match(r'^[a-z0-9_-]+$', v.strip()):
                raise ValueError('Organization name can only contain lowercase letters, numbers, underscores, and hyphens')
            return v.strip()
        return v

    @validator('title')
    def validate_title(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Title cannot be empty')
            if len(v.strip()) > 100:
                raise ValueError('Title cannot exceed 100 characters')
            return v.strip()
        return v

    @validator('product_type')
    def validate_product_type(cls, v):
        if v is not None:
            if len(v.strip()) > 100:
                raise ValueError('Product type cannot exceed 100 characters')
            return v.strip()
        return v

class OrganizationTransfer(BaseModel):
    """Schema for transferring organization ownership"""
    new_admin_id: int
    transfer_reason: Optional[str] = None

    @validator('transfer_reason')
    def validate_transfer_reason(cls, v):
        if v is not None and len(v.strip()) > 500:
            raise ValueError('Transfer reason cannot exceed 500 characters')
        return v.strip() if v else v

class OrganizationListResponse(BaseModel):
    """Schema for organization list response with pagination info"""
    organizations: List[Organization]
    total_count: int
    page: int
    page_size: int

class OrganizationTransferResponse(BaseModel):
    """Schema for organization transfer response"""
    message: str
    organization_id: int
    previous_admin_id: Optional[int]
    new_admin_id: int
    transfer_time: datetime 