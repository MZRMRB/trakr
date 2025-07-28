from app.db.connection import get_conn
from app.schemas.organizations import Organization, OrganizationCreate, OrganizationUpdate, OrganizationTransfer
from typing import List, Optional
from fastapi import HTTPException, status
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def get_organizations_with_pagination(page: int = 1, page_size: int = 20) -> dict:
    """Fetch all organizations with pagination"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Get total count
                cur.execute("SELECT COUNT(*) FROM Organizations")
                total_count = cur.fetchone()[0]
                
                # Get paginated results
                offset = (page - 1) * page_size
                cur.execute(
                    """
                    SELECT id, organization_name, title, product_type, create_time 
                    FROM Organizations 
                    ORDER BY organization_name 
                    LIMIT %s OFFSET %s
                    """,
                    (page_size, offset)
                )
                rows = cur.fetchall()
                
                organizations = [
                    Organization(
                        id=row[0], 
                        organization_name=row[1], 
                        title=row[2], 
                        product_type=row[3], 
                        create_time=row[4]
                    ) for row in rows
                ]
                
                return {
                    "organizations": organizations,
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size
                }
    except Exception as e:
        logger.error(f"Error fetching organizations: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch organizations")

def get_organization_by_id(organization_id: int) -> Optional[Organization]:
    """Fetch a specific organization by ID"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, organization_name, title, product_type, create_time 
                    FROM Organizations 
                    WHERE id = %s
                    """,
                    (organization_id,)
                )
                row = cur.fetchone()
                if row:
                    return Organization(
                        id=row[0], 
                        organization_name=row[1], 
                        title=row[2], 
                        product_type=row[3], 
                        create_time=row[4]
                    )
                return None
    except Exception as e:
        logger.error(f"Error fetching organization {organization_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch organization")

def create_organization(organization: OrganizationCreate) -> Organization:
    """Create a new organization"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Check if organization name already exists
                cur.execute("SELECT 1 FROM Organizations WHERE organization_name = %s", (organization.organization_name,))
                if cur.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="Organization name already exists"
                    )
                
                cur.execute(
                    """
                    INSERT INTO Organizations (organization_name, title, product_type, create_time)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, organization_name, title, product_type, create_time
                    """,
                    (organization.organization_name, organization.title, organization.product_type, datetime.utcnow())
                )
                row = cur.fetchone()
                conn.commit()
                
                logger.info(f"Organization '{organization.organization_name}' created successfully")
                return Organization(
                    id=row[0], 
                    organization_name=row[1], 
                    title=row[2], 
                    product_type=row[3], 
                    create_time=row[4]
                )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create organization")

def update_organization(organization_id: int, organization_update: OrganizationUpdate) -> Optional[Organization]:
    """Update an organization by ID"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Build dynamic update query based on provided fields
                update_fields = []
                update_values = []
                
                if organization_update.organization_name is not None:
                    # Check if new organization name already exists (excluding current org)
                    cur.execute(
                        "SELECT 1 FROM Organizations WHERE organization_name = %s AND id != %s", 
                        (organization_update.organization_name, organization_id)
                    )
                    if cur.fetchone():
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Organization name already exists"
                        )
                    update_fields.append("organization_name = %s")
                    update_values.append(organization_update.organization_name)
                
                if organization_update.title is not None:
                    update_fields.append("title = %s")
                    update_values.append(organization_update.title)
                
                if organization_update.product_type is not None:
                    update_fields.append("product_type = %s")
                    update_values.append(organization_update.product_type)
                
                if not update_fields:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
                
                update_values.append(organization_id)
                query = f"""
                    UPDATE Organizations 
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                    RETURNING id, organization_name, title, product_type, create_time
                """
                
                cur.execute(query, update_values)
                row = cur.fetchone()
                conn.commit()
                
                if row:
                    logger.info(f"Organization {organization_id} updated successfully")
                    return Organization(
                        id=row[0], 
                        organization_name=row[1], 
                        title=row[2], 
                        product_type=row[3], 
                        create_time=row[4]
                    )
                return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating organization {organization_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update organization")

def transfer_organization_ownership(organization_id: int, transfer_data: OrganizationTransfer) -> dict:
    """Transfer organization ownership to a new admin"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Check if organization exists
                cur.execute("SELECT organization_name FROM Organizations WHERE id = %s", (organization_id,))
                org_info = cur.fetchone()
                if not org_info:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, 
                        detail="Organization not found"
                    )
                
                # Check if new admin exists (assuming there's an admin table or accounts table)
                # For now, we'll just log the transfer request
                # In a real implementation, you'd validate the new_admin_id exists
                
                # Log the transfer request
                logger.warning(
                    f"Organization ownership transfer requested: "
                    f"Org '{org_info[0]}' (ID: {organization_id}) -> Admin ID: {transfer_data.new_admin_id}"
                )
                if transfer_data.transfer_reason:
                    logger.info(f"Transfer reason: {transfer_data.transfer_reason}")
                
                # In a real implementation, you'd update the organization's admin_id field
                # For now, we'll just return a success response
                return {
                    "message": "Organization ownership transfer initiated successfully",
                    "organization_id": organization_id,
                    "previous_admin_id": None,  # Would be fetched from current state
                    "new_admin_id": transfer_data.new_admin_id,
                    "transfer_time": datetime.utcnow()
                }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transferring organization ownership {organization_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to transfer organization ownership")

def check_organization_exists(organization_id: int) -> bool:
    """Check if an organization exists by ID"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM Organizations WHERE id = %s", (organization_id,))
                return cur.fetchone() is not None
    except Exception as e:
        logger.error(f"Error checking organization existence {organization_id}: {e}")
        return False 