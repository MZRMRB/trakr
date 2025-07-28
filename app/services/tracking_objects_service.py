from app.db.connection import get_conn
from app.schemas.tracking_objects import TrackingObject, Organization, TrackingObjectCreate, TrackingObjectUpdate
from typing import List, Optional
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

def get_organizations() -> List[Organization]:
    """Fetch all available organizations for dropdown selection"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, organization_name, title FROM Organizations ORDER BY organization_name")
                rows = cur.fetchall()
                return [Organization(id=row[0], organization_name=row[1], title=row[2]) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching organizations: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch organizations")

def get_tracking_objects_by_organization(organization: str) -> List[TrackingObject]:
    """Fetch all tracking objects for a specific organization"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT sn, organization, name, role, mac FROM Tracking_Objects WHERE organization = %s ORDER BY name",
                    (organization,)
                )
                rows = cur.fetchall()
                return [TrackingObject(sn=row[0], organization=row[1], name=row[2], role=row[3], mac=row[4]) for row in rows]
    except Exception as e:
        logger.error(f"Error fetching tracking objects for organization {organization}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch tracking objects")

def create_tracking_object(tracking_object: TrackingObjectCreate) -> TrackingObject:
    """Create a new tracking object"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO Tracking_Objects (organization, name, role, mac)
                    VALUES (%s, %s, %s, %s)
                    RETURNING sn, organization, name, role, mac
                    """,
                    (tracking_object.organization, tracking_object.name, tracking_object.role, tracking_object.mac)
                )
                row = cur.fetchone()
                conn.commit()
                return TrackingObject(sn=row[0], organization=row[1], name=row[2], role=row[3], mac=row[4])
    except Exception as e:
        logger.error(f"Error creating tracking object: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create tracking object")

def get_tracking_object_by_id(object_id: int) -> Optional[TrackingObject]:
    """Fetch a specific tracking object by ID"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT sn, organization, name, role, mac FROM Tracking_Objects WHERE sn = %s",
                    (object_id,)
                )
                row = cur.fetchone()
                if row:
                    return TrackingObject(sn=row[0], organization=row[1], name=row[2], role=row[3], mac=row[4])
                return None
    except Exception as e:
        logger.error(f"Error fetching tracking object {object_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch tracking object")

def update_tracking_object(object_id: int, tracking_object: TrackingObjectUpdate) -> Optional[TrackingObject]:
    """Update a tracking object by ID"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Build dynamic update query based on provided fields
                update_fields = []
                update_values = []
                
                if tracking_object.name is not None:
                    update_fields.append("name = %s")
                    update_values.append(tracking_object.name)
                
                if tracking_object.role is not None:
                    update_fields.append("role = %s")
                    update_values.append(tracking_object.role)
                
                if tracking_object.mac is not None:
                    update_fields.append("mac = %s")
                    update_values.append(tracking_object.mac)
                
                if not update_fields:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
                
                update_values.append(object_id)
                query = f"""
                    UPDATE Tracking_Objects 
                    SET {', '.join(update_fields)}
                    WHERE sn = %s
                    RETURNING sn, organization, name, role, mac
                """
                
                cur.execute(query, update_values)
                row = cur.fetchone()
                conn.commit()
                
                if row:
                    return TrackingObject(sn=row[0], organization=row[1], name=row[2], role=row[3], mac=row[4])
                return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tracking object {object_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update tracking object")

def delete_tracking_object(object_id: int) -> bool:
    """Delete a tracking object by ID"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM Tracking_Objects WHERE sn = %s", (object_id,))
                deleted_count = cur.rowcount
                conn.commit()
                return deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting tracking object {object_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete tracking object")

def import_tracking_objects_from_file(file_content: str) -> dict:
    """Placeholder for importing tracking objects from CSV/XLSX file"""
    # TODO: Implement actual file parsing logic
    logger.info("Import tracking objects from file - placeholder implementation")
    return {
        "message": "Import functionality not yet implemented",
        "imported_count": 0,
        "errors": ["Import feature is under development"]
    }

def upload_tracking_object_photos(files: List[bytes]) -> dict:
    """Placeholder for uploading multiple tracking object photos"""
    # TODO: Implement actual file upload and storage logic
    logger.info("Upload tracking object photos - placeholder implementation")
    return {
        "message": "Photo upload functionality not yet implemented",
        "uploaded_count": 0,
        "file_names": []
    } 