from datetime import date
from sqlalchemy import func
from flask import render_template
from flask_login import login_required, current_user

from extensions import db
from utils.tenancy import org_scoped
from models import (
    Project,
    StrategicObjective,
    Indicator,
    Activity,
    ActivityAttendance
)
from routes import bp_dashboard


def _total_reach():
    q = db.session.query(
        func.coalesce(func.sum(ActivityAttendance.male_count), 0).label("male"),
        func.coalesce(func.sum(ActivityAttendance.female_count), 0).label("female"),
    ).join(Activity, ActivityAttendance.activity_id == Activity.id)

    if not current_user.is_super_admin:
        q = q.filter(Activity.organisation_id == current_user.organisation_id)

    row = q.one()
    male = int(row.male or 0)
    female = int(row.female or 0)
    return male, female, male + female


@bp_dashboard.get("/")
@login_required
def dashboard_home():
    # Projects
    q_projects = org_scoped(Project.query, Project.organisation_id)
    total_projects = q_projects.count()

    # Strategic Objectives (join back to project)
    q_sos = StrategicObjective.query.join(Project, StrategicObjective.project_id == Project.id)
    if not current_user.is_super_admin:
        q_sos = q_sos.filter(Project.organisation_id == current_user.organisation_id)
    total_sos = q_sos.count()

    # Indicators
    q_inds = Indicator.query.join(StrategicObjective, Indicator.strategic_objective_id == StrategicObjective.id)                            .join(Project, StrategicObjective.project_id == Project.id)
    if not current_user.is_super_admin:
        q_inds = q_inds.filter(Project.organisation_id == current_user.organisation_id)
    total_indicators = q_inds.count()

    # Activities
    q_acts = Activity.query
    if not current_user.is_super_admin:
        q_acts = q_acts.filter(Activity.organisation_id == current_user.organisation_id)
    total_activities = q_acts.count()
    
    
    # --- ADD THIS SECTION START ---
    # Query to count activities by status
    status_query = db.session.query(
        Activity.status, func.count(Activity.id)
    ).group_by(Activity.status)
    
    if not current_user.is_super_admin:
        status_query = status_query.filter(Activity.organisation_id == current_user.organisation_id)
    
    status_results = dict(status_query.all())
    
    # Ensure all keys exist so Jinja doesn't crash if a status has 0 activities
    status_counts = {
        "planned": status_results.get("planned", 0),
        "ongoing": status_results.get("ongoing", 0),
        "completed": status_results.get("completed", 0)
    }

    # Simple completion rate calculation
    completion_rate = 0
    if total_activities > 0:
        completion_rate = round((status_counts["completed"] / total_activities) * 100)
    # --- ADD THIS SECTION END ---
    

    male, female, total_reach = _total_reach()

    recent_activities = (
        q_acts.order_by(Activity.activity_date.desc(), Activity.id.desc())
        .limit(10).all()
    )

    recent_projects = (
        q_projects.order_by(Project.created_at.desc())
        .limit(6).all()
    )

    return render_template(
        "dashboard/index.html",
        stats={
            "projects": total_projects,
            "sos": total_sos,
            "indicators": total_indicators,
            "activities": total_activities,
            "completion_rate": completion_rate, # Added this
            "status_counts": status_counts,     # Added this
            "male": male,
            "female": female,
            "total_reach": total_reach,
        },
        
        # Ensure 'charts' is defined even if empty to avoid more UndefinedErrors
        charts={
            "so_labels": [], "so_male": [], "so_female": [], "so_total": [],
            "monthly_labels": [], "monthly_total": []
        },
        
        recent_activities=recent_activities,
        recent_projects=recent_projects,
        today=date.today(),
    )
