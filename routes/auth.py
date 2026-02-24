from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user


from routes import bp_auth
from extensions import db, limiter
from models import User
from flask_login import login_user, current_user
from models import Organisation, User, OrganisationInvite
from werkzeug.security import generate_password_hash
import re

from utils.tokens import make_token, read_token
from utils.auth_email import send_verification_email

from utils.auth_email import send_password_reset_email

from extensions import limiter





@bp_auth.get("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard_home"))
    return render_template("auth/register.html", form={})


# @bp_auth.post("/register")
# def register_post():
#     # Org fields
#     org_name = request.form.get("org_name", "").strip()
#     org_slug = request.form.get("org_slug", "").strip().lower()

#     # User fields
#     full_name = request.form.get("full_name", "").strip()
#     email = request.form.get("email", "").strip().lower()
#     password = request.form.get("password", "")
#     confirm = request.form.get("confirm_password", "")

#     errors = []

#     # Validate org
#     if not org_name:
#         errors.append("Organisation name is required.")
#     if not org_slug:
#         errors.append("Organisation slug is required.")
#     if org_slug and not re.match(r"^[a-z0-9-]+$", org_slug):
#         errors.append("Slug can only contain lowercase letters, numbers, and hyphens (e.g. gpi-edo).")
#     if Organisation.query.filter_by(slug=org_slug).first():
#         errors.append("That organisation slug is already taken.")

#     # Validate user
#     if not full_name:
#         errors.append("Full name is required.")
#     if not email or "@" not in email:
#         errors.append("A valid email is required.")
#     if User.query.filter_by(email=email).first():
#         errors.append("A user with this email already exists.")
#     if not password or len(password) < 8:
#         errors.append("Password must be at least 8 characters.")
#     if password != confirm:
#         errors.append("Passwords do not match.")

#     if errors:
#         for e in errors:
#             flash(e, "error")
#         return render_template("auth/register.html", form=request.form)

#     # Create org + org_admin user
#     org = Organisation(name=org_name, slug=org_slug, is_active=True)
#     db.session.add(org)
#     db.session.commit()

#     user = User(
#         organisation_id=org.id,
#         full_name=full_name,
#         email=email,
#         role="org_admin",
#         is_active=True
#     )
#     user.set_password(password)
#     db.session.add(user)
#     db.session.commit()

#     login_user(user)
#     flash("✅ Registration successful. Welcome!", "success")
#     return redirect(url_for("dashboard.dashboard_home"))


import re
from models import Organisation, User, OrganisationInvite


# @bp_auth.post("/register")
# @limiter.limit("5 per minute")
# def register_post():
    
#     # Honeypot
#     website = request.form.get("website", "").strip()
#     if website:
#         flash("Registration submitted.", "success")
#         return redirect(url_for("auth.login"))

#     # Terms acceptance
#     if request.form.get("accept_terms") != "on":
#         flash("You must accept the Terms and Privacy Policy.", "error")
#         return render_template("auth/register.html", form=request.form)


#     mode = request.form.get("mode", "create")  # create | join

#     full_name = request.form.get("full_name", "").strip()
#     email = request.form.get("email", "").strip().lower()
#     password = request.form.get("password", "")
#     confirm = request.form.get("confirm_password", "")

#     errors = []

#     # common user checks
#     if not full_name:
#         errors.append("Full name is required.")
#     if not email or "@" not in email:
#         errors.append("A valid email is required.")
#     if User.query.filter_by(email=email).first():
#         errors.append("A user with this email already exists.")
#     if not password or len(password) < 8:
#         errors.append("Password must be at least 8 characters.")
#     if password != confirm:
#         errors.append("Passwords do not match.")

#     if mode == "join":
#         invite_code = request.form.get("invite_code", "").strip()

#         if not invite_code:
#             errors.append("Invite code is required to join an organisation.")
#         invite = OrganisationInvite.query.filter_by(code=invite_code).first()
#         if not invite:
#             errors.append("Invite code is invalid.")
#         elif not invite.is_usable:
#             errors.append("Invite code is expired, used up, or disabled.")

#         if errors:
#             for e in errors:
#                 flash(e, "error")
#             return render_template("auth/register.html", form=request.form)

#         # Create user in that org with invite role
#         user = User(
#             organisation_id=invite.organisation_id,
#             full_name=full_name,
#             email=email,
#             role=invite.role,   # staff/org_admin
#             is_active=True
#         )
#         user.set_password(password)
#         db.session.add(user)

#         invite.uses += 1
#         db.session.commit()

