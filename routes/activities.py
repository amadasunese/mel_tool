from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, abort
from sqlalchemy import func
from flask_login import login_required, current_user

from extensions import db
from utils.tenancy import org_scoped, require_org_access
from models import StrategicObjective, Activity, Indicator, ActivityAttendance, Project
from routes import bp_activities


def activity_reach(activity_id: int):
    row = (db.session.query(
        func.coalesce(func.sum(ActivityAttendance.male_count), 0).label("male"),
        func.coalesce(func.sum(ActivityAttendance.female_count), 0).label("female"),
    ).filter(ActivityAttendance.activity_id == activity_id)).one()
    male = int(row.male or 0)
    female = int(row.female or 0)
    return male, female, male + female


@bp_activities.get("/")
@login_required
def list_activities():
    project_id = request.args.get("project_id", type=int)
    so_id = request.args.get("so_id", type=int)

    projects = org_scoped(Project.query, Project.organisation_id).order_by(Project.created_at.desc()).all()

    q = Activity.query
    if not current_user.is_super_admin:
        q = q.filter(Activity.organisation_id == current_user.organisation_id)

    sos = []
    if project_id:
        p = Project.query.get_or_404(project_id)
        require_org_access(p.organisation_id)
        sos = StrategicObjective.query.filter_by(project_id=project_id).order_by(StrategicObjective.id.desc()).all()
        so_ids = [s.id for s in sos]
        if so_ids:
            q = q.filter(Activity.strategic_objective_id.in_(so_ids))
        else:
            q = q.filter(Activity.id == -1)

    if so_id:
        so = StrategicObjective.query.get_or_404(so_id)
        p = Project.query.get_or_404(so.project_id)
        require_org_access(p.organisation_id)
        q = q.filter(Activity.strategic_objective_id == so_id)

    activities = q.order_by(Activity.activity_date.desc(), Activity.id.desc()).all()

    # attach reach summary
    reach_map = {}
    for a in activities:
        m, f, t = activity_reach(a.id)
        reach_map[a.id] = {"male": m, "female": f, "total": t}

    return render_template("activities/list.html", activities=activities, reach_map=reach_map, projects=projects, sos=sos, project_id=project_id, so_id=so_id)


@bp_activities.get("/create")
@login_required
def create_activity_form():
    projects = org_scoped(Project.query, Project.organisation_id).order_by(Project.created_at.desc()).all()
    indicators = Indicator.query.order_by(Indicator.id.desc()).limit(200).all()
    return render_template("activities/create.html", projects=projects, indicators=indicators, form={})


@bp_activities.post("/create")
@login_required
def create_activity():
    so_id = request.form.get("strategic_objective_id", type=int)
    indicator_id = request.form.get("indicator_id", type=int)
    activity_code = request.form.get("activity_code", "").strip() or None
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip() or None
    activity_date = request.form.get("activity_date") or None
    location = request.form.get("location", "").strip() or None

    so = StrategicObjective.query.get_or_404(so_id)
    p = Project.query.get_or_404(so.project_id)
    require_org_access(p.organisation_id)

    errors = []
    if not title:
        errors.append("Activity title is required.")
    if not activity_date:
        errors.append("Activity date is required.")
    if errors:
        for e in errors:
            flash(e, "error")
        projects = org_scoped(Project.query, Project.organisation_id).order_by(Project.created_at.desc()).all()
        indicators = Indicator.query.order_by(Indicator.id.desc()).limit(200).all()
        return render_template("activities/create.html", projects=projects, indicators=indicators, form=request.form)

    a = Activity(
        organisation_id=p.organisation_id,
        strategic_objective_id=so_id,
        indicator_id=indicator_id or None,
        activity_code=activity_code,
        title=title,
        description=description,
        activity_date=activity_date,
        location=location,
        created_at=datetime.utcnow(),
    )
    db.session.add(a)
    db.session.commit()

    flash("Activity created.", "success")
    return redirect(url_for("activities.list_activities", project_id=p.id, so_id=so_id))


@bp_activities.route("/<int:activity_id>/attendance", methods=["GET", "POST"])
@login_required
def attendance(activity_id):
    a = Activity.query.get_or_404(activity_id)
    require_org_access(a.organisation_id)

    if request.method == "POST":
        male = request.form.get("male_count", type=int) or 0
        female = request.form.get("female_count", type=int) or 0

        existing = ActivityAttendance.query.filter_by(activity_id=activity_id).first()
        if existing:
            existing.male_count = male
            existing.female_count = female
        else:
            db.session.add(ActivityAttendance(activity_id=activity_id, male_count=male, female_count=female))
        db.session.commit()

        flash("Attendance saved.", "success")
        return redirect(url_for("activities.list_activities"))

    existing = ActivityAttendance.query.filter_by(activity_id=activity_id).first()
    return render_template("activities/attendance.html", activity=a, attendance=existing)
