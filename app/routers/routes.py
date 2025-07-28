from fastapi import APIRouter, Depends, Query, HTTPException, status, Response, Request
from app.services.routes_service import (
    get_organizations,
    get_routes_with_filters,
    export_routes_to_csv,
    export_routes_to_xlsx,
    get_route_by_id,
    get_route_statistics
)
from app.schemas.routes import (
    Route,
    Organization,
    RouteFilter,
    RouteExportRequest,
    RouteListResponse,
    RouteExportResponse
)
from typing import List, Optional
from app.core.security import get_current_user
from app.core.rate_limiter import limiter
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/routes", tags=["Routes"])

@router.get("", response_model=RouteListResponse)
@limiter.limit("10/minute")
async def list_routes(
    request: Request,
    organization: str = Query(..., description="Organization name to filter by"),
    start_time: datetime = Query(..., description="Start time for filtering"),
    end_time: datetime = Query(..., description="End time for filtering"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    user=Depends(get_current_user)
):
    """
    Get all routes with filtering and pagination.
    
    Returns a paginated list of GPS route history with filtering by organization and time range.
    """
    route_filter = RouteFilter(
        organization=organization,
        start_time=start_time,
        end_time=end_time,
        page=page,
        page_size=page_size
    )
    result = get_routes_with_filters(route_filter)
    return RouteListResponse(**result)

@router.get("/organizations", response_model=List[Organization])
@limiter.limit("5/minute")
async def list_organizations(request: Request, user=Depends(get_current_user)):
    """
    Get all available organizations for dropdown selection.
    
    Returns a list of organizations that can be used to filter routes.
    """
    return get_organizations()

@router.get("/{route_id}", response_model=Route)
@limiter.limit("10/minute")
async def get_route(
    request: Request,
    route_id: int,
    user=Depends(get_current_user)
):
    """
    Get a specific route by ID.
    
    Returns the route details for the specified route ID.
    """
    route = get_route_by_id(route_id)
    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route with ID {route_id} not found"
        )
    return route

@router.get("/statistics/{organization}")
@limiter.limit("5/minute")
async def get_routes_statistics(
    request: Request,
    organization: str,
    start_time: datetime = Query(..., description="Start time for statistics"),
    end_time: datetime = Query(..., description="End time for statistics"),
    user=Depends(get_current_user)
):
    """
    Get route statistics for analytics.
    
    Returns basic statistics about routes for the specified organization and time range.
    """
    try:
        stats = get_route_statistics(organization, start_time, end_time)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in route statistics endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch route statistics"
        )

@router.post("/export")
@limiter.limit("2/minute")
async def export_routes(
    request: Request,
    export_request: RouteExportRequest,
    user=Depends(get_current_user)
):
    """
    Export routes to CSV or XLSX format.
    
    Exports filtered route data to the specified format with timestamp in filename.
    """
    try:
        # Create filter from export request
        route_filter = RouteFilter(
            organization=export_request.organization,
            start_time=export_request.start_time,
            end_time=export_request.end_time
        )
        
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        if export_request.format == "csv":
            csv_content = export_routes_to_csv(route_filter)
            filename = f"routes_export_{timestamp}.csv"
            
            logger.info(f"Routes exported to CSV by user {user.get('sub', 'unknown')}: {filename}")
            
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        else:  # xlsx
            xlsx_content = export_routes_to_xlsx(route_filter)
            filename = f"routes_export_{timestamp}.xlsx"
            
            logger.info(f"Routes exported to XLSX by user {user.get('sub', 'unknown')}: {filename}")
            
            return Response(
                content=xlsx_content,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in route export endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export routes"
        ) 