#         login_user(user)
#         flash("✅ Account created. You’ve joined the organisation.", "success")
#         return redirect(url_for("dashboard.dashboard_home"))

#     # else: mode == "create"
#     org_name = request.form.get("org_name", "").strip()
#     org_slug = request.form.get("org_slug", "").strip().lower()

#     if not org_name:
#         errors.append("Organisation name is required.")
#     if not org_slug:
#         errors.append("Organisation slug is required.")
#     if org_slug and not re.match(r"^[a-z0-9-]+$", org_slug):
#         errors.append("Slug can only contain lowercase letters, numbers, and hyphens (e.g. gpi-edo).")
#     if Organisation.query.filter_by(slug=org_slug).first():
#         errors.append("That organisation slug is already taken.")

#     if errors:
#         for e in errors:
#             flash(e, "error")
#         return render_template("auth/register.html", form=request.form)

#     org = Organisation(name=org_name, slug=org_slug, is_active=True)
#     db.session.add(org)
#     db.session.commit()

#     user = User(
#         organisation_id=org.id,
#         full_name=full_name,
#         email=email,
#         role="org_admin",
#         is_active=True
#     )
#     user.set_password(password)
#     db.session.add(user)
#     db.session.commit()

#     login_user(user)
#     flash("✅ Organisation created and account registered.", "success")
#     return redirect(url_for("dashboard.dashboard_home"))






