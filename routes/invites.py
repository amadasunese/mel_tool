import secrets
from datetime import datetime, timedelta

from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from routes import bp_invites
from extensions import db
from models import OrganisationInvite


def _org_admin_required():
    if not current_user.is_org_admin:
        abort(403)


@bp_invites.get("/")
@login_required
def list_invites():
    _org_admin_required()

    q = OrganisationInvite.query
    if not current_user.is_super_admin:
        q = q.filter(OrganisationInvite.organisation_id == current_user.organisation_id)

    invites = q.order_by(OrganisationInvite.created_at.desc()).all()
    return render_template("invites/list.html", invites=invites)


@bp_invites.route("/create", methods=["GET", "POST"])
@login_required
def create_invite():
    _org_admin_required()

    if request.method == "POST":
        role = request.form.get("role", "staff").strip()
        max_uses = request.form.get("max_uses", type=int) or 1
        expires_days = request.form.get("expires_days", type=int)

        if role not in ("staff", "org_admin"):
            flash("Invalid role.", "error")
            return render_template("invites/create.html", form=request.form)

        # org_admin cannot create org_admin invites if you want stricter control:
        # if not current_user.is_super_admin and role == "org_admin":
        #     role = "staff"

        expires_at = None
        if expires_days and expires_days > 0:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)

        code = secrets.token_urlsafe(24)

        inv = OrganisationInvite(
            organisation_id=current_user.organisation_id,
            code=code,
            role=role,
            max_uses=max_uses,
            uses=0,
            expires_at=expires_at,
            is_active=True,
        )
        db.session.add(inv)
        db.session.commit()

        flash("Invite created.", "success")
        return redirect(url_for("invites.list_invites"))

    return render_template("invites/create.html", form={})


@bp_invites.post("/<int:invite_id>/toggle")
@login_required
def toggle_invite(invite_id):
    _org_admin_required()

    inv = OrganisationInvite.query.get_or_404(invite_id)

    if not current_user.is_super_admin and inv.organisation_id != current_user.organisation_id:
        abort(403)

    inv.is_active = not inv.is_active
    db.session.commit()

    flash("Invite status updated.", "success")
    return redirect(url_for("invites.list_invites"))