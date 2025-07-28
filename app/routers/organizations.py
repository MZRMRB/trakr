from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from app.services.organizations_service import (
    get_organizations_with_pagination,
    get_organization_by_id,
    create_organization,
    update_organization,
    transfer_organization_ownership,
    check_organization_exists
)
from app.schemas.organizations import (
    Organization,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationTransfer,
    OrganizationListResponse,
    OrganizationTransferResponse
)
from typing import List
from app.core.security import get_current_user
from app.core.rate_limiter import limiter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/organizations", tags=["Organizations"])

@router.get("", response_model=OrganizationListResponse)
@limiter.limit("10/minute")
async def list_organizations(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    user=Depends(get_current_user)
):
    """
    Get all organizations with pagination.
    
    Returns a paginated list of all organizations in the system.
    """
    result = get_organizations_with_pagination(page, page_size)
    return OrganizationListResponse(**result)

@router.get("/{organization_id}", response_model=Organization)
@limiter.limit("10/minute")
async def get_organization(
    request: Request,
    organization_id: int,
    user=Depends(get_current_user)
):
    """
    Get a specific organization by ID.
    
    Returns the organization details for the specified organization ID.
    """
    organization = get_organization_by_id(organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with ID {organization_id} not found"
        )
    return organization

@router.post("", response_model=Organization, status_code=status.HTTP_201_CREATED)
@limiter.limit("2/minute")
async def create_new_organization(
    request: Request,
    organization: OrganizationCreate,
    user=Depends(get_current_user)
):
    """
    Create a new organization.
    
    Creates a new organization with the provided details including name, title, and optional product type.
    Organization names must be unique and follow the naming convention (lowercase letters, numbers, underscores, hyphens).
    """
    return create_organization(organization)

@router.put("/{organization_id}", response_model=Organization)
@limiter.limit("5/minute")
async def update_organization_by_id(
    request: Request,
    organization_id: int,
    organization_update: OrganizationUpdate,
    user=Depends(get_current_user)
):
    """
    Update an organization by ID.
    
    Updates the specified organization with the provided fields.
    Only the fields that are provided will be updated.
    Organization names must remain unique.
    """
    updated_organization = update_organization(organization_id, organization_update)
    if not updated_organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization with ID {organization_id} not found"
        )
    return updated_organization

@router.post("/{organization_id}/transfer", response_model=OrganizationTransferResponse)
@limiter.limit("2/minute")
async def transfer_organization_ownership_by_id(
    request: Request,
    organization_id: int,
    transfer_data: OrganizationTransfer,
    user=Depends(get_current_user)
):
    """
    Transfer organization ownership to a new admin.
    
    Transfers ownership of the specified organization to a new admin user.
    This is a placeholder implementation that logs the transfer request.
    """
    try:
        result = transfer_organization_ownership(organization_id, transfer_data)
        return OrganizationTransferResponse(
            message=result["message"],
            organization_id=result["organization_id"],
            previous_admin_id=result["previous_admin_id"],
            new_admin_id=result["new_admin_id"],
            transfer_time=result["transfer_time"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in organization transfer endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transfer organization ownership"
        ) 