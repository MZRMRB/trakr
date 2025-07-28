from app.db.connection import get_conn
from app.schemas.alarms import Alarm, AlarmFilter, AlarmExportRequest, AlarmHandleRequest, Organization
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

def get_alarms_with_filters(alarm_filter: AlarmFilter) -> Dict[str, Any]:
    """Fetch alarms with filtering and pagination using JOINs"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Build dynamic query with JOINs to resolve names
                base_query = """
                    SELECT a.sn, a.organization, t.imei, to.name as tracking_object_name,
                           a.warn_type, a.time, a.check_the_time, a.check_time,
                           a.is_handled, a.handled_by, a.handled_at, a.handle_reason
                    FROM Alarms a
                    LEFT JOIN Tags t ON a.imei = t.imei
                    LEFT JOIN Tracking_Objects to ON t.imei = to.mac
                    WHERE a.organization = %s
                """
                count_query = """
                    SELECT COUNT(*)
                    FROM Alarms a
                    WHERE a.organization = %s
                """
                params = [alarm_filter.organization]
                
                if alarm_filter.warn_type:
                    base_query += " AND a.warn_type = %s"
                    count_query += " AND a.warn_type = %s"
                    params.append(alarm_filter.warn_type.value)
                
                if alarm_filter.start_time:
                    base_query += " AND a.time >= %s"
                    count_query += " AND a.time >= %s"
                    params.append(alarm_filter.start_time)
                
                if alarm_filter.end_time:
                    base_query += " AND a.time <= %s"
                    count_query += " AND a.time <= %s"
                    params.append(alarm_filter.end_time)
                
                # Get total count
                cur.execute(count_query, params)
                total_count = cur.fetchone()[0]
                
                # Add pagination
                base_query += " ORDER BY a.time DESC LIMIT %s OFFSET %s"
                offset = (alarm_filter.page - 1) * alarm_filter.page_size
                params.extend([alarm_filter.page_size, offset])
                
                cur.execute(base_query, params)
                rows = cur.fetchall()
                
                alarms = [
                    Alarm(
                        sn=row[0],
                        organization=row[1],
                        imei=row[2] or "Unknown",
                        tracking_object=row[3] or "Unknown",
                        warn_type=row[4],
                        time=row[5],
                        check_the_time=row[6],
                        check_time=row[7],
                        is_handled=row[8],
                        handled_by=row[9],
                        handled_at=row[10],
                        handle_reason=row[11]
                    ) for row in rows
                ]
                
                return {
                    "alarms": alarms,
                    "pagination": {
                        "page": alarm_filter.page,
                        "page_size": alarm_filter.page_size,
                        "total_records": total_count
                    }
                }
    except Exception as e:
        logger.error(f"Error fetching alarms with filters: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch alarms")

def export_alarms_to_csv(alarm_filter: AlarmFilter) -> str:
    """Export alarms to CSV format"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Build query similar to get_alarms_with_filters but without pagination
                base_query = """
                    SELECT a.sn, a.organization, t.imei, to.name as tracking_object_name,
                           a.warn_type, a.time, a.check_the_time, a.check_time,
                           a.is_handled, a.handled_by, a.handled_at, a.handle_reason
                    FROM Alarms a
                    LEFT JOIN Tags t ON a.imei = t.imei
                    LEFT JOIN Tracking_Objects to ON t.imei = to.mac
                    WHERE a.organization = %s
                """
                params = [alarm_filter.organization]
                
                if alarm_filter.warn_type:
                    base_query += " AND a.warn_type = %s"
                    params.append(alarm_filter.warn_type.value)
                
                if alarm_filter.start_time:
                    base_query += " AND a.time >= %s"
                    params.append(alarm_filter.start_time)
                
                if alarm_filter.end_time:
                    base_query += " AND a.time <= %s"
                    params.append(alarm_filter.end_time)
                
                base_query += " ORDER BY a.time DESC"
                
                cur.execute(base_query, params)
                rows = cur.fetchall()
                
                # Create CSV content
                output = io.StringIO()
                writer = csv.writer(output)
                
                # Write header
                writer.writerow([
                    'SN', 'Organization', 'IMEI', 'Tracking Object', 'Warn Type', 
                    'Time', 'Check The Time', 'Check Time', 'Is Handled', 
                    'Handled By', 'Handled At', 'Handle Reason'
                ])
                
                # Write data
                for row in rows:
                    writer.writerow([
                        row[0], row[1], row[2] or "Unknown", row[3] or "Unknown", row[4],
                        row[5], row[6], row[7], row[8], row[9], row[10], row[11]
                    ])
                
                csv_content = output.getvalue()
                output.close()
                
                logger.info(f"Exported {len(rows)} alarms to CSV for organization: {alarm_filter.organization}")
                return csv_content
                
    except Exception as e:
        logger.error(f"Error exporting alarms to CSV: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to export alarms")

