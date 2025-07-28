from fastapi import APIRouter, Depends, Query, HTTPException, status, Response, Request
from app.services.tags_service import (
    get_organizations,
    get_tags_with_filters,
    export_tags_to_csv,
    export_tags_to_xlsx,
    transfer_tags,
    get_tag_by_id
)
from app.schemas.tags import (
    Tag,
    Organization,
    TagFilter,
    TagExportRequest,
    TagTransferRequest,
    TagListResponse,
    TagExportResponse,
    TagTransferResponse
)
from typing import List, Optional
from app.core.security import get_current_user
from app.core.rate_limiter import limiter
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tags", tags=["Tags"])

@router.get("", response_model=TagListResponse)
@limiter.limit("10/minute")
async def list_tags(
    request: Request,
    organization: Optional[str] = Query(None, description="Filter by organization name"),
    model: Optional[str] = Query(None, description="Filter by device model (partial match)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    user=Depends(get_current_user)
):
    """
    Get all tags with filtering and pagination.
    
    Returns a paginated list of GPS tracking tags with optional filtering by organization and model.
    """
    tag_filter = TagFilter(
        organization=organization,
        model=model,
        page=page,
        page_size=page_size
    )
    result = get_tags_with_filters(tag_filter)
    return TagListResponse(**result)

@router.get("/organizations", response_model=List[Organization])
@limiter.limit("5/minute")
async def list_organizations(request: Request, user=Depends(get_current_user)):
    """
    Get all available organizations for dropdown selection.
    
    Returns a list of organizations that can be used to filter tags.
    """
    return get_organizations()

@router.get("/{tag_id}", response_model=Tag)
@limiter.limit("10/minute")
async def get_tag(
    request: Request,
    tag_id: int,
    user=Depends(get_current_user)
):
    """
    Get a specific tag by ID.
    
    Returns the tag details for the specified tag ID.
    """
    tag = get_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )
    return tag

@router.post("/export")
@limiter.limit("2/minute")
async def export_tags(
    request: Request,
    export_request: TagExportRequest,
    user=Depends(get_current_user)
):
    """
    Export tags to CSV or XLSX format.
    
    Exports filtered tag data to the specified format with timestamp in filename.
    """
    try:
        # Create filter from export request
        tag_filter = TagFilter(
            organization=export_request.organization,
            model=export_request.model
        )
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        if export_request.format == "csv":
            csv_content = export_tags_to_csv(tag_filter)
            filename = f"tags_export_{timestamp}.csv"
            
            logger.info(f"Tags exported to CSV by user: {filename}")
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:  # xlsx
            xlsx_content = export_tags_to_xlsx(tag_filter)
            filename = f"tags_export_{timestamp}.xlsx"
            
            logger.info(f"Tags exported to XLSX by user: {filename}")
            
            return Response(
                content=xlsx_content,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in tag export endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export tags"
        )

@router.post("/transfer", response_model=TagTransferResponse)
@limiter.limit("2/minute")
async def transfer_tags_bulk(
    request: Request,
    transfer_request: TagTransferRequest,
    user=Depends(get_current_user)
):
    """
    Transfer multiple tags to a new organization.
    
    Transfers the specified tags to a new organization with optional reason.
    Maximum 100 tags can be transferred at once.
    """
    try:
        result = transfer_tags(transfer_request)
        return TagTransferResponse(
            message=result["message"],
            transferred_count=result["transferred_count"],
            failed_count=result["failed_count"],
            failed_tag_ids=result["failed_tag_ids"],
            transfer_time=result["transfer_time"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in tag transfer endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to transfer tags"
        ) 