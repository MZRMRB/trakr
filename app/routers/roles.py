from fastapi import APIRouter, Depends, Query, Request
from app.services.roles_service import get_organizations, get_roles_by_organization
from app.schemas.roles import Role, Organization
from typing import List
from app.core.security import get_current_user
from app.core.rate_limiter import limiter

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.get("/organizations", response_model=List[Organization])
@limiter.limit("5/minute")
def list_organizations(request: Request, user=Depends(get_current_user)):
    return get_organizations()

@router.get("", response_model=List[Role])
@limiter.limit("10/minute")
def list_roles(request: Request, organization: str = Query(...), user=Depends(get_current_user)):
    return get_roles_by_organization(organization) 