from datetime import datetime, date
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from extensions import db
from utils.tenancy import org_scoped, require_org_access
from models import Project
from routes import bp_projects




@bp_projects.get("/")
@login_required
def list_projects():
    projects = org_scoped(Project.query, Project.organisation_id).order_by(Project.created_at.desc()).all()
    return render_template("projects/list.html", projects=projects)


@bp_projects.get("/create")
@login_required
def create_project_form():
    return render_template("projects/create.html", form={})


@bp_projects.post("/create")
@login_required
def create_project():
    name = request.form.get("name", "").strip()
    goal = request.form.get("goal", "").strip()
    donor = request.form.get("donor", "").strip() or None
    location = request.form.get("location", "").strip() or None
    start_date = request.form.get("start_date") or None
    end_date = request.form.get("end_date") or None

    errors = []
    if not name:
        errors.append("Project name is required.")
    if not goal:
        errors.append("Project goal is required.")

    if errors:
        for e in errors:
            flash(e, "error")
        return render_template("projects/create.html", form=request.form)
    
    def parse_date(v):
        return datetime.strptime(v, "%Y-%m-%d").date() if v else None

    p = Project(
        name=name,
        goal=goal,
        donor=donor,
        location=location,
        start_date=parse_date(request.form.get("start_date")),
        end_date=parse_date(request.form.get("end_date")),
        organisation_id=current_user.organisation_id,
        created_at=datetime.utcnow(),
    )
    db.session.add(p)
    db.session.commit()

    flash("Project created successfully.", "success")
    return redirect(url_for("projects.list_projects"))


@bp_projects.get("/<int:project_id>/edit")
@login_required
def edit_project_form(project_id):
    p = Project.query.get_or_404(project_id)
    require_org_access(p.organisation_id)
    return render_template("projects/edit.html", project=p)


@bp_projects.post("/<int:project_id>/edit")
@login_required
def edit_project(project_id):
    p = Project.query.get_or_404(project_id)
    require_org_access(p.organisation_id)

    p.name = request.form.get("name", "").strip()
    p.goal = request.form.get("goal", "").strip()
    p.donor = request.form.get("donor", "").strip() or None
    p.location = request.form.get("location", "").strip() or None
    p.start_date = request.form.get("start_date") or None
    p.end_date = request.form.get("end_date") or None

    db.session.commit()
    flash("Project updated.", "success")
    return redirect(url_for("projects.list_projects"))


@bp_projects.post("/<int:project_id>/delete")
@login_required
def delete_project(project_id):
    p = Project.query.get_or_404(project_id)
    require_org_access(p.organisation_id)
    db.session.delete(p)
    db.session.commit()
    flash("Project deleted.", "success")
    return redirect(url_for("projects.list_projects"))
