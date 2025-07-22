from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "changeme")

USER_FILE = "users.json"
TODO_FILE = "todos.json"


def load_user():
    try:
        with open(USER_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"username": "admin", "password": "password"}


def load_todos():
    try:
        with open(TODO_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_todos(todos):
    try:
        with open(TODO_FILE, 'w') as f:
            json.dump(todos, f, indent=2)
        return True
    except Exception as e:
        print(f"Fehler beim Speichern der To-Dos: {e}")
        return False


@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    return redirect(url_for("home"))


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


# Neue Route für die To-Do-Seite
@app.route('/todo')
def todo_page():
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template('todo.html', username=session["username"])


# Neue Route für die leere Seite
@app.route('/empty/<page>')
def empty_page(page):
    if "username" not in session:
        return redirect(url_for("login"))
    return render_template('empty.html', page=page, username=session["username"])


# ===== TO-DO API ROUTES =====
@app.route('/api/todos', methods=['GET'])
def get_todos():
    if "username" not in session:
        return jsonify({"error": "Nicht angemeldet"}), 401

    todos = load_todos()
    return jsonify(todos)


@app.route('/api/todos', methods=['POST'])
def save_todos_api():
    if "username" not in session:
        return jsonify({"error": "Nicht angemeldet"}), 401

    try:
        todos = request.get_json()
        if save_todos(todos):
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Speichern fehlgeschlagen"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ===== NOTIFICATION API ROUTES =====
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    if "username" not in session:
        return jsonify({"error": "Nicht angemeldet"}), 401

    todos = load_todos()
    # Nur offene Aufgaben als Benachrichtigungen
    open_todos = [todo for todo in todos if not todo.get('completed', False)]

    # Beschränke auf die neuesten 10 Aufgaben
    notifications = open_todos[:10]

    return jsonify({
        "notifications": notifications,
        "total_count": len(open_todos)
    })


@app.route('/api/todos/<int:todo_id>/complete', methods=['POST'])
def complete_todo(todo_id):
    if "username" not in session:
        return jsonify({"error": "Nicht angemeldet"}), 401

    try:
        todos = load_todos()

        # Finde die Aufgabe und markiere sie als erledigt
        for todo in todos:
            if todo.get('id') == todo_id:
                todo['completed'] = True
                todo['completedAt'] = request.json.get('completedAt')
                break

        if save_todos(todos):
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Speichern fehlgeschlagen"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)