from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


def utc_now():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash = db.Column(db.String(255), nullable=False)

    college = db.Column(db.String(150))
    branch = db.Column(db.String(100))
    semester = db.Column(db.Integer)
    cgpa = db.Column(db.Float)
    target_career = db.Column(db.String(150))

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )

    skills = db.relationship(
        "UserSkill",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    analyses = db.relationship(
        "SkillAnalysis",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "college": self.college,
            "branch": self.branch,
            "semester": self.semester,
            "cgpa": self.cgpa,
            "target_career": self.target_career,
        }


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    category = db.Column(db.String(100))

    users = db.relationship(
        "UserSkill",
        back_populates="skill",
        cascade="all, delete-orphan"
    )


class UserSkill(db.Model):
    __tablename__ = "user_skills"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    skill_id = db.Column(
        db.Integer,
        db.ForeignKey("skills.id"),
        nullable=False
    )

    proficiency = db.Column(
        db.String(30),
        nullable=False,
        default="Beginner"
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )

    user = db.relationship("User", back_populates="skills")
    skill = db.relationship("Skill", back_populates="users")

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "skill_id",
            name="unique_user_skill"
        ),
    )


class SkillAnalysis(db.Model):
    __tablename__ = "skill_analyses"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    target_career = db.Column(
        db.String(150),
        nullable=False
    )

    current_skills = db.Column(db.Text)
    missing_skills = db.Column(db.Text)
    recommendations = db.Column(db.Text)

    readiness_score = db.Column(
        db.Float,
        nullable=False,
        default=0.0
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )

    user = db.relationship("User", back_populates="analyses")