from pydantic import BaseModel, validator
from typing import Optional, List
import re
from enum import Enum

class PermissionLevel(str, Enum):
    """Enum for account permission levels"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"

class Account(BaseModel):
    """Schema for account response"""
    sn: int
    organization: str
    account: str
    permission: str
    login_free_address: Optional[str]

class AccountCreate(BaseModel):
    """Schema for creating a new account"""
    organization: str
    account: str
    permission: str
    login_free_address: Optional[str] = None

    @validator('account')
    def validate_account_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Account name cannot be empty')
        if len(v.strip()) > 50:
            raise ValueError('Account name cannot exceed 50 characters')
        # Basic username validation (alphanumeric, underscore, hyphen)
        if not re.match(r'^[a-zA-Z0-9_-]+$', v.strip()):
            raise ValueError('Account name can only contain letters, numbers, underscores, and hyphens')
        return v.strip()

    @validator('permission')
    def validate_permission(cls, v):
        valid_permissions = [p.value for p in PermissionLevel]
        if v not in valid_permissions:
            raise ValueError(f'Permission must be one of: {", ".join(valid_permissions)}')
        return v

    @validator('login_free_address')
    def validate_login_free_address(cls, v):
        if v is not None and v.strip():
            # IP address validation
            ip_pattern = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
            # URL validation (basic)
            url_pattern = re.compile(r'^https?://[^\s/$.?#].[^\s]*$')
            
            if not (ip_pattern.match(v.strip()) or url_pattern.match(v.strip())):
                raise ValueError('Login-free address must be a valid IP address or URL')
            return v.strip()
        return v

class AccountUpdate(BaseModel):
    """Schema for updating an account"""
    account: Optional[str] = None
    permission: Optional[str] = None
    login_free_address: Optional[str] = None

    @validator('account')
    def validate_account_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Account name cannot be empty')
            if len(v.strip()) > 50:
                raise ValueError('Account name cannot exceed 50 characters')
            if not re.match(r'^[a-zA-Z0-9_-]+$', v.strip()):
                raise ValueError('Account name can only contain letters, numbers, underscores, and hyphens')
            return v.strip()
        return v

    @validator('permission')
    def validate_permission(cls, v):
        if v is not None:
            valid_permissions = [p.value for p in PermissionLevel]
            if v not in valid_permissions:
                raise ValueError(f'Permission must be one of: {", ".join(valid_permissions)}')
        return v

    @validator('login_free_address')
    def validate_login_free_address(cls, v):
        if v is not None and v.strip():
            ip_pattern = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
            url_pattern = re.compile(r'^https?://[^\s/$.?#].[^\s]*$')
            
            if not (ip_pattern.match(v.strip()) or url_pattern.match(v.strip())):
                raise ValueError('Login-free address must be a valid IP address or URL')
            return v.strip()
        return v

class Organization(BaseModel):
    """Schema for organization response"""
    id: int
    organization_name: str
    title: Optional[str]

class AccountListResponse(BaseModel):
    """Schema for account list response with pagination info"""
    accounts: List[Account]
    total_count: int
    page: int
    page_size: int

class PasswordResetResponse(BaseModel):
    """Schema for password reset response"""
    message: str
    reset_token: Optional[str] = None

class AccountStatusResponse(BaseModel):
    """Schema for account status change response"""
    message: str
    account_id: int
    status: str 