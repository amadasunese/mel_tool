from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from extensions import db

# class Organisation(db.Model):
#     __tablename__ = "organisations"

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(180), unique=True, nullable=False)
#     slug = db.Column(db.String(80), unique=True, nullable=False)  # e.g. gpi-edo
#     is_active = db.Column(db.Boolean, default=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     organisation = db.relationship("Organisation", backref="projects")

#     users = db.relationship("User", backref="organisation", lazy=True)


class Organisation(db.Model):
    __tablename__ = "organisations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), unique=True, nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Correct relationships:
    users = db.relationship("User", back_populates="organisation", lazy=True)
    projects = db.relationship("Project", back_populates="organisation", lazy=True, cascade="all, delete-orphan")
    activities = db.relationship("Activity", back_populates="organisation", lazy=True, cascade="all, delete-orphan")
    invites = db.relationship("OrganisationInvite", back_populates="organisation", lazy=True, cascade="all, delete-orphan")
    
    
# class User(db.Model, UserMixin):
#     __tablename__ = "users"

#     id = db.Column(db.Integer, primary_key=True)

#     organisation_id = db.Column(
#         db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True
#     )

#     full_name = db.Column(db.String(120), nullable=False)
#     email = db.Column(db.String(180), unique=True, index=True, nullable=False)

#     password_hash = db.Column(db.String(255), nullable=False)

#     role = db.Column(db.String(20), default="staff")  # staff | org_admin | super_admin
#     is_active = db.Column(db.Boolean, default=True)

#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     organisation = db.relationship("Organisation", backref="projects")
#     last_login_at = db.Column(db.DateTime)

#     email_verified = db.Column(db.Boolean, default=False)
#     email_verified_at = db.Column(db.DateTime, nullable=True)

#     terms_accepted_at = db.Column(db.DateTime, nullable=True)
#     privacy_accepted_at = db.Column(db.DateTime, nullable=True)

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)

    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), default="staff")
    is_active = db.Column(db.Boolean, default=True)

    last_login_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    email_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime, nullable=True)
    terms_accepted_at = db.Column(db.DateTime, nullable=True)
    privacy_accepted_at = db.Column(db.DateTime, nullable=True)

    organisation = db.relationship("Organisation", back_populates="users")
    
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_super_admin(self) -> bool:
        return self.role == "super_admin"

    @property
    def is_org_admin(self) -> bool:
        return self.role in ("org_admin", "super_admin")


# class Project(db.Model):
#     __tablename__ = "projects"
#     id = db.Column(db.Integer, primary_key=True)

#     organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)
#     name = db.Column(db.String(200), nullable=False)
#     goal = db.Column(db.Text, nullable=False)

#     donor = db.Column(db.String(200))
#     location = db.Column(db.String(200))

#     start_date = db.Column(db.Date)
#     end_date = db.Column(db.Date)

#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     organisation = db.relationship("Organisation", backref="projects")

#     strategic_objectives = db.relationship(
#         "StrategicObjective",
#         backref="project",
#         lazy=True,
#         cascade="all, delete-orphan"
#     )


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)

    name = db.Column(db.String(200), nullable=False)
    goal = db.Column(db.Text, nullable=False)

    donor = db.Column(db.String(200))
    location = db.Column(db.String(200))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    organisation = db.relationship("Organisation", back_populates="projects")

    strategic_objectives = db.relationship(
        "StrategicObjective",
        backref="project",
        lazy=True,
        cascade="all, delete-orphan"
    )
    
# class StrategicObjective(db.Model):
#     __tablename__ = "strategic_objectives"
#     id = db.Column(db.Integer, primary_key=True)

#     project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)

#     so_code = db.Column(db.String(20), nullable=False)   # e.g., SO1
#     title = db.Column(db.String(250), nullable=False)
#     description = db.Column(db.Text)

#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     # organisation = db.relationship("Organisation", backref="projects")

#     indicators = db.relationship(
#         "Indicator",
#         backref="strategic_objective",
#         lazy=True,
#         cascade="all, delete-orphan"
#     )

#     activities = db.relationship(
#         "Activity",
#         backref="strategic_objective",
#         lazy=True,
#         cascade="all, delete-orphan"
#     )

#     __table_args__ = (
#         db.UniqueConstraint("project_id", "so_code", name="uq_project_so_code"),
#     )

class StrategicObjective(db.Model):
    __tablename__ = "strategic_objectives"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)

    so_code = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    indicators = db.relationship("Indicator", backref="strategic_objective", lazy=True, cascade="all, delete-orphan")
    activities = db.relationship("Activity", backref="strategic_objective", lazy=True, cascade="all, delete-orphan")

    __table_args__ = (db.UniqueConstraint("project_id", "so_code", name="uq_project_so_code"),)

