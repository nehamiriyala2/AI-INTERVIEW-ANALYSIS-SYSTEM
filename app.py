from vision_analysis import analyze_video

from flask import Flask, render_template, request, redirect, session, jsonify


from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3, os, random
import smtplib
from email.message import EmailMessage
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ================= CONFIG =================
ADMIN_EMAIL = "nehamiriyala2005@gmail.com"
ADMIN_PASSWORD = "12345"

app = Flask(__name__)
app.secret_key = "interview_ai_secret"

DB = "interview_ai.db"
UPLOAD = "static/uploads"
os.makedirs(UPLOAD, exist_ok=True)

# Load AI Model Once
model = SentenceTransformer("all-MiniLM-L6-v2")

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()

    # USERS TABLE
    db.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user'
    )
    """)

    # REPORTS TABLE
   # REPORTS TABLE
    db.execute("""
    CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        score INTEGER,
        semantic_score INTEGER,
        similarity REAL,
        vision_score INTEGER,
        confidence TEXT,
        emotion TEXT,
        words INTEGER,
        feedback TEXT,
        time TEXT,
        video TEXT
)
""")
    # OTP TABLE
    db.execute("""
    CREATE TABLE IF NOT EXISTS otp_verification(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        otp TEXT,
        created_at TEXT
    )
    """)

    # FEEDBACK TABLE (ONLY ONCE)
    db.execute("""
    CREATE TABLE IF NOT EXISTS candidate_feedback(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        usability INTEGER,
        clarity TEXT,
        comfort INTEGER,
        fairness TEXT,
        technical TEXT,
        sentiment INTEGER,
        submitted_at TEXT
    )
    """)

    # CREATE ADMIN IF NOT EXISTS
    admin = db.execute(
        "SELECT * FROM users WHERE email=?",
        (ADMIN_EMAIL,)
    ).fetchone()

    if not admin:
        db.execute("""
        INSERT INTO users (name, email, password, role)
        VALUES (?, ?, ?, ?)
        """, (
            "Admin",
            ADMIN_EMAIL,
            generate_password_hash(ADMIN_PASSWORD),
            "admin"
        ))

    db.commit()
    db.close()
# ================= AUTH =================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        db = get_db()
        db.execute("""
        INSERT INTO users (name, email, password, role)
        VALUES (?, ?, ?, ?)
        """, (name, email, password, "user"))
        db.commit()
        db.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= LOGIN =================

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=? AND role='user'",
            (email,)
        ).fetchone()
        db.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["role"] = "user"
            return redirect("/dashboard")

        return render_template("login.html", error="Invalid User Credentials")

    return render_template("login.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    # If already logged in as admin → go to dashboard
    if session.get("role") == "admin":
        return redirect("/admin/dashboard")

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        admin = db.execute(
            "SELECT * FROM users WHERE email=? AND role='admin'",
            (email,)
        ).fetchone()
        db.close()

        if admin and check_password_hash(admin["password"], password):
            session.clear()
            session["user_id"] = admin["id"]
            session["role"] = "admin"
            return redirect("/admin/dashboard")

        return render_template("admin_login.html", error="Invalid Credentials")

    return render_template("admin_login.html")
# ================= DASHBOARD =================

@app.route("/dashboard")
def dashboard():
    if session.get("role") != "user":
        return redirect("/login")

    db = get_db()

    rows = db.execute("""
        SELECT score, emotion
        FROM reports
        WHERE user_id = ?
        ORDER BY id ASC
    """, (session["user_id"],)).fetchall()

    db.close()

    total = len(rows)
    last_score = rows[-1]["score"] if total > 0 else 0
    avg_score = round(
        sum(r["score"] for r in rows) / total, 1
    ) if total > 0 else 0

    completion_rate = 100 if total > 0 else 0

    scores = [r["score"] for r in rows]
    emotions = [r["emotion"] for r in rows]

    return render_template(
        "dashboard.html",
        total=total,
        last_score=last_score,
        avg_score=avg_score,
        completion_rate=completion_rate,
        scores=scores,
        emotions=emotions
    )


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/")


# ================= INTERVIEW =================

@app.route("/interview")
def interview():
    if session.get("role") != "user":
        return redirect("/login")
    return render_template("interview.html")
# ================= SAVE RESULT =================

@app.route("/save_result", methods=["POST"])
def save_result():
    if session.get("role") != "user":
        return jsonify({"error": "unauthorized"}), 401

    print("FORM DATA:", request.form)
    print("FILES:", request.files)

    raw_question = request.form.get("question", "")
    answer = request.form.get("answer", "").strip()
    technology = (request.form.get("technology") or "").lower()

    question = raw_question.lower().strip()

    # ================= REMOVE FILLER WORDS =================
    filler_words = ["hmm", "uh", "aaa", "umm", "like"]
    original_words = answer.lower().split()

    clean_words = [word for word in original_words if word not in filler_words]
    clean_answer = " ".join(clean_words)

    filler_count = len(original_words) - len(clean_words)
    words = len(clean_words)

    # ================= REFERENCE ANSWERS =================
    reference_answers = {
    # ===== GENERAL =====
         "tell me about yourself":
        "Introduce your name, education background, technical skills, key projects, internship experience and career goals clearly.",

        "what are your strengths":
        "Discuss your key strengths such as problem solving, communication, leadership, adaptability and give examples.",
  
        "what are your weaknesses":
        "Mention a real weakness and explain how you are actively improving it professionally.",

        "how do you handle pressure":
        "Explain how you stay calm, prioritize tasks, and maintain focus under pressure situations.",

        "where do you see yourself in 5 years":
        "Talk about career growth, skill development, leadership goals and contribution to organization.",

        # ===== JAVA =====
        "what is oop in java":
        "Object Oriented Programming includes encapsulation, inheritance, polymorphism and abstraction.",

        "explain inheritance in java":
        "Inheritance in Java allows a class to acquire properties and behavior of another class using extends keyword.",

        "what is jvm":
        "JVM is Java Virtual Machine that executes Java bytecode and provides platform independence.",

        # ===== PYTHON =====
       "what are python features":
        "Python features include simplicity, readability, dynamic typing, object oriented support and large libraries.",

        "what is list comprehension":
        "List comprehension in Python provides a concise way to create lists using a single line loop expression."
}

    reference_text = ""
    for key in reference_answers:
        if key in question:
            reference_text = reference_answers[key]
            break

    if reference_text == "":
        reference_text = "Technical explanation about " + technology

    # ================= SEMANTIC SIMILARITY =================
    embeddings = model.encode([reference_text, clean_answer])
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    similarity = max(0, similarity)

    semantic_score = round(similarity * 100)
    semantic_score = max(0, min(semantic_score, 100))

    # ================= LENGTH SCORE =================
    if words < 10:
        length_score = 30
    elif words < 25:
        length_score = 60
    elif words < 50:
        length_score = 80
    else:
        length_score = 100

    # ================= VIDEO SAVE =================
    video = request.files.get("video")
    filename = None

    if video:
        filename = f"{session['user_id']}_{int(datetime.now().timestamp())}.webm"
        video.save(os.path.join(UPLOAD, filename))

    # ================= VISION SCORE =================
    vision_score_percent = 0
    detected_emotion = "Neutral"

    if filename:
        video_path = os.path.join(UPLOAD, filename)
        vision_score, detected_emotion = analyze_video(video_path)
        vision_score_percent = int(vision_score * 100)

    # ================= FINAL SCORE (Balanced) =================
    final_score = int(
        semantic_score * 0.5 +
        length_score * 0.3 +
        vision_score_percent * 0.2
    )

    # Safety Clamp
    final_score = max(0, min(final_score, 100))

    # ================= SMART FEEDBACK SYSTEM =================
    if words < 10:
        confidence = "Low"
        emotion = "Uncertain"
        feedback = (
            f"For '{question}', your answer was too brief. "
            "Try explaining with definition, key points, and one practical example."
        )

    elif filler_count > 5:
        confidence = "Moderate"
        emotion = "Slightly Nervous"
        feedback = (
            f"You explained '{question}' well, but frequent filler words "
            "like 'hmm' or 'uh' reduced clarity. "
            "Try pausing silently instead of using fillers."
        )

    elif semantic_score < 40:
        confidence = "Developing"
        emotion = "Improving"
        feedback = (
            f"Your answer touched on '{question}', but core technical depth is missing. "
            "Focus on structured explanation and important concepts."
        )

    elif semantic_score < 70:
        confidence = "Good"
        emotion = "Calm"
        feedback = (
            f"Good explanation of '{question}'. "
            "To improve further, add a real-world example or deeper technical clarity."
        )

    else:
        confidence = "Excellent"
        emotion = "Confident"
        feedback = (
            f"Excellent structured answer for '{question}'. "
            "Clear explanation and strong relevance. "
            "You are interview ready!"
        )

    # ================= SAVE TO DATABASE =================
    db = get_db()
    db.execute("""
        INSERT INTO reports
        (user_id, score, semantic_score, similarity, vision_score, confidence, emotion, words, feedback, time, video)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session["user_id"],
        final_score,
        semantic_score,
        similarity,
        vision_score_percent,
        confidence,
        emotion,
        words,
        feedback,
        datetime.now().strftime("%d-%m-%Y %H:%M"),
        filename
    ))
    db.commit()
    db.close()

    return jsonify({"success": True})
