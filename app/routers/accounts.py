from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from app.services.accounts_service import (
    get_organizations,
    get_accounts_by_organization,
    create_account,
    get_account_by_id,
    update_account,
    delete_account,
    reset_account_password,
    disable_account
)
from app.schemas.accounts import (
    Account,
    Organization,
    AccountCreate,
    AccountUpdate,
    AccountListResponse,
    PasswordResetResponse,
    AccountStatusResponse
)
from typing import List, Optional
from app.core.security import get_current_user
from app.core.rate_limiter import limiter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.get("/organizations", response_model=List[Organization])
@limiter.limit("5/minute")
async def list_organizations(request: Request, user=Depends(get_current_user)):
    """
    Get all available organizations for dropdown selection.
    
    Returns a list of organizations that can be used to filter accounts.
    """
    return get_organizations()

@router.get("", response_model=AccountListResponse)
@limiter.limit("10/minute")
async def list_accounts(
    request: Request,
    organization: str = Query(..., description="Organization name to filter by"),
    account_name: Optional[str] = Query(None, description="Filter by account name (partial match)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    user=Depends(get_current_user)
):
    """
    Get all accounts for a specific organization with optional filtering and pagination.
    
    Returns a paginated list of accounts filtered by organization and optionally by account name.
    """
    result = get_accounts_by_organization(organization, account_name, page, page_size)
    return AccountListResponse(**result)

@router.post("", response_model=Account, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_new_account(
    request: Request,
    account: AccountCreate,
    user=Depends(get_current_user)
):
    """
    Create a new account.
    
    Creates a new account with the provided details including organization,
    username, permission level, and optional login-free address.
    """
    return create_account(account)

@router.get("/{account_id}", response_model=Account)
@limiter.limit("10/minute")
async def get_account(
    request: Request,
    account_id: int,
    user=Depends(get_current_user)
):
    """
    Get a specific account by ID.
    
    Returns the account details for the specified account ID.
    """
    account = get_account_by_id(account_id)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found"
        )
    return account

@router.put("/{account_id}", response_model=Account)
@limiter.limit("5/minute")
async def update_account_by_id(
    request: Request,
    account_id: int,
    account_update: AccountUpdate,
    user=Depends(get_current_user)
):
    """
    Update an account by ID.
    
    Updates the specified account with the provided fields.
    Only the fields that are provided will be updated.
    """
    updated_account = update_account(account_id, account_update)
    if not updated_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found"
        )
    return updated_account

@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def delete_account_by_id(
    request: Request,
    account_id: int,
    user=Depends(get_current_user)
):
    """
    Delete an account by ID.
    
    Permanently deletes the account with the specified ID.
    """
    deleted = delete_account(account_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {account_id} not found"
        )

@router.post("/{account_id}/reset-password", response_model=PasswordResetResponse)
@limiter.limit("2/minute")
async def reset_password(
    request: Request,
    account_id: int,
    user=Depends(get_current_user)
):
    """
    Reset password for an account.
    
    Generates a password reset token for the specified account.
    The token is valid for 24 hours.
    """
    try:
        result = reset_account_password(account_id)
        return PasswordResetResponse(
            message=result["message"],
            reset_token=result["reset_token"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in password reset endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )

@router.post("/{account_id}/disable", response_model=AccountStatusResponse)
@limiter.limit("2/minute")
async def disable_account_by_id(
    request: Request,
    account_id: int,
    user=Depends(get_current_user)
):
    """
    Disable an account.
    
    Disables the specified account, preventing login access.
    This is a placeholder implementation.
    """
    try:
        result = disable_account(account_id)
        return AccountStatusResponse(
            message=result["message"],
            account_id=result["account_id"],
            status=result["status"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in account disable endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable account"
        ) 