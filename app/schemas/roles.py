from pydantic import BaseModel
from typing import Optional

class Role(BaseModel):
    sn: int
    organization: str
    name: str
    color: Optional[str]

class RoleCreate(BaseModel):
    organization: str
    name: str
    color: Optional[str]

class Organization(BaseModel):
    id: int
    organization_name: str
    title: Optional[str] 