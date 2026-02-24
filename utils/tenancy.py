from flask import abort
from flask_login import current_user

def require_org_access(org_id: int):
    if current_user.is_super_admin:
        return
    if current_user.organisation_id != org_id:
        abort(403)

def org_scoped(query, org_field):
    """Apply organisation filter unless user is super_admin."""
    if current_user.is_super_admin:
        return query
    return query.filter(org_field == current_user.organisation_id)
