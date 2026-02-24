from flask import Flask, redirect, url_for
from config import Config
from extensions import db, migrate, csrf, login_manager, limiter

from routes import (
    bp_dashboard, bp_projects, bp_sos, bp_indicators, bp_activities, bp_reports,
    bp_testscore, bp_contact, bp_auth, bp_users, bp_orgs, bp_invites, bp_public
)

# Import route modules so handlers register on blueprints (required)
from routes import dashboard as _dashboard_routes  # noqa: F401
from routes import projects as _projects_routes    # noqa: F401
from routes import sos as _sos_routes              # noqa: F401
from routes import indicators as _ind_routes       # noqa: F401
from routes import activities as _act_routes       # noqa: F401
from routes import reports as _rep_routes          # noqa: F401
from routes import testscore as _testscore_routes  # noqa: F401
from routes import contact as _contact_routes      # noqa: F401
from routes import auth as _auth_routes            # noqa: F401
from routes import users as _users_routes          # noqa: F401
from routes import orgs as _orgs_routes            # noqa: F401
from utils import auth as _login_loader            # noqa: F401
from routes import invites as _invites_routes  # noqa: F401
from routes import public as _public_routes  # noqa: F401




def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    app.register_blueprint(bp_dashboard)
    app.register_blueprint(bp_projects)
    app.register_blueprint(bp_sos)
    app.register_blueprint(bp_indicators)
    app.register_blueprint(bp_activities)
    app.register_blueprint(bp_reports)
    app.register_blueprint(bp_testscore)
    app.register_blueprint(bp_contact)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_users)
    app.register_blueprint(bp_orgs)
    app.register_blueprint(bp_invites)
    app.register_blueprint(bp_public)

    # @app.get("/")
    # def index():
    #     return redirect(url_for("dashboard.dashboard_home"))





    from flask_login import current_user
    from flask import render_template

    @app.get("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.dashboard_home"))
        return render_template("landing.html")


    from flask_limiter.errors import RateLimitExceeded

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(e):
        return render_template("errors/429.html"), 429


    return app


if __name__ == "__main__":
    create_app().run(debug=True)
