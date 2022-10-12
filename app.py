import os
from datetime import datetime
from random import randrange

from flask import Flask, redirect, render_template, request, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy

from mail import mail_otp



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config["SECRET_KEY"] = os.urandom(40)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))



class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    mail = db.Column(db.String(50), nullable=True)
    password = db.Column(db.String(20), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    otp = db.Column(db.Integer, nullable=True)

class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(100), nullable=True)
    tag = db.Column(db.String(20), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    lastedited = db.Column(db.DateTime, default=datetime.now(), nullable=False)

class Tags():
    tags = ["General", "Home", "Office", "Random"]



@app.route("/", methods=["GET", "POST"])
@app.route("/login")
def index():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Users.query.filter_by(username=username).first()
        if user:
            if bcrypt.check_password_hash(user.password, password) == True:
                login_user(user)
                print(">>> LOGIN SUCCESS")
                return redirect("/dashboard")
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        mail = request.form.get("mail")
        password = request.form.get("password")
        hashed_password = bcrypt.generate_password_hash(password)
        new_user = Users(username=username, mail=mail, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        print(">>> REGISTER SUCCESS")
        return redirect("/login")
    return render_template("register.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form.get("username")
        user = Users.query.filter_by(username=username).first()
        if user:
            if user.mail != "":
                otp = str(randrange(1000, 9999))
                user.otp = otp
                db.session.commit()
                print(f">>> OTP {otp}")
                return redirect(f"/otp-change-password/{username}")
                # if mail_otp(user.mail, otp) == True:
                #     print(">>> OTP sent {otp}")
        else:
            print(">>> User not found")
    return render_template("forgot-password.html")

@app.route("/otp-change-password/<username>", methods=["GET", "POST"])
def otp_change_password(username):
    if request.method == "POST":
        otp = request.form.get("otp")
        password = request.form.get("password")
        user = Users.query.filter_by(username=username).first()
        if user.otp == otp:
            user.password = password
            db.session.commit()
            print(">>> Password changed")
        return redirect("/login")        
    return render_template("otp-change-password.html")

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    username = current_user.username
    notes = Notes.query.filter_by(username=username)
    general_notes = [[note.id, note.title, note.content, note.tag, note.created, note.lastedited] for note in notes if note.tag == "General"]
    home_notes = [[note.id, note.title, note.content, note.tag, note.created, note.lastedited] for note in notes if note.tag == "Home"]
    office_notes = [[note.id, note.title, note.content, note.tag, note.created, note.lastedited] for note in notes if note.tag == "Office"]
    return render_template("dashboard.html", username=username, general_notes=general_notes, home_notes=home_notes, office_notes=office_notes)

@app.route("/create-note", methods=["GET", "POST"])
@login_required
def create_note():
    if request.method == "POST":
        username = current_user.username
        title = request.form.get("title")
        content = request.form.get("content")
        tag = request.form.get("tag")
        new_note = Notes(username=username, title=title, content=content, tag=tag)
        db.session.add(new_note)
        db.session.commit()
        print(">>> NEW NOTE CREATED")
        return redirect("/dashboard")
    tags = Tags.tags
    return render_template("createnote.html", tags=tags)

@app.route("/delete-note", methods=["GET", "POST"])
@login_required
def delete_note():
    if request.method == "POST":
        id = request.json.get("id")
        Notes.query.filter_by(id=id).delete()
        db.session.commit()
        print(">>> NOTE DELETED")
        return redirect(request.referrer)

@app.route("/edit-note", methods=["GET", "POST"])
@login_required
def edit_note():
    if request.method == "POST":
        id = request.form.get("id")
        new_title = request.form.get("title")
        new_content = request.form.get("content")
        note = Notes.query.filter_by(id=id).first()
        note.title = new_title
        note.content = new_content
        note.lastedited = datetime.now()
        db.session.commit()
        print(">>> NOTE EDITED")
        return redirect(request.referrer)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    print(">>> LOGOUT SUCCESS")
    return redirect("/login")



if __name__ == "__main__":
    app.run(debug=True)
