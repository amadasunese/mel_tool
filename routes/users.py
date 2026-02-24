from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from routes import bp_users
from extensions import db
from models import User, Organisation


def _org_admin_required():
    if not current_user.is_org_admin:
        abort(403)


@bp_users.get("/")
@login_required
def list_users():
    _org_admin_required()

    q = User.query
    if not current_user.is_super_admin:
        q = q.filter(User.organisation_id == current_user.organisation_id)

    users = q.order_by(User.created_at.desc()).all()
    org = Organisation.query.get(current_user.organisation_id)
    return render_template("users/list.html", users=users, org=org)


@bp_users.route("/create", methods=["GET", "POST"])
@login_required
def create_user():
    _org_admin_required()

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "staff").strip()
        password = request.form.get("password", "")

        # super_admin can select organisation, org_admin cannot
        org_id = request.form.get("organisation_id", type=int)
        if not current_user.is_super_admin:
            org_id = current_user.organisation_id
            if role == "super_admin":
                role = "org_admin"  # cannot create super admin

        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if not email or "@" not in email:
            errors.append("Valid email is required.")
        if role not in ("staff", "org_admin", "super_admin"):
            errors.append("Invalid role.")
        if not password or len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if not org_id:
            errors.append("Organisation is required.")
        else:
            org = Organisation.query.get(org_id)
            if not org:
                errors.append("Organisation not found.")
            elif not org.is_active:
                errors.append("Organisation is disabled.")

        if User.query.filter_by(email=email).first():
            errors.append("A user with this email already exists.")

        if errors:
            for e in errors:
                flash(e, "error")
            orgs = Organisation.query.order_by(Organisation.name.asc()).all() if current_user.is_super_admin else []
            return render_template("users/create.html", form=request.form, orgs=orgs)

        u = User(full_name=full_name, email=email, role=role, organisation_id=org_id, is_active=True)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()

        flash("User created successfully.", "success")
        return redirect(url_for("users.list_users"))

    orgs = Organisation.query.order_by(Organisation.name.asc()).all() if current_user.is_super_admin else []
    return render_template("users/create.html", form={}, orgs=orgs)


@bp_users.post("/<int:user_id>/toggle")
@login_required
def toggle_user(user_id):
    _org_admin_required()

    u = User.query.get_or_404(user_id)

    # org admins can only manage users in same org
    if not current_user.is_super_admin and u.organisation_id != current_user.organisation_id:
        abort(403)

    if u.id == current_user.id:
        flash("You cannot disable your own account.", "error")
        return redirect(url_for("users.list_users"))

    u.is_active = not u.is_active
    db.session.commit()
    flash("User status updated.", "success")
    return redirect(url_for("users.list_users"))


@bp_users.route("/<int:user_id>/reset-password", methods=["GET", "POST"])
@login_required
def reset_password(user_id):
    _org_admin_required()

    u = User.query.get_or_404(user_id)
    if not current_user.is_super_admin and u.organisation_id != current_user.organisation_id:
        abort(403)

    if request.method == "POST":
        password = request.form.get("password", "")
        if not password or len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("users/reset_password.html", user=u)

        u.set_password(password)
        db.session.commit()
        flash("Password reset successfully.", "success")
        return redirect(url_for("users.list_users"))

    return render_template("users/reset_password.html", user=u)