def export_alarms_to_xlsx(alarm_filter: AlarmFilter) -> bytes:
    """Export alarms to XLSX format (placeholder implementation)"""
    try:
        # For now, we'll return CSV content as placeholder
        # In a real implementation, you'd use openpyxl or xlsxwriter
        csv_content = export_alarms_to_csv(alarm_filter)
        
        logger.info(f"Exported alarms to XLSX (placeholder implementation)")
        return csv_content.encode('utf-8')
        
    except Exception as e:
        logger.error(f"Error exporting alarms to XLSX: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to export alarms")

def handle_alarms(alarm_handle: AlarmHandleRequest, handled_by: str) -> Dict[str, Any]:
    """Handle multiple alarms with transactional integrity"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Check if all alarms exist and belong to the same organization
                cur.execute(
                    """
                    SELECT sn, organization, is_handled 
                    FROM Alarms 
                    WHERE sn = ANY(%s)
                    """,
                    (alarm_handle.alarm_ids,)
                )
                existing_alarms = cur.fetchall()
                
                if len(existing_alarms) != len(alarm_handle.alarm_ids):
                    existing_ids = [alarm[0] for alarm in existing_alarms]
                    missing_ids = [aid for aid in alarm_handle.alarm_ids if aid not in existing_ids]
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Alarms not found: {missing_ids}"
                    )
                
                # Check if all alarms belong to the same organization
                organizations = set(alarm[1] for alarm in existing_alarms)
                if len(organizations) > 1:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="All alarms must belong to the same organization"
                    )
                
                # Check if any alarms are already handled
                already_handled = [alarm[0] for alarm in existing_alarms if alarm[2]]
                if already_handled:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Alarms already handled: {already_handled}"
                    )
                
                # Handle alarms
                handled_count = 0
                failed_alarm_ids = []
                
                for alarm_id in alarm_handle.alarm_ids:
                    try:
                        cur.execute(
                            """
                            UPDATE Alarms 
                            SET is_handled = TRUE, handled_by = %s, handled_at = %s, handle_reason = %s
                            WHERE sn = %s
                            """,
                            (handled_by, datetime.utcnow(), alarm_handle.reason, alarm_id)
                        )
                        if cur.rowcount > 0:
                            handled_count += 1
                        else:
                            failed_alarm_ids.append(alarm_id)
                    except Exception as e:
                        logger.error(f"Error handling alarm {alarm_id}: {e}")
                        failed_alarm_ids.append(alarm_id)
                
                conn.commit()
                
                # Log the handling action
                logger.warning(
                    f"Alarms handled by {handled_by}: {handled_count} alarms handled, "
                    f"{len(failed_alarm_ids)} failed"
                )
                if alarm_handle.reason:
                    logger.info(f"Handle reason: {alarm_handle.reason}")
                
                return {
                    "message": "Alarm handling completed",
                    "handled_count": handled_count,
                    "failed_count": len(failed_alarm_ids),
                    "failed_alarm_ids": failed_alarm_ids,
                    "handle_time": datetime.utcnow()
                }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling alarms: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to handle alarms")

def get_alarm_by_id(alarm_id: int) -> Optional[Alarm]:
    """Fetch a specific alarm by ID"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT a.sn, a.organization, t.imei, to.name as tracking_object_name,
                           a.warn_type, a.time, a.check_the_time, a.check_time,
                           a.is_handled, a.handled_by, a.handled_at, a.handle_reason
                    FROM Alarms a
                    LEFT JOIN Tags t ON a.imei = t.imei
                    LEFT JOIN Tracking_Objects to ON t.imei = to.mac
                    WHERE a.sn = %s
                    """,
                    (alarm_id,)
                )
                row = cur.fetchone()
                if row:
                    return Alarm(
                        sn=row[0],
                        organization=row[1],
                        imei=row[2] or "Unknown",
                        tracking_object=row[3] or "Unknown",
                        warn_type=row[4],
                        time=row[5],
                        check_the_time=row[6],
                        check_time=row[7],
                        is_handled=row[8],
                        handled_by=row[9],
                        handled_at=row[10],
                        handle_reason=row[11]
                    )
                return None
    except Exception as e:
        logger.error(f"Error fetching alarm {alarm_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch alarm") 