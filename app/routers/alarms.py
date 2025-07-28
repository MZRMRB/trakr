from fastapi import APIRouter, Depends, Query, HTTPException, status, Response, Request
from app.services.alarms_service import (
    get_organizations,
    get_alarms_with_filters,
    export_alarms_to_csv,
    export_alarms_to_xlsx,
    handle_alarms,
    get_alarm_by_id
)
from app.schemas.alarms import (
    Alarm,
    Organization,
    AlarmFilter,
    AlarmExportRequest,
    AlarmHandleRequest,
    AlarmListResponse,
    AlarmExportResponse,
    AlarmHandleResponse,
    WarnType
)
from typing import List, Optional
from app.core.security import get_current_user
from app.core.rate_limiter import limiter
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alarms", tags=["Alarms"])

@router.get("", response_model=AlarmListResponse)
@limiter.limit("10/minute")
async def list_alarms(
    request: Request,
    organization: str = Query(..., description="Organization name to filter by"),
    warn_type: Optional[WarnType] = Query(None, description="Filter by warning type"),
    start_time: Optional[datetime] = Query(None, description="Start time for filtering"),
    end_time: Optional[datetime] = Query(None, description="End time for filtering"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    user=Depends(get_current_user)
):
    """
    Get all alarms with filtering and pagination.
    
    Returns a paginated list of GPS alarm events with optional filtering by organization,
    warning type, and time range.
    """
    alarm_filter = AlarmFilter(
        organization=organization,
        warn_type=warn_type,
        start_time=start_time,
        end_time=end_time,
        page=page,
        page_size=page_size
    )
    result = get_alarms_with_filters(alarm_filter)
    return AlarmListResponse(**result)

@router.get("/organizations", response_model=List[Organization])
@limiter.limit("5/minute")
async def list_organizations(request: Request, user=Depends(get_current_user)):
    """
    Get all available organizations for dropdown selection.
    
    Returns a list of organizations that can be used to filter alarms.
    """
    return get_organizations()

@router.get("/{alarm_id}", response_model=Alarm)
@limiter.limit("10/minute")
async def get_alarm(
    request: Request,
    alarm_id: int,
    user=Depends(get_current_user)
):
    """
    Get a specific alarm by ID.
    
    Returns the alarm details for the specified alarm ID.
    """
    alarm = get_alarm_by_id(alarm_id)
    if not alarm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alarm with ID {alarm_id} not found"
        )
    return alarm

@router.post("/export")
@limiter.limit("2/minute")
async def export_alarms(
    request: Request,
    export_request: AlarmExportRequest,
    user=Depends(get_current_user)
):
    """
    Export alarms to CSV or XLSX format.
    
    Exports filtered alarm data to the specified format with timestamp in filename.
    """
    try:
        # Create filter from export request
        alarm_filter = AlarmFilter(
            organization=export_request.organization,
            warn_type=export_request.warn_type,
            start_time=export_request.start_time,
            end_time=export_request.end_time
        )
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        if export_request.format == "csv":
            csv_content = export_alarms_to_csv(alarm_filter)
            filename = f"alarms_export_{timestamp}.csv"
            
            logger.info(f"Alarms exported to CSV by user {user.get('sub', 'unknown')}: {filename}")
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:  # xlsx
            xlsx_content = export_alarms_to_xlsx(alarm_filter)
            filename = f"alarms_export_{timestamp}.xlsx"
            
            logger.info(f"Alarms exported to XLSX by user {user.get('sub', 'unknown')}: {filename}")
            
            return Response(
                content=xlsx_content,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in alarm export endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export alarms"
        )

@router.post("/handle", response_model=AlarmHandleResponse)
@limiter.limit("5/minute")
async def handle_alarms_bulk(
    request: Request,
    handle_request: AlarmHandleRequest,
    user=Depends(get_current_user)
):
    """
    Handle multiple alarms in bulk.
    
    Marks the specified alarms as handled with optional reason.
    Maximum 100 alarms can be handled at once.
    All alarms must belong to the same organization.
    """
    try:
        # Extract user identifier from JWT token
        handled_by = user.get('sub', 'unknown')
        
        result = handle_alarms(handle_request, handled_by)
        return AlarmHandleResponse(
            message=result["message"],
            handled_count=result["handled_count"],
            failed_count=result["failed_count"],
            failed_alarm_ids=result["failed_alarm_ids"],
            handle_time=result["handle_time"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in alarm handle endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to handle alarms"
        ) 