@bp_auth.post("/register")
@limiter.limit("5 per minute")
def register_post():
    # Honeypot (anti-bot)
    website = request.form.get("website", "").strip()
    if website:
        flash("Registration submitted.", "success")
        return redirect(url_for("auth.login"))

    # Terms acceptance
    if request.form.get("accept_terms") != "on":
        flash("You must accept the Terms and Privacy Policy.", "error")
        return render_template("auth/register.html", form=request.form)

    mode = request.form.get("mode", "create")  # create | join

    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")

    errors = []

    # Common user checks
    if not full_name:
        errors.append("Full name is required.")
    if not email or "@" not in email:
        errors.append("A valid email is required.")
    if User.query.filter_by(email=email).first():
        errors.append("A user with this email already exists.")
    if not password or len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    if password != confirm:
        errors.append("Passwords do not match.")

    now = datetime.utcnow()

    if mode == "join":
        invite_code = request.form.get("invite_code", "").strip()

        if not invite_code:
            errors.append("Invite code is required to join an organisation.")

        invite = OrganisationInvite.query.filter_by(code=invite_code).first()
        if not invite:
            errors.append("Invite code is invalid.")
        elif not invite.is_usable:
            errors.append("Invite code is expired, used up, or disabled.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("auth/register.html", form=request.form)

        # Create user + consume invite in ONE commit
        user = User(
            organisation_id=invite.organisation_id,
            full_name=full_name,
            email=email,
            role=invite.role,     # staff/org_admin
            is_active=True,
            email_verified=False,
            terms_accepted_at=now,
            privacy_accepted_at=now,
        )
        user.set_password(password)
        db.session.add(user)

        invite.uses += 1
        db.session.commit()

        # Email verification
        token = make_token({"purpose": "verify", "user_id": user.id})
        try:
            send_verification_email(user.email, token)
        except Exception as e:
            # Don't block registration if email fails; just inform user/admin
            print("[VERIFY EMAIL ERROR]", e)

        flash("✅ Account created. Please check your email to verify your account.", "success")
        return redirect(url_for("auth.verify_notice"))

    # else: mode == "create"
    org_name = request.form.get("org_name", "").strip()
    org_slug = request.form.get("org_slug", "").strip().lower()

    if not org_name:
        errors.append("Organisation name is required.")
    if not org_slug:
        errors.append("Organisation slug is required.")
    if org_slug and not re.match(r"^[a-z0-9-]+$", org_slug):
        errors.append("Slug can only contain lowercase letters, numbers, and hyphens (e.g. gpi-edo).")
    if Organisation.query.filter_by(slug=org_slug).first():
        errors.append("That organisation slug is already taken.")

    if errors:
        for e in errors:
            flash(e, "error")
        return render_template("auth/register.html", form=request.form)

    org = Organisation(name=org_name, slug=org_slug, is_active=True)
    db.session.add(org)
    db.session.commit()

    user = User(
        organisation_id=org.id,
        full_name=full_name,
        email=email,
        role="org_admin",
        is_active=True,
        email_verified=False,
        terms_accepted_at=now,
        privacy_accepted_at=now,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Email verification
    token = make_token({"purpose": "verify", "user_id": user.id})
    try:
        send_verification_email(user.email, token)
    except Exception as e:
        print("[VERIFY EMAIL ERROR]", e)

    flash("✅ Organisation created. Please verify your email to activate your account.", "success")
    return redirect(url_for("auth.verify_notice"))



@bp_auth.get("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard_home"))
    return render_template("auth/login.html")


# @bp_auth.post("/login")
# @limiter.limit("10 per minute")
# def login_post():
#     email = request.form.get("email", "").strip().lower()
#     password = request.form.get("password", "")

#     user = User.query.filter_by(email=email).first()

#     if not user or not user.check_password(password):
#         flash("Invalid email or password.", "error")
#         return redirect(url_for("auth.login"))

#     if not user.is_active:
#         flash("Your account is disabled. Contact your organisation admin.", "error")
#         return redirect(url_for("auth.login"))

#     if not user.organisation or not user.organisation.is_active:
#         flash("Your organisation is disabled. Contact support.", "error")
#         return redirect(url_for("auth.login"))

#     user.last_login_at = datetime.utcnow()
#     db.session.commit()

#     login_user(user)
#     flash("Welcome back!", "success")
#     return redirect(url_for("dashboard.dashboard_home"))


@bp_auth.post("/login")
@limiter.limit("10 per minute")
def login_post():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        flash("Invalid email or password.", "error")
        return redirect(url_for("auth.login"))

    if not user.is_active:
        flash("Your account is disabled. Contact your organisation admin.", "error")
        return redirect(url_for("auth.login"))

    if not user.organisation or not user.organisation.is_active:
        flash("Your organisation is disabled. Contact support.", "error")
        return redirect(url_for("auth.login"))

    ENFORCE_VERIFICATION = current_app.config.get("ENFORCE_EMAIL_VERIFICATION", True)
    if ENFORCE_VERIFICATION and not user.email_verified:
        flash("Please verify your email to continue.", "error")
        return redirect(url_for("auth.verify_notice", email=user.email))

    user.last_login_at = datetime.utcnow()
    db.session.commit()

    login_user(user)
    flash("Welcome back!", "success")
    return redirect(url_for("dashboard.dashboard_home"))


# @bp_auth.post("/login")
# @limiter.limit("10 per minute")
# def login_post():
#     email = request.form.get("email", "").strip().lower()
#     password = request.form.get("password", "")

#     user = User.query.filter_by(email=email).first()

#     if not user or not user.check_password(password):
#         flash("Invalid email or password.", "error")
#         return redirect(url_for("auth.login"))

#     if not user.is_active:
#         flash("Your account is disabled. Contact your organisation admin.", "error")
#         return redirect(url_for("auth.login"))

#     if not user.organisation or not user.organisation.is_active:
#         flash("Your organisation is disabled. Contact support.", "error")
#         return redirect(url_for("auth.login"))

#     ENFORCE_VERIFICATION = current_app.config.get("ENFORCE_EMAIL_VERIFICATION", True)
#     if ENFORCE_VERIFICATION and not user.email_verified:
#         flash("Please verify your email before logging in. Check your inbox.", "error")
#         return redirect(url_for("auth.login"))

#     user.last_login_at = datetime.utcnow()
#     db.session.commit()

#     login_user(user)
#     flash("Welcome back!", "success")
#     return redirect(url_for("dashboard.dashboard_home"))



@bp_auth.get("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    # return redirect(url_for("auth.login"))
    return render_template("landing.html")


# @bp_auth.get("/verify-notice")
# def verify_notice():
#     return render_template("auth/verify_notice.html")


@bp_auth.get("/verify-notice")
def verify_notice():
    email = request.args.get("email", "")
    return render_template("auth/verify_notice.html", email=email)




@bp_auth.get("/verify/<token>")
def verify_email(token):
    data = read_token(token, max_age_seconds=60 * 60 * 24)  # 24 hours
    if not data or data.get("purpose") != "verify":
        flash("Verification link is invalid or expired.", "error")
        return redirect(url_for("auth.login"))

    user = User.query.get(data.get("user_id"))
    if not user:
        flash("Account not found.", "error")
        return redirect(url_for("auth.login"))

    if user.email_verified:
        flash("Email already verified. You can login.", "success")
        return redirect(url_for("auth.login"))

    user.email_verified = True
    user.email_verified_at = datetime.utcnow()
    db.session.commit()

    flash("✅ Email verified successfully. You can now login.", "success")
    return redirect(url_for("auth.login"))



# @bp_auth.post("/resend-verification")
# @limiter.limit("5 per minute")
# def resend_verification():
#     email = request.form.get("email", "").strip().lower()
#     user = User.query.filter_by(email=email).first()

#     # Always respond same to avoid leaking accounts
#     if user and not user.email_verified and user.is_active:
#         token = make_token({"purpose": "verify", "user_id": user.id})
#         send_verification_email(user.email, token)

#     flash("If that email exists, a verification link has been sent.", "success")
#     return redirect(url_for("auth.login"))


@bp_auth.post("/resend-verification")
@limiter.limit("3 per minute")
def resend_verification():
    email = request.form.get("email", "").strip().lower()
    user = User.query.filter_by(email=email).first()

    # Always respond same → prevents account enumeration
    if user and not user.email_verified and user.is_active:
        token = make_token({"purpose": "verify", "user_id": user.id})

        try:
            send_verification_email(user.email, token)
        except Exception as e:
            print("[RESEND VERIFY ERROR]", e)

    flash("If that email exists, a confirmation link has been sent.", "success")
    return redirect(url_for("auth.login"))


# @bp_auth.get("/verify/<token>")
# def verify_email(token):
#     data = read_token(token, max_age_seconds=60 * 60 * 24)  # 24 hours
#     if not data or data.get("purpose") != "verify":
#         flash("Verification link is invalid or expired.", "error")
#         return redirect(url_for("auth.login"))

#     user = User.query.get(data.get("user_id"))
#     if not user:
#         flash("Account not found.", "error")
#         return redirect(url_for("auth.login"))

#     if user.email_verified:
#         flash("Email already verified. You can login.", "success")
#         return redirect(url_for("auth.login"))

#     user.email_verified = True
#     user.email_verified_at = datetime.utcnow()
#     db.session.commit()

#     flash("✅ Email verified successfully. You can now login.", "success")
#     return redirect(url_for("auth.login"))



@bp_auth.get("/forgot-password")
def forgot_password():
    return render_template("auth/forgot_password.html")



# @bp_auth.post("/forgot-password")
# @limiter.limit("5 per minute")
# def forgot_password_post():
#     email = request.form.get("email", "").strip().lower()
#     user = User.query.filter_by(email=email).first()

#     # Always respond same (no account enumeration)
#     if user and user.is_active:
#         token = make_token({"purpose": "reset", "user_id": user.id})
#         send_password_reset_email(user.email, token)

#     flash("If that email exists, a password reset link has been sent.", "success")
#     return redirect(url_for("auth.login"))


@bp_auth.post("/forgot-password")
@limiter.limit("5 per minute")
def forgot_password_post():
    email = request.form.get("email", "").strip().lower()
    user = User.query.filter_by(email=email).first()

    if user and user.is_active:
        token = make_token({"purpose": "reset", "user_id": user.id})

        try:
            send_password_reset_email(user.email, token)
        except Exception as e:
            print("[RESET EMAIL ERROR]", e)

    flash("If that email exists, a password reset link has been sent.", "success")
    return redirect(url_for("auth.login"))



@bp_auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    data = read_token(token, max_age_seconds=60 * 60)  # 1 hour expiry

    if not data or data.get("purpose") != "reset":
        flash("Reset link is invalid or expired.", "error")
        return redirect(url_for("auth.forgot_password"))

    user = User.query.get(data.get("user_id"))
    if not user or not user.is_active:
        flash("Account not found.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return render_template("auth/reset_password.html", token=token)

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("auth/reset_password.html", token=token)

        user.set_password(password)
        db.session.commit()

        flash("✅ Password reset successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token)

# @bp_auth.route("/reset-password/<token>", methods=["GET", "POST"])
# def reset_password(token):
#     data = read_token(token, max_age_seconds=60 * 60)  # 1 hour
#     if not data or data.get("purpose") != "reset":
#         flash("Reset link is invalid or expired.", "error")
#         return redirect(url_for("auth.forgot_password"))

#     user = User.query.get(data.get("user_id"))
#     if not user or not user.is_active:
#         flash("Account not found.", "error")
#         return redirect(url_for("auth.forgot_password"))

#     if request.method == "POST":
#         password = request.form.get("password", "")
#         confirm = request.form.get("confirm_password", "")

#         if not password or len(password) < 8:
#             flash("Password must be at least 8 characters.", "error")
#             return render_template("auth/reset_password.html", token=token)

#         if password != confirm:
#             flash("Passwords do not match.", "error")
#             return render_template("auth/reset_password.html", token=token)

#         user.set_password(password)
#         db.session.commit()

#         flash("✅ Password changed successfully. Please login.", "success")
#         return redirect(url_for("auth.login"))

#     return render_template("auth/reset_password.html", token=token)