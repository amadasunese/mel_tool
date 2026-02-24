from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from extensions import db
from utils.tenancy import org_scoped, require_org_access
from models import StrategicObjective, Indicator, Project
from routes import bp_indicators


@bp_indicators.get("/")
@login_required
def list_indicators():
    project_id = request.args.get("project_id", type=int)
    so_id = request.args.get("so_id", type=int)

    projects = org_scoped(Project.query, Project.organisation_id).order_by(Project.created_at.desc()).all()

    q = Indicator.query.join(StrategicObjective, Indicator.strategic_objective_id == StrategicObjective.id)                       .join(Project, StrategicObjective.project_id == Project.id)
    if not current_user.is_super_admin:
        q = q.filter(Project.organisation_id == current_user.organisation_id)

    sos = []
    if project_id:
        p = Project.query.get_or_404(project_id)
        require_org_access(p.organisation_id)
        sos = StrategicObjective.query.filter_by(project_id=project_id).order_by(StrategicObjective.id.desc()).all()
        q = q.filter(Project.id == project_id)
    else:
        # show sos for first project maybe
        pass

    if so_id:
        # ensure SO belongs to accessible project
        so = StrategicObjective.query.get_or_404(so_id)
        p = Project.query.get_or_404(so.project_id)
        require_org_access(p.organisation_id)
        q = q.filter(Indicator.strategic_objective_id == so_id)

    indicators = q.order_by(Indicator.id.desc()).all()
    return render_template("indicators/list.html", indicators=indicators, projects=projects, sos=sos, project_id=project_id, so_id=so_id)


@bp_indicators.get("/create")
@login_required
def create_indicator_form():
    projects = org_scoped(Project.query, Project.organisation_id).order_by(Project.created_at.desc()).all()
    return render_template("indicators/create.html", projects=projects, form={})


@bp_indicators.post("/create")
@login_required
def create_indicator():
    so_id = request.form.get("strategic_objective_id", type=int)
    indicator_code = request.form.get("indicator_code", "").strip()
    statement = request.form.get("statement", "").strip()
    indicator_type = request.form.get("indicator_type", "").strip() or None
    unit = request.form.get("unit", "").strip() or None
    gender_disaggregation = request.form.get("gender_disaggregation") == "on"

    so = StrategicObjective.query.get_or_404(so_id)
    p = Project.query.get_or_404(so.project_id)
    require_org_access(p.organisation_id)

    errors = []
    if not indicator_code:
        errors.append("Indicator code is required.")
    if not statement:
        errors.append("Indicator statement is required.")
    if errors:
        for e in errors:
            flash(e, "error")
        projects = org_scoped(Project.query, Project.organisation_id).order_by(Project.created_at.desc()).all()
        return render_template("indicators/create.html", projects=projects, form=request.form)

    ind = Indicator(
        strategic_objective_id=so_id,
        indicator_code=indicator_code,
        statement=statement,
        indicator_type=indicator_type,
        unit=unit,
        gender_disaggregation=gender_disaggregation,
    )
    db.session.add(ind)
    db.session.commit()

    flash("Indicator created.", "success")
    return redirect(url_for("indicators.list_indicators", project_id=p.id, so_id=so_id))
