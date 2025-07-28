from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File, Request
from app.services.tracking_objects_service import (
    get_organizations,
    get_tracking_objects_by_organization,
    create_tracking_object,
    get_tracking_object_by_id,
    update_tracking_object,
    delete_tracking_object,
    import_tracking_objects_from_file,
    upload_tracking_object_photos
)
from app.schemas.tracking_objects import (
    TrackingObject,
    Organization,
    TrackingObjectCreate,
    TrackingObjectUpdate,
    ImportResponse,
    PhotoUploadResponse
)
from typing import List
from app.core.security import get_current_user
from app.core.rate_limiter import limiter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tracking-objects", tags=["Tracking Objects"])

@router.get("/organizations", response_model=List[Organization])
@limiter.limit("5/minute")
async def list_organizations(request: Request, user=Depends(get_current_user)):
    """
    Get all available organizations for dropdown selection.
    
    Returns a list of organizations that can be used to filter tracking objects.
    """
    return get_organizations()

@router.get("", response_model=List[TrackingObject])
@limiter.limit("10/minute")
async def list_tracking_objects(
    request: Request,
    organization: str = Query(..., description="Organization name to filter by"),
    user=Depends(get_current_user)
):
    """
    Get all tracking objects for a specific organization.
    
    Returns a list of tracking objects filtered by the provided organization name.
    """
    return get_tracking_objects_by_organization(organization)

@router.post("", response_model=TrackingObject, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_new_tracking_object(
    request: Request,
    tracking_object: TrackingObjectCreate,
    user=Depends(get_current_user)
):
    """
    Create a new tracking object.
    
    Creates a new tracking object with the provided details including organization,
    name, role, and MAC address (optional).
    """
    return create_tracking_object(tracking_object)

@router.get("/{object_id}", response_model=TrackingObject)
@limiter.limit("10/minute")
async def get_tracking_object(
    request: Request,
    object_id: int,
    user=Depends(get_current_user)
):
    """
    Get a specific tracking object by ID.
    
    Returns the tracking object details for the specified object ID.
    """
    tracking_object = get_tracking_object_by_id(object_id)
    if not tracking_object:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tracking object with ID {object_id} not found"
        )
    return tracking_object

@router.put("/{object_id}", response_model=TrackingObject)
@limiter.limit("5/minute")
async def update_tracking_object_by_id(
    request: Request,
    object_id: int,
    tracking_object: TrackingObjectUpdate,
    user=Depends(get_current_user)
):
    """
    Update a tracking object by ID.
    
    Updates the specified tracking object with the provided fields.
    Only the fields that are provided will be updated.
    """
    updated_object = update_tracking_object(object_id, tracking_object)
    if not updated_object:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tracking object with ID {object_id} not found"
        )
    return updated_object

@router.delete("/{object_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def delete_tracking_object_by_id(
    request: Request,
    object_id: int,
    user=Depends(get_current_user)
):
    """
    Delete a tracking object by ID.
    
    Permanently deletes the tracking object with the specified ID.
    """
    deleted = delete_tracking_object(object_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tracking object with ID {object_id} not found"
        )

@router.post("/import", response_model=ImportResponse)
@limiter.limit("2/minute")
async def import_tracking_objects(
    request: Request,
    file: UploadFile = File(..., description="CSV or XLSX file containing tracking objects"),
    user=Depends(get_current_user)
):
    """
    Import tracking objects from a CSV or XLSX file.
    
    Uploads a file containing tracking object data and imports them into the system.
    This is a placeholder implementation.
    """
    try:
        # Read file content (placeholder implementation)
        content = await file.read()
        file_content = content.decode('utf-8') if isinstance(content, bytes) else str(content)
        
        result = import_tracking_objects_from_file(file_content)
        return ImportResponse(**result)
    except Exception as e:
        logger.error(f"Error importing tracking objects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to import tracking objects"
        )

@router.post("/photo-batch-upload", response_model=PhotoUploadResponse)
@limiter.limit("2/minute")
async def upload_tracking_object_photos_batch(
    request: Request,
    files: List[UploadFile] = File(..., description="Multiple photo files to upload"),
    user=Depends(get_current_user)
):
    """
    Upload multiple tracking object photos.
    
    Uploads multiple photo files for tracking objects.
    This is a placeholder implementation.
    """
    try:
        # Read file contents (placeholder implementation)
        file_contents = []
        for file in files:
            content = await file.read()
            file_contents.append(content)
        
        result = upload_tracking_object_photos(file_contents)
        return PhotoUploadResponse(**result)
    except Exception as e:
        logger.error(f"Error uploading tracking object photos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload tracking object photos"
        ) 