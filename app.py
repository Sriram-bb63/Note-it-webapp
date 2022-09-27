import os
from datetime import datetime

from flask import Flask, redirect, render_template, request
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)
app.config["SECRET_KEY"] = os.urandom(40)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(100), nullable=True)
    created = db.Column(db.DateTime, default=datetime.now(), nullable=False)



@app.route("/", methods=["GET"])
@app.route("/home", methods=["GET"])
def index():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        print(">>> REGISTER SUCCESS")
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                login_user(user)
                print(">>> LOGIN SUCCESS")
                return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    username = current_user.username
    notes = Note.query.filter_by(username=username)
    notes_lst = [[note.id, note.title, note.content, note.created] for note in notes]
    return render_template("dashboard.html", username=username, notes_lst=notes_lst)

@app.route("/create-note", methods=["GET", "POST"])
@login_required
def create_note():
    if request.method == "POST":
        username = current_user.username
        title = request.form.get("title")
        content = request.form.get("content")
        new_note = Note(username=username, title=title, content=content)
        db.session.add(new_note)
        db.session.commit()
        print(">>> NEW NOTE CREATED")
        return redirect("/dashboard")
    return render_template("createnote.html")

@app.route("/delete-note", methods=["GET", "POST"])
@login_required
def delete_note():
    if request.method == "POST":
        username = current_user.username
        id = request.json.get("id")
        Note.query.filter_by(id=id).delete()
        db.session.commit()
        print(">>> NOTE DELETED")
        print(request.referrer)
        return redirect(request.referrer)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    print(">>> LOGOUT SUCCESS")
    return redirect("/login")



if __name__ == "__main__":
    app.run(debug=True)