class Indicator(db.Model):
    __tablename__ = "indicators"
    id = db.Column(db.Integer, primary_key=True)

    strategic_objective_id = db.Column(
        db.Integer, db.ForeignKey("strategic_objectives.id"), nullable=False
    )

    indicator_code = db.Column(db.String(40), nullable=False)  # e.g., SO1_IND1
    statement = db.Column(db.Text, nullable=False)

    indicator_type = db.Column(db.String(20))   # Output|Outcome
    unit = db.Column(db.String(50))            # "# persons", "%", "# sessions"
    gender_disaggregation = db.Column(db.Boolean, default=True)

    baseline = db.Column(db.Float, default=0)
    target = db.Column(db.Float)  # optional at MVP

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # organisation = db.relationship("Organisation", backref="projects")

    __table_args__ = (
        db.UniqueConstraint(
            "strategic_objective_id",
            "indicator_code",
            name="uq_so_indicator_code"
        ),
    )


# class Activity(db.Model):
#     __tablename__ = "activities"
#     id = db.Column(db.Integer, primary_key=True)

#     organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)
#     strategic_objective_id = db.Column(
#         db.Integer, db.ForeignKey("strategic_objectives.id"), nullable=False
#     )

#     # optional: link activity to a specific indicator
#     indicator_id = db.Column(db.Integer, db.ForeignKey("indicators.id"))

#     activity_code = db.Column(db.String(30))  # e.g., A1.1.1
#     title = db.Column(db.String(250), nullable=False)
#     description = db.Column(db.Text)

#     activity_date = db.Column(db.Date, nullable=False, default=date.today)
#     location = db.Column(db.String(200))

#     status = db.Column(db.String(20), default="planned")  # planned|ongoing|completed
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     organisation = db.relationship("Organisation", backref="projects")

#     indicator = db.relationship(
#         "Indicator",
#         backref=db.backref("activities", lazy=True)
#     )

#     attendance = db.relationship(
#         "ActivityAttendance",
#         backref="activity",
#         lazy=True,
#         cascade="all, delete-orphan"
#     )


class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)

    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)
    strategic_objective_id = db.Column(db.Integer, db.ForeignKey("strategic_objectives.id"), nullable=False)

    indicator_id = db.Column(db.Integer, db.ForeignKey("indicators.id"))

    activity_code = db.Column(db.String(30))
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text)

    activity_date = db.Column(db.Date, nullable=False, default=date.today)
    location = db.Column(db.String(200))

    status = db.Column(db.String(20), default="planned")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    organisation = db.relationship("Organisation", back_populates="activities")

    indicator = db.relationship("Indicator", backref=db.backref("activities", lazy=True))

    attendance = db.relationship("ActivityAttendance", backref="activity", lazy=True, cascade="all, delete-orphan")
    
    

# class ActivityAttendance(db.Model):
#     __tablename__ = "activity_attendance"
#     id = db.Column(db.Integer, primary_key=True)

#     activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"), nullable=False)

#     male_count = db.Column(db.Integer, default=0)
#     female_count = db.Column(db.Integer, default=0)

#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     organisation = db.relationship("Organisation", backref="projects")

#     @property
#     def total(self):
#         return (self.male_count or 0) + (self.female_count or 0)

#     __table_args__ = (
#         db.UniqueConstraint("activity_id", name="uq_attendance_activity"),
#     )


class ActivityAttendance(db.Model):
    __tablename__ = "activity_attendance"

    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"), nullable=False)

    male_count = db.Column(db.Integer, default=0)
    female_count = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def total(self):
        return (self.male_count or 0) + (self.female_count or 0)

    __table_args__ = (db.UniqueConstraint("activity_id", name="uq_attendance_activity"),)
    

# class OrganisationInvite(db.Model):
#     __tablename__ = "organisation_invites"

#     id = db.Column(db.Integer, primary_key=True)

#     organisation_id = db.Column(
#         db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True
#     )

#     code = db.Column(db.String(64), unique=True, index=True, nullable=False)  # random token

#     role = db.Column(db.String(20), default="staff")  # staff | org_admin
#     max_uses = db.Column(db.Integer, default=1)
#     uses = db.Column(db.Integer, default=0)

#     expires_at = db.Column(db.DateTime, nullable=True)
#     is_active = db.Column(db.Boolean, default=True)

#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     organisation = db.relationship("Organisation", backref="invites")


class OrganisationInvite(db.Model):
    __tablename__ = "organisation_invites"

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)

    code = db.Column(db.String(64), unique=True, index=True, nullable=False)
    role = db.Column(db.String(20), default="staff")
    max_uses = db.Column(db.Integer, default=1)
    uses = db.Column(db.Integer, default=0)

    expires_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    organisation = db.relationship("Organisation", back_populates="invites")
    
    @property
    def is_expired(self) -> bool:
        return self.expires_at is not None and datetime.utcnow() > self.expires_at

    @property
    def is_usable(self) -> bool:
        if not self.is_active:
            return False
        if self.is_expired:
            return False
        if self.max_uses is not None and self.uses >= self.max_uses:
            return False
        return True