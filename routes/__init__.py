from flask import Blueprint

bp_dashboard  = Blueprint("dashboard", __name__, url_prefix="/dashboard")

bp_projects   = Blueprint("projects", __name__, url_prefix="/projects")
bp_sos        = Blueprint("sos", __name__, url_prefix="/sos")
bp_indicators = Blueprint("indicators", __name__, url_prefix="/indicators")
bp_activities = Blueprint("activities", __name__, url_prefix="/activities")
bp_reports    = Blueprint("reports", __name__, url_prefix="/reports")
bp_testscore  = Blueprint("testscore", __name__, url_prefix="/testscore")
bp_contact    = Blueprint("contact", __name__, url_prefix="")


bp_auth  = Blueprint("auth", __name__, url_prefix="/auth")
bp_users = Blueprint("users", __name__, url_prefix="/users")
bp_orgs  = Blueprint("orgs", __name__, url_prefix="/orgs")

bp_invites = Blueprint("invites", __name__, url_prefix="/invites")

bp_public = Blueprint("public", __name__)