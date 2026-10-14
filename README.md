SkillSync AI

AI-Powered Skill Gap Analysis and Personalized Career Learning Platform

SkillSync AI is a web-based platform designed to help college students understand their existing skills, identify potential skill gaps for their target careers, and receive personalized learning guidance using Artificial Intelligence.

Project Overview

Many students struggle to determine which skills they need for their desired careers. Generic learning platforms often provide broad learning paths without considering each student's current knowledge, career interests, or individual challenges.

SkillSync AI aims to make career preparation more structured by combining AI-generated skill-gap guidance with personalized learning recommendations.

Key Features

- AI Skill Gap Analysis: Generates personalized reports based on a student's target career, existing skills, self-reported skill level, and learning challenges.
- Personalized Learning Roadmap: Provides a suggested four-week learning plan.
- Project Recommendations: Suggests practical projects relevant to the student's career interests.
- Learning Resources: Recommends learning websites and resources.
- Student Authentication: Provides account registration and login functionality.
- Personalized Student Dashboard: Gives logged-in students access to the platform's features.
- Report Storage: Stores generated skill-analysis reports in an SQLite database.
- Dark-Themed User Interface: Uses a dark navy background, cyan accents, and modern card-based layouts.

Technology Stack

Component| Technology
Backend| Python, Flask
Frontend| HTML, CSS, Jinja2
Database| SQLite
Database Integration| Flask-SQLAlchemy
AI Integration| OpenRouter API
Configuration| python-dotenv
Report Formatting| Python-Markdown
Deployment Support| Gunicorn

How It Works

1. A student creates an account and logs in.
2. The student selects the skill-gap analysis category.
3. The student enters their target career, current skills, skill level, and biggest challenge.
4. SkillSync sends the information to an AI model through the OpenRouter API.
5. The AI generates a personalized career-readiness overview, potential skill gaps, learning roadmap, project suggestions, and recommended resources.
6. The application saves the report in the database and displays it to the student.

Note: Reports are AI-generated guidance based on student-provided information. They do not represent objectively verified skill assessments or guaranteed placement outcomes.

Project Structure

SkillSync/
├── app.py
├── config.py
├── models.py
├── ai_service.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── instance/
├── uploads/
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── sign_up.html
    ├── dashboard.html
    ├── student_categories.html
    ├── skilled_stuck.html
    └── analysis_result.html

Additional templates and folders may be added as development continues. The ".env" file and local database files should not be committed to a public repository.

Installation and Setup

Prerequisites

- Python 3.10 or later
- Git
- A GitHub account
- An OpenRouter account and API key for AI functionality

1. Clone the Repository

git clone YOUR_GITHUB_REPOSITORY_URL
cd SkillSync

Replace "YOUR_GITHUB_REPOSITORY_URL" with your repository's actual URL.

2. Create a Virtual Environment

python -m venv .venv

Activate it on Windows PowerShell:

.\.venv\Scripts\Activate.ps1

3. Install Dependencies

pip install -r requirements.txt

4. Configure Environment Variables

Create a local ".env" file based on ".env.example".

SECRET_KEY=replace_with_a_random_secret_key
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openrouter/free
DATABASE_URL=sqlite:///skillsync.db

Generate a Flask secret key using:

python -c "import secrets; print(secrets.token_hex(32))"

Get an OpenRouter API key from:

https://openrouter.ai/settings/keys

Browse available models at:

https://openrouter.ai/models

The configured model must be available to your account and support the API request used by the application. Free-model availability and rate limits may vary.

Security: Never commit ".env" or expose your API key in source code, screenshots, or public repositories.

5. Run the Application

python app.py

Open the following URL in your browser:

http://127.0.0.1:5000

Current Development Status

The current implementation includes the main homepage, student authentication, dashboard, student categories, the first skill-gap analysis category, OpenRouter integration, and AI report storage/display flow.

Further development can extend the remaining categories, learning planner, student collaboration features, analysis history, and deployment configuration.

Future Enhancements

- Additional personalized learning categories
- Progress tracking and analysis history
- Course and certification recommendations
- Peer-to-peer skill exchange
- Learning planner and study schedules
- Career preparation resources
- Production deployment and security hardening

Responsible Use

SkillSync AI provides educational guidance and career-development suggestions. Recommendations should be reviewed by students and may require independent verification. The platform does not guarantee jobs, internships, certifications, or placement results.

Project Purpose

SkillSync AI aims to help students make better-informed learning decisions, build practical skills, and prepare more systematically for their desired careers.