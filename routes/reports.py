from datetime import datetime
from io import BytesIO
from flask import render_template, request, send_file
from sqlalchemy import func
from flask_login import login_required, current_user

from extensions import db
from models import Project, StrategicObjective, Indicator, Activity, ActivityAttendance
from utils.tenancy import org_scoped, require_org_access
from routes import bp_reports


def _parse_dates(start: str, end: str):
    start_d = datetime.strptime(start, "%Y-%m-%d").date()
    end_d = datetime.strptime(end, "%Y-%m-%d").date()
    return start_d, end_d


def _reach_for_activity_ids(activity_ids):
    if not activity_ids:
        return {"male": 0, "female": 0, "total": 0}

    row = (
        db.session.query(
            func.coalesce(func.sum(ActivityAttendance.male_count), 0).label("male"),
            func.coalesce(func.sum(ActivityAttendance.female_count), 0).label("female"),
        )
        .filter(ActivityAttendance.activity_id.in_(activity_ids))
        .one()
    )
    male = int(row.male or 0)
    female = int(row.female or 0)
    return {"male": male, "female": female, "total": male + female}


@bp_reports.get("/")
@login_required
def report_builder():
    projects = org_scoped(Project.query, Project.organisation_id).order_by(Project.created_at.desc()).all()
    return render_template("reports/home.html", projects=projects)


@bp_reports.get("/period")
@login_required
def period_report_form():
    projects = org_scoped(Project.query, Project.organisation_id).order_by(Project.created_at.desc()).all()
    return render_template("reports/period.html", projects=projects)

@bp_reports.post("/period")
@login_required
def period_report():
    project_id = request.form.get("project_id", type=int)
    start = request.form.get("start_date")
    end = request.form.get("end_date")

    project = Project.query.get_or_404(project_id)
    require_org_access(project.organisation_id)

    start_d, end_d = _parse_dates(start, end)

    sos = StrategicObjective.query.filter_by(project_id=project_id).order_by(StrategicObjective.id.asc()).all()

    indicators = (
        Indicator.query.join(StrategicObjective, Indicator.strategic_objective_id == StrategicObjective.id)
        .filter(StrategicObjective.project_id == project_id)
        .order_by(Indicator.id.asc())
        .all()
    )

    activities = (
        Activity.query.join(StrategicObjective, Activity.strategic_objective_id == StrategicObjective.id)
        .filter(StrategicObjective.project_id == project_id)
        .filter(Activity.activity_date >= start_d, Activity.activity_date <= end_d)
        .order_by(Activity.activity_date.asc(), Activity.id.asc())
        .all()
    )

    activity_ids = [a.id for a in activities]
    reach = _reach_for_activity_ids(activity_ids)

    return render_template(
        "reports/period_report.html",
        project=project,
        start_date=start_d,
        end_date=end_d,
        sos=sos,
        indicators=indicators,
        activities=activities,
        reach=reach,
    )


# @bp_reports.get('/reporting')
# def reporting():
#     report_year = Project.query.all()
#     # if 

    
    
#     return render_template('reports/report_year.html')
    