import os
from datetime import datetime, timedelta

from flask import Flask, redirect, render_template, request, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy



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
    Userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    mail = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    otp = db.Column(db.Integer, nullable=True)
    otpValidity = db.Column(db.DateTime, default=datetime.now() + timedelta(minutes=10))

class Notes(db.Model):
    Noteid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(100), nullable=True)
    tag = db.Column(db.String(20), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    lastEdited = db.Column(db.DateTime, default=datetime.now(), nullable=False)

class Tags():
    tags = ["General", "Home", "Office", "Random"]



@app.route("/", methods=["GET", "POST"])
@app.route("/login")
def index():
    try:
        if request.method == "POST":
            mail = request.form.get("mail")
            password = request.form.get("password")
            user = Users.query.filter_by(mail=mail).first()
            if user:
                if bcrypt.check_password_hash(user.password, password) == True:
                    login_user(user)
                    print(">>> LOGIN SUCCESS")
                    return redirect("/dashboard")
        return render_template("login.html")
    except Exception as e:
        data = request.get_data()
        req_dict = request.__dict__
        return render_template("error.html", e=str(e), data=data, req_dict=req_dict)

@app.route("/register", methods=["GET", "POST"])
def register():
    try:
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
    except Exception as e:
        data = request.get_data()
        req_dict = request.__dict__
        return render_template("error.html", e=str(e), data=data, req_dict=req_dict)

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    try:
        if request.method == "POST":
            mail = request.form.get("mail")
            user = Users.query.filter_by(mail=mail).first()
            if user:
                return redirect(f"/forgot-password-otp/{user.username}")
            else:
                print("No user found")
        return render_template("forgot-password.html")
    except Exception as e:
        data = request.get_data()
        req_dict = request.__dict__
        return render_template("error.html", e=str(e), data=data, req_dict=req_dict)

@app.route("/forgot-password/<username>", methods=["GET", "POST"])
def forgot_password_otp(username):
    try:
        if request.method == "POST":
            user = Users.query.filter_by(username=username).first()
            otp = request.form.get("otp")
            if datetime.now() <= user.otpValidity and otp == user.otp:
                return redirect(f"/change-password/{username}")
        return render_template("forgot-password-otp.html")
    except Exception as e:
        data = request.get_data()
        req_dict = request.__dict__
        return render_template("error.html", e=str(e), data=data, req_dict=req_dict)

@app.route("/change-password/<username>", methods=["GET", "POST"])
def change_password(username):
    try:
        if request.method == "POST":
            password_1 = request.form.get("password1")
            password_2 = request.form.get("password2")
            if password_1 == password_2:
                user = Users.query.filter_by(username=username).first()
                user.password = password_1
                db.session.commit()
            return redirect("/login")
        return render_template("change-password.html")
    except Exception as e:
        data = request.get_data()
        req_dict = request.__dict__
        return render_template("error.html", e=str(e), data=data, req_dict=req_dict)

@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def change_username():
    try:
        username = current_user.username
        user = Users.query.filter_by(username=username)
        if request.method == "POST":
            new_username = request.form.get("username")
            new_mail = request.form.get("mail")
            user.username = new_username
            user.mail = new_mail
            notes = Notes.query.filter_by(username=username)
            for note in notes:
                note.username = new_username
            db.session.commit()
            return redirect("/dashboard")
        return render_template("change-username.html", username=username, mail=user.mail)
    except Exception as e:
        data = request.get_data()
        req_dict = request.__dict__
        return render_template("error.html", e=str(e), data=data, req_dict=req_dict)

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    try:
        username = current_user.username
        notes = Notes.query.filter_by(username=username)
        general_notes = [[note.id, note.title, note.content, note.tag, note.created, note.lastedited] for note in notes if note.tag == "General"]
        home_notes = [[note.id, note.title, note.content, note.tag, note.created, note.lastedited] for note in notes if note.tag == "Home"]
        office_notes = [[note.id, note.title, note.content, note.tag, note.created, note.lastedited] for note in notes if note.tag == "Office"]
        return render_template("dashboard.html", username=username, general_notes=general_notes, home_notes=home_notes, office_notes=office_notes)
    except Exception as e:
        data = request.get_data()
        req_dict = request.__dict__
        return render_template("error.html", e=str(e), data=data, req_dict=req_dict)

@app.route("/create-note", methods=["GET", "POST"])
@login_required
def create_note():
    try:
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
    except Exception as e:
        data = request.get_data()
        req_dict = request.__dict__
        return render_template("error.html", e=str(e), data=data, req_dict=req_dict)

@app.route("/delete-note", methods=["GET", "POST"])
@login_required
def delete_note():
    try:
        if request.method == "POST":
            id = request.json.get("id")
            Notes.query.filter_by(id=id).delete()
            db.session.commit()
            print(">>> NOTE DELETED")
            return redirect(request.referrer)
    except Exception as e:
        data = request.get_data()
        req_dict = request.__dict__
        return render_template("error.html", e=str(e), data=data, req_dict=req_dict)

@app.route("/edit-note", methods=["GET", "POST"])
@login_required
def edit_note():
    try:
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
    except Exception as e:
        data = request.get_data()
        req_dict = request.__dict__
        return render_template("error.html", e=str(e), data=data, req_dict=req_dict)

@app.route("/logout")
@login_required
def logout():
    try:
        logout_user()
        print(">>> LOGOUT SUCCESS")
        return redirect("/login")
    except Exception as e:
        data = request.get_data()
        req_dict = request.__dict__
        return render_template("error.html", e=str(e), data=data, req_dict=req_dict)



if __name__ == "__main__":
    app.run(debug=True)
