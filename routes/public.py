from flask import render_template
from routes import bp_public

@bp_public.get("/privacy")
def privacy():
    return render_template("privacy.html")

@bp_public.get("/terms")
def terms():
    return render_template("terms.html")