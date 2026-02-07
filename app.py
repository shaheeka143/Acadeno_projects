import os
from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from ml.matcher import match_jobs
from utils.resume_parser import extract_resume_text

app = Flask(__name__)
app.secret_key = "acadeno_secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

os.makedirs("uploads", exist_ok=True)

db = SQLAlchemy(app)

# ---------------- MODELS ---------------- #

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="Student")
    status = db.Column(db.String(50), default="Active")

class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    resume_text = db.Column(db.Text)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    skills = db.Column(db.String(300))
    company = db.Column(db.String(120))
    location = db.Column(db.String(120))
    apply_link = db.Column(db.String(300))

# ---------------- ROUTES ---------------- #

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            session["user_id"] = user.id
            session["user_email"] = user.email
            session["user_role"] = user.role
            session["user_status"] = user.status
            return redirect("/dashboard")

        flash("Invalid credentials")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # check existing user
        existing_user = User.query.filter_by(email=request.form["email"]).first()
        if existing_user:
            flash("Account already exists. Please login.")
            return redirect("/")

        resume = request.files.get("resume")
        if not resume or not resume.filename.endswith(".pdf"):
            flash("Upload a valid PDF resume")
            return redirect("/register")

        filename = secure_filename(resume.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        resume.save(path)

        resume_text = extract_resume_text(path)
        if resume_text == "":
            flash("Could not read resume (must be text-based PDF)")
            return redirect("/register")

        user = User(
            email=request.form["email"],
            password=generate_password_hash(request.form["password"])
        )
        db.session.add(user)
        db.session.commit()

        profile = StudentProfile(
            user_id=user.id,
            resume_text=resume_text
        )
        db.session.add(profile)
        db.session.commit()

        flash("Account created successfully. Please login.")
        return redirect("/")

    return render_template("register.html")



@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    profile = StudentProfile.query.filter_by(user_id=session["user_id"]).first()
    jobs = Job.query.all()

    matches = match_jobs(profile.resume_text, jobs)

    return render_template(
        "dashboard.html",
        matches=matches,
        total_matches=len(matches),
        top_match=max([m["score"] for m in matches], default=0),
        user_email=session["user_email"],
        user_role=session["user_role"],
        user_status=session["user_status"]
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
