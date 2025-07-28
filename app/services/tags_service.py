from app.db.connection import get_conn
from app.schemas.tags import Tag, TagFilter, TagExportRequest, TagTransferRequest, Organization
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
import logging
from datetime import datetime
import csv
import io

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

def get_tags_with_filters(tag_filter: TagFilter) -> Dict[str, Any]:
    """Fetch tags with filtering and pagination"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Build dynamic query based on filters
                base_query = """
                    SELECT t.sn, o.organization_name, t.imei, t.signal, t.power, 
                           t.charge_status, t.tracking_update_time, t.data_update_time, t.bluetooth_mark
                    FROM Tags t
                    JOIN Organizations o ON t.organization = o.organization_name
                    WHERE 1=1
                """
                count_query = """
                    SELECT COUNT(*)
                    FROM Tags t
                    JOIN Organizations o ON t.organization = o.organization_name
                    WHERE 1=1
                """
                params = []
                
                if tag_filter.organization:
                    base_query += " AND o.organization_name = %s"
                    count_query += " AND o.organization_name = %s"
                    params.append(tag_filter.organization)
                
                if tag_filter.model:
                    base_query += " AND t.imei ILIKE %s"
                    count_query += " AND t.imei ILIKE %s"
                    params.append(f"%{tag_filter.model}%")
                
                # Get total count
                cur.execute(count_query, params)
                total_count = cur.fetchone()[0]
                
                # Add pagination
                base_query += " ORDER BY t.sn LIMIT %s OFFSET %s"
                offset = (tag_filter.page - 1) * tag_filter.page_size
                params.extend([tag_filter.page_size, offset])
                
                cur.execute(base_query, params)
                rows = cur.fetchall()
                
                tags = [
                    Tag(
                        sn=row[0],
                        organization=row[1],
                        imei=row[2],
                        signal=row[3],
                        power=row[4],
                        charge_status=row[5],
                        tracking_update_time=row[6],
                        data_update_time=row[7],
                        bluetooth_mark=row[8]
                    ) for row in rows
                ]
                
                return {
                    "tags": tags,
                    "total_count": total_count,
                    "page": tag_filter.page,
                    "page_size": tag_filter.page_size
                }
    except Exception as e:
        logger.error(f"Error fetching tags with filters: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch tags")

def export_tags_to_csv(tag_filter: TagFilter) -> str:
    """Export tags to CSV format"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Build query similar to get_tags_with_filters but without pagination
                base_query = """
                    SELECT t.sn, o.organization_name, t.imei, t.signal, t.power, 
                           t.charge_status, t.tracking_update_time, t.data_update_time, t.bluetooth_mark
                    FROM Tags t
                    JOIN Organizations o ON t.organization = o.organization_name
                    WHERE 1=1
                """
                params = []
                
                if tag_filter.organization:
                    base_query += " AND o.organization_name = %s"
                    params.append(tag_filter.organization)
                
                if tag_filter.model:
                    base_query += " AND t.imei ILIKE %s"
                    params.append(f"%{tag_filter.model}%")
                
                base_query += " ORDER BY t.sn"
                
                cur.execute(base_query, params)
                rows = cur.fetchall()
                
                # Create CSV content
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow([
                    'SN', 'Organization', 'IMEI', 'Signal', 'Power', 
                    'Charge Status', 'Tracking Update Time', 'Data Update Time', 'Bluetooth Mark'
                ])
                
                # Write data
                for row in rows:
                    writer.writerow([
                        row[0], row[1], row[2], row[3], row[4], 
                        row[5], row[6], row[7], row[8]
                    ])
                
                csv_content = output.getvalue()
                output.close()
                
                logger.info(f"Exported {len(rows)} tags to CSV")
                return csv_content
                
    except Exception as e:
        logger.error(f"Error exporting tags to CSV: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to export tags")

def export_tags_to_xlsx(tag_filter: TagFilter) -> bytes:
    """Export tags to XLSX format (placeholder implementation)"""
    try:
        # For now, we'll return CSV content as placeholder
        # In a real implementation, you'd use openpyxl or xlsxwriter
        csv_content = export_tags_to_csv(tag_filter)
        
        logger.info(f"Exported tags to XLSX (placeholder implementation)")
        return csv_content.encode('utf-8')
        
    except Exception as e:
        logger.error(f"Error exporting tags to XLSX: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to export tags")

def transfer_tags(tag_transfer: TagTransferRequest) -> Dict[str, Any]:
    """Transfer tags to a new organization"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Check if target organization exists
                cur.execute("SELECT organization_name FROM Organizations WHERE id = %s", (tag_transfer.new_organization_id,))
                target_org = cur.fetchone()
                if not target_org:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Target organization not found"
                    )
                
                # Check if all tags exist and get their current organization
                cur.execute(
                    "SELECT sn, organization FROM Tags WHERE sn = ANY(%s)",
                    (tag_transfer.tag_ids,)
                )
                existing_tags = cur.fetchall()
                
                if len(existing_tags) != len(tag_transfer.tag_ids):
                    existing_ids = [tag[0] for tag in existing_tags]
                    missing_ids = [tid for tid in tag_transfer.tag_ids if tid not in existing_ids]
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Tags not found: {missing_ids}"
                    )
                
                # Transfer tags
                transferred_count = 0
                failed_tag_ids = []
                
                for tag_id in tag_transfer.tag_ids:
                    try:
                        cur.execute(
                            "UPDATE Tags SET organization = %s WHERE sn = %s",
                            (target_org[0], tag_id)
                        )
                        if cur.rowcount > 0:
                            transferred_count += 1
                        else:
                            failed_tag_ids.append(tag_id)
                    except Exception as e:
                        logger.error(f"Error transferring tag {tag_id}: {e}")
                        failed_tag_ids.append(tag_id)
                
                conn.commit()
                
                # Log the transfer
                logger.warning(
                    f"Tag transfer completed: {transferred_count} tags transferred to organization '{target_org[0]}' "
                    f"(ID: {tag_transfer.new_organization_id})"
                )
                if tag_transfer.reason:
                    logger.info(f"Transfer reason: {tag_transfer.reason}")
                
                return {
                    "message": "Tag transfer completed",
                    "transferred_count": transferred_count,
                    "failed_count": len(failed_tag_ids),
                    "failed_tag_ids": failed_tag_ids,
                    "transfer_time": datetime.utcnow()
                }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transferring tags: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to transfer tags")

def get_tag_by_id(tag_id: int) -> Optional[Tag]:
    """Fetch a specific tag by ID"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT t.sn, o.organization_name, t.imei, t.signal, t.power, 
                           t.charge_status, t.tracking_update_time, t.data_update_time, t.bluetooth_mark
                    FROM Tags t
                    JOIN Organizations o ON t.organization = o.organization_name
                    WHERE t.sn = %s
                    """,
                    (tag_id,)
                )
                row = cur.fetchone()
                if row:
                    return Tag(
                        sn=row[0],
                        organization=row[1],
                        imei=row[2],
                        signal=row[3],
                        power=row[4],
                        charge_status=row[5],
                        tracking_update_time=row[6],
                        data_update_time=row[7],
                        bluetooth_mark=row[8]
                    )
                return None
    except Exception as e:
        logger.error(f"Error fetching tag {tag_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch tag") 