from app.db.connection import get_conn
from app.schemas.roles import Role, Organization
from typing import List


def get_organizations() -> List[Organization]:
    with next(get_conn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, organization_name, title FROM Organizations")
            rows = cur.fetchall()
            return [Organization(id=row[0], organization_name=row[1], title=row[2]) for row in rows]


def get_roles_by_organization(organization: str) -> List[Role]:
    with next(get_conn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT sn, organization, name, color FROM Roles WHERE organization = %s", (organization,))
            rows = cur.fetchall()
            return [Role(sn=row[0], organization=row[1], name=row[2], color=row[3]) for row in rows] 