from flask import Flask, render_template, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "changeme")

USER_FILE = "users.json"


def load_user():
    try:
        with open(USER_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"username": "admin", "password": "password"}


@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("home"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        creds = load_user()
        username = request.form.get("username")
        password = request.form.get("password")
        if username == creds.get("username") and password == creds.get("password"):
            session["username"] = username
            return redirect(url_for("home"))
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/home")
def home():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template("home.html", username=session["username"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
