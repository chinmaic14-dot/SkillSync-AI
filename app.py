import markdown

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

from config import Config
from models import db, User, SkillAnalysis
from ai_service import get_ai_response


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # ---------------- MARKDOWN FILTER ----------------

    @app.template_filter("markdown_to_html")
    def markdown_to_html(value):
        return markdown.markdown(
            value or "",
            extensions=["extra", "nl2br"],
        )

    # ---------------- DATABASE INITIALIZATION ----------------

    with app.app_context():
        db.create_all()

    # ---------------- HOME PAGE ----------------

    @app.route("/")
    def home():
        return render_template("index.html")

    # ---------------- HEALTH CHECK ----------------

    @app.route("/health")
    def health():
        return {"status": "healthy"}, 200

    # ---------------- STUDENT CATEGORIES ----------------

    @app.route("/student-categories")
    def student_categories():
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))

        return render_template("student_categories.html")

    # ---------------- CATEGORY 01: SKILLED BUT STUCK ----------------

    @app.route("/skilled-stuck", methods=["GET", "POST"])
    def skilled_stuck():
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))

        user = db.session.get(User, session["user_id"])

        if user is None:
            session.clear()
            flash("Your session has expired. Please log in again.", "error")
            return redirect(url_for("login"))

        if request.method == "POST":
            target_career = request.form.get(
                "target_career", ""
            ).strip()

            current_skills = request.form.get(
                "current_skills", ""
            ).strip()

            skill_level = request.form.get(
                "skill_level", ""
            ).strip()

            career_challenge = request.form.get(
                "career_challenge", ""
            ).strip()

            fields = [
                target_career,
                current_skills,
                skill_level,
                career_challenge,
            ]

            if not all(fields):
                flash("Please complete all required fields.", "error")
                return render_template("skilled_stuck.html")

            if any(len(value) > 3000 for value in fields):
                flash(
                    "Please keep each response under 3000 characters.",
                    "error",
                )
                return render_template("skilled_stuck.html")

            # Build the personalized AI prompt.
            prompt = f"""
You are SkillSync AI, a career skill-gap assistant for college students.

Analyze the student's self-reported information.

STUDENT PROFILE
Name: {user.full_name}
College: {user.college or "Not provided"}
Branch: {user.branch or "Not provided"}
Semester: {user.semester if user.semester is not None else "Not provided"}
CGPA: {user.cgpa if user.cgpa is not None else "Not provided"}

TARGET CAREER
{target_career}

CURRENT SKILLS
{current_skills}

SELF-REPORTED SKILL LEVEL
{skill_level}

BIGGEST CHALLENGE
{career_challenge}

Write a personalized report in Markdown with these sections:

## 1. Career Readiness Overview
Assess readiness based only on the supplied information.
Do not claim that skills have been objectively tested.

## 2. Existing Strengths
List the skills the student has mentioned.

## 3. Potential Skill Gaps
Identify relevant skills that were not mentioned or may need practice.
Do not assume an unmentioned skill is definitely absent.

## 4. Priority Learning Roadmap
Organize recommendations into foundations, practical projects,
and career preparation.

## 5. Four-Week Learning Plan
Give realistic tasks for each week.

## 6. Project Suggestions
Recommend two relevant projects and explain what each demonstrates.

## 7. Learning Resources
Recommend reputable websites and accurate official URLs.
Do not invent courses, certifications, or links.

## 8. Five Next Actions
Give five concrete actions the student can start taking.

Be encouraging, practical, specific, and honest.
Do not guarantee employment, placements, or interviews.
Clearly distinguish recommendations from verified facts.
"""

            # ---------------- OPENROUTER AI ----------------

            ai_result = get_ai_response(prompt)

            if not ai_result.get("success"):
                flash(
                    ai_result.get(
                        "message",
                        "Unable to generate your AI report. Please try again.",
                    ),
                    "error",
                )
                return render_template("skilled_stuck.html")

            report = ai_result.get("message", "").strip()

            if not report:
                flash(
                    "The AI returned an empty report. Please try again.",
                    "error",
                )
                return render_template("skilled_stuck.html")

            # ---------------- SAVE REPORT TO DATABASE ----------------
            # IMPORTANT: target_career is required by the database.
            # Passing it here fixes the NOT NULL constraint error.

            analysis = SkillAnalysis(
                user_id=user.id,
                target_career=target_career,
                current_skills=current_skills,
                missing_skills=(
                    "Potential gaps are described in the AI-generated report."
                ),
                recommendations=report,
                readiness_score=None,
            )

            user.target_career = target_career

            try:
                db.session.add(analysis)
                db.session.commit()

            except Exception:
                db.session.rollback()
                app.logger.exception(
                    "Unable to save skill analysis."
                )
                flash(
                    "Your AI report was generated, but we couldn't save it. "
                    "Please try again.",
                    "error",
                )
                return render_template("skilled_stuck.html")

            flash(
                "Your personalized AI skill-gap report is ready!",
                "success",
            )

            return redirect(
                url_for(
                    "analysis_result",
                    analysis_id=analysis.id,
                )
            )

        return render_template("skilled_stuck.html")

    # ---------------- ANALYSIS RESULT ----------------

    @app.route("/analysis-result/<int:analysis_id>")
    def analysis_result(analysis_id):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))

        analysis = db.session.get(SkillAnalysis, analysis_id)

        # Students can view only their own reports.
        if (
            analysis is None
            or analysis.user_id != session["user_id"]
        ):
            flash("Analysis not found.", "error")
            return redirect(url_for("dashboard"))

        return render_template(
            "analysis_result.html",
            analysis=analysis,
        )

    # ---------------- SIGN UP ----------------

    @app.route("/sign-up", methods=["GET", "POST"])
    def sign_up():
        if request.method == "POST":
            full_name = request.form.get(
                "full_name", ""
            ).strip()

            email = request.form.get(
                "email", ""
            ).strip().lower()

            college = request.form.get(
                "college", ""
            ).strip()

            branch = request.form.get(
                "branch", ""
            ).strip()

            semester_value = request.form.get(
                "semester", ""
            ).strip()

            password = request.form.get("password", "")
            confirm_password = request.form.get(
                "confirm_password", ""
            )

            if not full_name or not email or not password:
                flash(
                    "Please complete all required fields.",
                    "error",
                )
                return render_template("sign_up.html")

            if len(password) < 8:
                flash(
                    "Your password must contain at least 8 characters.",
                    "error",
                )
                return render_template("sign_up.html")

            if password != confirm_password:
                flash(
                    "The passwords do not match.",
                    "error",
                )
                return render_template("sign_up.html")

            if User.query.filter_by(email=email).first():
                flash(
                    "An account with this email already exists.",
                    "error",
                )
                return render_template("sign_up.html")

            semester = None

            if semester_value:
                try:
                    semester = int(semester_value)

                    if semester not in range(1, 9):
                        raise ValueError

                except ValueError:
                    flash(
                        "Please select a valid semester.",
                        "error",
                    )
                    return render_template("sign_up.html")

            user = User(
                full_name=full_name,
                email=email,
                college=college or None,
                branch=branch or None,
                semester=semester,
            )

            user.set_password(password)

            try:
                db.session.add(user)
                db.session.commit()

            except Exception:
                db.session.rollback()
                app.logger.exception(
                    "Unable to create user account."
                )
                flash(
                    "We couldn't create your account. Please try again.",
                    "error",
                )
                return render_template("sign_up.html")

            flash(
                "Account created successfully. Please log in.",
                "success",
            )

            return redirect(url_for("login"))

        return render_template("sign_up.html")

    # ---------------- LOGIN ----------------

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get(
                "email", ""
            ).strip().lower()

            password = request.form.get("password", "")

            user = User.query.filter_by(email=email).first()

            if user is None or not user.check_password(password):
                flash(
                    "Invalid email or password.",
                    "error",
                )
                return render_template("login.html")

            session.clear()
            session["user_id"] = user.id
            session["user_name"] = user.full_name

            flash(
                "Welcome back, " + user.full_name + "!",
                "success",
            )

            return redirect(url_for("dashboard"))

        return render_template("login.html")

    # ---------------- DASHBOARD ----------------

    @app.route("/dashboard")
    def dashboard():
        if "user_id" not in session:
            flash(
                "Please log in to access your dashboard.",
                "error",
            )
            return redirect(url_for("login"))

        user = db.session.get(User, session["user_id"])

        if user is None:
            session.clear()
            flash(
                "Your session has expired. Please log in again.",
                "error",
            )
            return redirect(url_for("login"))

        return render_template(
            "dashboard.html",
            user=user,
        )

    # ---------------- LOGOUT ----------------

    @app.route("/logout")
    def logout():
        session.clear()
        flash(
            "You have been logged out.",
            "success",
        )
        return redirect(url_for("home"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)