# ================= SUBMIT FEEDBACK =================

@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():
    if session.get("role") != "user":
        return redirect("/login")

    db = get_db()
    db.execute("""
        INSERT INTO candidate_feedback
        (user_id, usability, clarity, comfort, fairness, technical, sentiment, submitted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session["user_id"],
        request.form.get("usability"),
        request.form.get("clarity"),
        request.form.get("comfort"),
        request.form.get("fairness"),
        request.form.get("technical"),
        request.form.get("sentiment"),
        datetime.now().strftime("%d-%m-%Y %H:%M")
    ))
    db.commit()
    db.close()

    return redirect("/dashboard")


# ================= ADMIN FEEDBACK =================

@app.route("/admin/feedback")
def admin_feedback():
    if session.get("role") != "admin":
        return redirect("/admin/login")

    db = get_db()
    rows = db.execute(
        "SELECT * FROM candidate_feedback ORDER BY id DESC"
    ).fetchall()
    db.close()

    return render_template("admin_feedback.html", feedback=rows)


# ================= RESULT =================

@app.route("/result")
def result():
    if session.get("role") != "user":
        return redirect("/login")

    db = get_db()
    r = db.execute(
        "SELECT * FROM reports WHERE user_id=? ORDER BY id DESC LIMIT 1",
        (session["user_id"],)
    ).fetchone()
    db.close()

    if not r:
        return redirect("/dashboard")

    return render_template("result.html", **dict(r))


# ================= REPORTS =================

@app.route("/reports")
def reports():
    if session.get("role") != "user":
        return redirect("/login")

    db = get_db()
    rows = db.execute(
        "SELECT * FROM reports WHERE user_id=? ORDER BY id DESC",
        (session["user_id"],)
    ).fetchall()
    db.close()

    return render_template("reports.html", rows=rows)


# ================= PROFILE =================

@app.route("/profile")
def profile():
    if session.get("role") != "user":
        return redirect("/login")

    db = get_db()

    user = db.execute(
        "SELECT email FROM users WHERE id=?",
        (session["user_id"],)
    ).fetchone()

    scores = db.execute(
        "SELECT score FROM reports WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()

    db.close()

    total = len(scores)
    avg = round(sum(s["score"] for s in scores)/total,1) if total else 0

    return render_template("profile.html",
                           name=user["email"],
                           total_interviews=total,
                           avg_score=avg)


# ================= SETTINGS =================

@app.route("/settings")
def settings():
    if session.get("role") != "user":
        return redirect("/login")
    return render_template("settings.html")


# ================= CHANGE PASSWORD =================

@app.route("/change_password", methods=["GET","POST"])
def change_password():
    if session.get("role") != "user":
        return redirect("/login")

    if request.method == "POST":
        current = request.form["current_password"]
        new = request.form["new_password"]
        confirm = request.form["confirm_password"]

        if new != confirm:
            return render_template("change_password.html",
                                   error="Passwords do not match")

        db = get_db()
        user = db.execute(
            "SELECT password FROM users WHERE id=?",
            (session["user_id"],)
        ).fetchone()

        if not check_password_hash(user["password"], current):
            db.close()
            return render_template("change_password.html",
                                   error="Current password incorrect")

        db.execute(
            "UPDATE users SET password=? WHERE id=?",
            (generate_password_hash(new), session["user_id"])
        )
        db.commit()
        db.close()

        return render_template("change_password.html",
                               success="Password updated successfully")

    return render_template("change_password.html")


# ================= ADMIN DASHBOARD =================

@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect("/admin/login")

    db = get_db()

    # Basic counts
    total_users = db.execute(
        "SELECT COUNT(*) FROM users WHERE role='user'"
    ).fetchone()[0]

    total_reports = db.execute(
        "SELECT COUNT(*) FROM reports"
    ).fetchone()[0]

    total_feedback = db.execute(
        "SELECT COUNT(*) FROM candidate_feedback"
    ).fetchone()[0]

    feedback_data = db.execute(
        "SELECT * FROM candidate_feedback ORDER BY id DESC"
    ).fetchall()

    # 📈 User Growth (by date)
    user_growth = db.execute("""
        SELECT substr(time, 1, 10) as date, COUNT(*) as count
        FROM reports
        GROUP BY date
        ORDER BY date ASC
    """).fetchall()

    growth_labels = [row["date"] for row in user_growth]
    growth_counts = [row["count"] for row in user_growth]

    # 📊 Score Trend
    score_trend = db.execute("""
        SELECT score FROM reports ORDER BY id ASC
    """).fetchall()

    scores = [row["score"] for row in score_trend]

    db.close()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_reports=total_reports,
        total_feedback=total_feedback,
        feedback_data=feedback_data,
        growth_labels=growth_labels,
        growth_counts=growth_counts,
        scores=scores
    )

import csv
from flask import Response

@app.route("/admin/export")
def export_data():
    if session.get("role") != "admin":
        return redirect("/admin/login")

    db = get_db()
    reports = db.execute("SELECT * FROM reports").fetchall()
    db.close()

    def generate():
        data = csv.writer(open("temp.csv", "w", newline=""))
        yield "user_id,score,semantic_score,vision_score,confidence,emotion,words,time\n"
        for r in reports:
            yield f"{r['user_id']},{r['score']},{r['semantic_score']},{r['vision_score']},{r['confidence']},{r['emotion']},{r['words']},{r['time']}\n"

    return Response(generate(),
                    mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=reports.csv"})
@app.route("/feedback")
def feedback_page():
    if session.get("role") != "user":
        return redirect("/login")
    return render_template("feedback.html")



init_db()

if __name__ == "__main__":
    app.run(debug=True)