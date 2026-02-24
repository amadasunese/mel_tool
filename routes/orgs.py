from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from routes import bp_orgs
from extensions import db
from models import Organisation


def _super_admin_required():
    if not current_user.is_super_admin:
        abort(403)


@bp_orgs.get("/")
@login_required
def list_orgs():
    _super_admin_required()
    orgs = Organisation.query.order_by(Organisation.created_at.desc()).all()
    return render_template("orgs/list.html", orgs=orgs)


@bp_orgs.route("/create", methods=["GET", "POST"])
@login_required
def create_org():
    _super_admin_required()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        slug = request.form.get("slug", "").strip().lower()

        errors = []
        if not name:
            errors.append("Organisation name is required.")
        if not slug:
            errors.append("Slug is required.")
        if Organisation.query.filter_by(slug=slug).first():
            errors.append("Slug already exists.")
        if Organisation.query.filter_by(name=name).first():
            errors.append("Organisation name already exists.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("orgs/create.html", form=request.form)

        org = Organisation(name=name, slug=slug, is_active=True)
        db.session.add(org)
        db.session.commit()

        flash("Organisation created.", "success")
        return redirect(url_for("orgs.list_orgs"))

    return render_template("orgs/create.html", form={})


@bp_orgs.post("/<int:org_id>/toggle")
@login_required
def toggle_org(org_id):
    _super_admin_required()
    org = Organisation.query.get_or_404(org_id)
    org.is_active = not org.is_active
    db.session.commit()
    flash("Organisation status updated.", "success")
    return redirect(url_for("orgs.list_orgs"))
