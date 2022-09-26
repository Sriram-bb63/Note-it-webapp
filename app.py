
from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user


app = Flask(__name__)
db = SQLAlchemy(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

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
    username = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(100), nullable=True)



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
    return render_template("dashboard.html")

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

@app.route("/logout")
@login_required
def logout():
    logout_user()
    print(">>> LOGOUT SUCCESS")
    return redirect("/login")



if __name__ == "__main__":
    app.run(debug=True)