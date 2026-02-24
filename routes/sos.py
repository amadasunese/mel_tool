from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from extensions import db
from utils.tenancy import org_scoped, require_org_access
from models import Project, StrategicObjective
from routes import bp_sos


@bp_sos.get("/")
@login_required
def list_sos():
    project_id = request.args.get("project_id", type=int)

    projects = org_scoped(Project.query, Project.organisation_id).order_by(Project.created_at.desc()).all()

    q = StrategicObjective.query.join(Project, StrategicObjective.project_id == Project.id)
    if not current_user.is_super_admin:
        q = q.filter(Project.organisation_id == current_user.organisation_id)

    if project_id:
        # ensure project is accessible
        p = Project.query.get_or_404(project_id)
        require_org_access(p.organisation_id)
        q = q.filter(StrategicObjective.project_id == project_id)

    sos = q.order_by(StrategicObjective.id.desc()).all()
    return render_template("sos/list.html", sos=sos, projects=projects, project_id=project_id)


@bp_sos.get("/create")
@login_required
def create_so_form():
    projects = org_scoped(Project.query, Project.organisation_id).order_by(Project.created_at.desc()).all()
    return render_template("sos/create.html", projects=projects, form={})


@bp_sos.post("/create")
@login_required
def create_so():
    project_id = request.form.get("project_id", type=int)
    so_code = request.form.get("so_code", "").strip()
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip() or None

    p = Project.query.get_or_404(project_id)
    require_org_access(p.organisation_id)

    errors = []
    if not so_code:
        errors.append("SO code is required (e.g., SO1).")
    if not title:
        errors.append("SO title is required.")
    if errors:
        for e in errors:
            flash(e, "error")
        projects = org_scoped(Project.query, Project.organisation_id).order_by(Project.created_at.desc()).all()
        return render_template("sos/create.html", projects=projects, form=request.form)

    so = StrategicObjective(project_id=project_id, so_code=so_code, title=title, description=description)
    db.session.add(so)
    db.session.commit()

    flash("Strategic Objective created.", "success")
    return redirect(url_for("sos.list_sos", project_id=project_id))
