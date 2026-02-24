from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from routes import bp_contact
from utils.emailer import send_contact_email
from extensions import limiter



@bp_contact.route("/contact/", methods=["GET", "POST"])
@login_required
@limiter.limit("10 per minute")
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        # Prefix subject with organisation for easier support triage
        org_name = getattr(getattr(current_user, "organisation", None), "name", "Unknown Org")
        if subject:
            subject = f"{org_name} | {subject}"
        else:
            subject = org_name

        # Basic validation
        errors = []
        if not name:
            errors.append("Name is required.")
        if not email or "@" not in email:
            errors.append("A valid email is required.")
        if not subject:
            errors.append("Subject is required.")
        if not message or len(message) < 10:
            errors.append("Message must be at least 10 characters.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("contact.html", form=request.form)

        try:
            send_contact_email(name=name, sender_email=email, subject=subject, message=message)
            flash("✅ Message sent successfully. We’ll get back to you soon.", "success")
            return redirect(url_for("contact.contact"))
        except Exception as e:
            print(f"[CONTACT EMAIL ERROR] {e}")
            flash("❌ Could not send message right now. Please try again later.", "error")
            return render_template("contact.html", form=request.form)

    return render_template("contact.html", form={})
