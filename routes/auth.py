from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
from models.user import User
from utils import login_required, log_audit

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("login.html")

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["username"] = user.username
            log_audit("Login", f"User {username} logged in")
            db.session.commit()
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard.index"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    username = session.get("username", "Unknown")
    log_audit("Logout", f"User {username} logged out")
    db.session.commit()
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
