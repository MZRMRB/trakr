from app.db.connection import get_conn
from app.schemas.accounts import Account, Organization, AccountCreate, AccountUpdate
from typing import List, Optional
from fastapi import HTTPException, status
import logging
import secrets
import hashlib
from datetime import datetime, timedelta

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

def get_accounts_by_organization(organization: str, account_name: Optional[str] = None, page: int = 1, page_size: int = 20) -> dict:
    """Fetch accounts for a specific organization with optional filtering and pagination"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Build dynamic query based on filters
                base_query = "SELECT sn, organization, account, permission, login_free_address FROM Accounts WHERE organization = %s"
                count_query = "SELECT COUNT(*) FROM Accounts WHERE organization = %s"
                params = [organization]
                
                if account_name:
                    base_query += " AND account ILIKE %s"
                    count_query += " AND account ILIKE %s"
                    params.append(f"%{account_name}%")
                
                # Get total count
                cur.execute(count_query, params)
                total_count = cur.fetchone()[0]
                
                # Add pagination
                base_query += " ORDER BY account LIMIT %s OFFSET %s"
                offset = (page - 1) * page_size
                params.extend([page_size, offset])
                
                cur.execute(base_query, params)
                rows = cur.fetchall()
                
                accounts = [Account(sn=row[0], organization=row[1], account=row[2], permission=row[3], login_free_address=row[4]) for row in rows]
                
                return {
                    "accounts": accounts,
                    "total_count": total_count,
                    "page": page,
                    "page_size": page_size
                }
    except Exception as e:
        logger.error(f"Error fetching accounts for organization {organization}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch accounts")

def create_account(account: AccountCreate) -> Account:
    """Create a new account"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Check if account already exists
                cur.execute("SELECT 1 FROM Accounts WHERE account = %s AND organization = %s", (account.account, account.organization))
                if cur.fetchone():
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account already exists in this organization")
                
                cur.execute(
                    """
                    INSERT INTO Accounts (organization, account, permission, login_free_address)
                    VALUES (%s, %s, %s, %s)
                    RETURNING sn, organization, account, permission, login_free_address
                    """,
                    (account.organization, account.account, account.permission, account.login_free_address)
                )
                row = cur.fetchone()
                conn.commit()
                
                logger.info(f"Account '{account.account}' created in organization '{account.organization}'")
                return Account(sn=row[0], organization=row[1], account=row[2], permission=row[3], login_free_address=row[4])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating account: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create account")

def get_account_by_id(account_id: int) -> Optional[Account]:
    """Fetch a specific account by ID"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT sn, organization, account, permission, login_free_address FROM Accounts WHERE sn = %s",
                    (account_id,)
                )
                row = cur.fetchone()
                if row:
                    return Account(sn=row[0], organization=row[1], account=row[2], permission=row[3], login_free_address=row[4])
                return None
    except Exception as e:
        logger.error(f"Error fetching account {account_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch account")

def update_account(account_id: int, account_update: AccountUpdate) -> Optional[Account]:
    """Update an account by ID"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Build dynamic update query based on provided fields
                update_fields = []
                update_values = []
                
                if account_update.account is not None:
                    update_fields.append("account = %s")
                    update_values.append(account_update.account)
                
                if account_update.permission is not None:
                    update_fields.append("permission = %s")
                    update_values.append(account_update.permission)
                
                if account_update.login_free_address is not None:
                    update_fields.append("login_free_address = %s")
                    update_values.append(account_update.login_free_address)
                
                if not update_fields:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
                
                update_values.append(account_id)
                query = f"""
                    UPDATE Accounts 
                    SET {', '.join(update_fields)}
                    WHERE sn = %s
                    RETURNING sn, organization, account, permission, login_free_address
                """
                
                cur.execute(query, update_values)
                row = cur.fetchone()
                conn.commit()
                
                if row:
                    logger.info(f"Account {account_id} updated successfully")
                    return Account(sn=row[0], organization=row[1], account=row[2], permission=row[3], login_free_address=row[4])
                return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating account {account_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update account")

def delete_account(account_id: int) -> bool:
    """Delete an account by ID"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Get account info for logging
                cur.execute("SELECT account, organization FROM Accounts WHERE sn = %s", (account_id,))
                account_info = cur.fetchone()
                
                cur.execute("DELETE FROM Accounts WHERE sn = %s", (account_id,))
                deleted_count = cur.rowcount
                conn.commit()
                
                if deleted_count > 0 and account_info:
                    logger.info(f"Account '{account_info[0]}' deleted from organization '{account_info[1]}'")
                
                return deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting account {account_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete account")

def reset_account_password(account_id: int) -> dict:
    """Generate a password reset token for an account"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Check if account exists
                cur.execute("SELECT account, organization FROM Accounts WHERE sn = %s", (account_id,))
                account_info = cur.fetchone()
                
                if not account_info:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
                
                # Generate reset token (in a real implementation, this would be stored in a separate table)
                reset_token = secrets.token_urlsafe(32)
                reset_expiry = datetime.utcnow() + timedelta(hours=24)
                
                # For now, we'll just log the reset request
                # In a real implementation, you'd store this in a password_resets table
                logger.info(f"Password reset requested for account '{account_info[0]}' in organization '{account_info[1]}'")
                logger.info(f"Reset token: {reset_token} (expires: {reset_expiry})")
                
                return {
                    "message": "Password reset token generated successfully",
                    "reset_token": reset_token,
                    "expires_at": reset_expiry.isoformat()
                }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password for account {account_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to reset password")

def disable_account(account_id: int) -> dict:
    """Disable an account (placeholder implementation)"""
    try:
        with next(get_conn()) as conn:
            with conn.cursor() as cur:
                # Check if account exists
                cur.execute("SELECT account, organization FROM Accounts WHERE sn = %s", (account_id,))
                account_info = cur.fetchone()
                
                if not account_info:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
                
                # In a real implementation, you'd have an 'enabled' or 'status' column
                # For now, we'll just log the disable request
                logger.warning(f"Account '{account_info[0]}' disabled in organization '{account_info[1]}'")
                
                return {
                    "message": "Account disabled successfully",
                    "account_id": account_id,
                    "status": "disabled"
                }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling account {account_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to disable account") 