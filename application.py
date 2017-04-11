from flask import Flask, render_template, redirect, request, url_for, flash, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user , logout_user , current_user , login_required

app = Flask(__name__)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

#in_user = current_user

# Flask-SQLAlchemy
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///froshims3.db"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Registrant(db.Model):

    __tablename__ = "registrants"
    id = db.Column(db.Integer, primary_key=True)
    tel = db.Column(db.Text)
    kontakt = db.Column(db.Text)
    mobile = db.Column(db.Text)
    mail = db.Column(db.Text)

    def __init__(self, tel, kontakt, mobile, mail):
        self.tel = tel
        self.kontakt = kontakt
        self.mobile = mobile
        self.mail = mail
        
class Users(db.Model):

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    role = db.Column(db.Text)

    def __init__(self, login, password, role):
        self.login = login
        self.password = password
        self.role = role
        
    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return str(self.id)
 
    def __repr__(self):
        return '<User %r>' % (self.username)
        
@app.route("/")
def main():
    return render_template("main.html")

@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/register", methods=["POST"])
def register():
    if request.form["tel"] == "" or request.form["kontakt"] == "" or request.form["mobile"] == "" or request.form["mail"] == "":
        return render_template("failure.html")
    registrant = Registrant(request.form["tel"], request.form["kontakt"], request.form["mobile"], request.form["mail"])
    db.session.add(registrant)
    db.session.commit()
    return render_template("success.html")

@app.route("/registrants")
@login_required
def registrants():
    rows = Registrant.query.all()
    return render_template("registrants.html", registrants=rows)

@app.route("/unregister", methods=["GET", "POST"])
@login_required
def unregister():
    if request.method == "GET":
        rows = Registrant.query.all()
        return render_template("unregister.html", registrants=rows)
    elif request.method == "POST":
        if request.form["id"]:
            Registrant.query.filter(Registrant.id == request.form["id"]).delete()
            db.session.commit()
        return redirect(url_for("registrants"))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    login = request.form['login']
    password = request.form['password']
    remember_me = False
    if 'remember' in request.form:
        remember_me = True
    registered_user = Users.query.filter_by(login=login,password=password).first()
    if registered_user is None:
        flash('Username or Password is invalid' , 'error')
        return redirect(url_for('login'))
    login_user(registered_user, remember = remember_me)
    flash('Logged in successfully')
    if login == 'admin':
        return redirect(url_for('panel'))
    return redirect(url_for('unregister'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main'))

@app.route("/panel", methods=["GET", "POST"])
@login_required
def panel():    
    if request.method == "GET":
        rows = Users.query.all()
        return render_template("panel.html", users=rows)
    elif request.method == "POST":
        if request.form["id"]:
            Users.query.filter(Users.id == request.form["id"]).delete()
            db.session.commit()
        return redirect(url_for("panel"))

@app.route("/adduserform")
@login_required
def adduserform():
    return render_template("adduserform.html")

@app.route("/adduser", methods=["POST"])
@login_required
def adduser():
    if request.form["login"] == "" or request.form["password"] == "" or request.form["role"] == "":
        return render_template("failure.html")
    user = Users(request.form["login"], request.form["password"], request.form["role"])
    db.session.add(user)
    db.session.commit()
    return render_template("success.html")

@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

app.run(debug=True)
