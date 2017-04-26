# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, request, url_for, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user , logout_user , current_user , login_required
from functools import wraps
import datetime
from flask_mail import Mail, Message
from threading import Thread

app = Flask(__name__)

now = datetime.datetime.now()
mydate = now.strftime("%d-%m-%Y")

app.secret_key = 'super secret key'
#app.config['SESSION_TYPE'] = 'filesystem'

# Flask-SQLAlchemy
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///froshims3.db"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)

#mail
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'vladimiruman81'
app.config["MAIL_PASSWORD"] = 'rtktwrfz112'
mail = Mail(app)

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
    date = db.Column(db.Text)
    archiv = db.Column(db.Boolean)
    coment = db.Column(db.Text)

    def __init__(self, tel, kontakt, mobile, mail, date, archiv, coment):
        self.tel = tel
        self.kontakt = kontakt
        self.mobile = mobile
        self.mail = mail
        self.date = date
        self.archiv = archiv
        self.coment = coment
                
class Users(db.Model):

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    mail = db.Column(db.Text)
    role = db.Column(db.Text)

    def __init__(self, login, password, mail, role):
        self.login = login
        self.password = password
        self.mail = mail
        self.role = role
        
    def get_role(self):
        return self.role
    
    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return '%s' % (self.login)

def required_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.get_role() not in roles:
                return redirect(url_for('main'))
            return f(*args, **kwargs)
        return wrapped
    return wrapper
 
@app.route("/")
@app.route("/main")
def main():
    return render_template("main.html")

@app.route("/tarif")
def tarif():
    return render_template("tarif.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contacts")
def contacts():
    return render_template("contacts.html")

@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/register", methods=["POST"])
def register():
    comment = str(mydate) + ': нова заявка. ' + request.form["coment"]
    registrant = Registrant(request.form["tel"], request.form["kontakt"], request.form["mobile"], request.form["mail"], mydate, False, comment)
    db.session.add(registrant)
    db.session.commit()
    send(request.form["mail"], request.form["kontakt"], request.form["mobile"], request.form["tel"])
    return render_template("success.html", kontakt=request.form["kontakt"], tel=request.form["tel"])

@app.route("/registrants", methods=["GET", "POST"])
@login_required
def registrants():
    if request.method == "GET":
        rows = Registrant.query.filter(Registrant.archiv == False)
        return render_template("registrants.html", registrants=rows)
    elif request.method == "POST":
        if request.form["id"]:
            zayavka = Registrant.query.filter(Registrant.id == request.form["id"]).first()
            comment = '\n' + str(mydate) + ': ' + request.form["coment"]
            zayavka.coment += comment
            if 'archiv' in request.form:
                zayavka.archiv = True 
            db.session.commit()
        return redirect(url_for("registrants"))
    
@app.route("/registrants_archiv", methods=["GET", "POST"])
@login_required
def registrants_archiv():
    if request.method == "GET":
        rows = Registrant.query.filter(Registrant.archiv == True)
        return render_template("registrants_archiv.html", registrants=rows)
    elif request.method == "POST":
        if request.form["id"]:
            Registrant.query.filter(Registrant.id == request.form["id"]).delete()
            db.session.commit()
        return redirect(url_for("registrants_archiv"))

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
        return redirect(url_for('login'))
    login_user(registered_user, remember = remember_me)
    if g.user.get_role() == 'admin':
        return redirect(url_for('panel'))
    return redirect(url_for('registrants'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main'))

@app.route("/panel", methods=["GET", "POST"])
@login_required
@required_roles('admin')
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
@required_roles('admin')
def adduserform():
    return render_template("adduserform.html")

@app.route("/adduser", methods=["POST"])
@login_required
@required_roles('admin')
def adduser():
    user = Users(request.form["login"], request.form["password"], request.form["mail"], request.form["role"])
    db.session.add(user)
    db.session.commit()
    return redirect(url_for("panel"))

@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

#mail

def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target = f, args = args, kwargs = kwargs)
        thr.start()
    return wrapper

@async
def send_async_email(msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.html = html_body
    send_async_email(msg)
    #thr = Thread(target = send_async_email, args = [msg])
    #thr.start()
    
def send(client, kontakt, mobile, tel):
    sender = 'admin'
    recipient_client = [client]
    recipient_user = []
    subject = "Vintelecom"
    send_email(subject, sender, recipient_client, render_template("html_body.html", kontakt=kontakt, tel=tel))
    users = Users.query.filter(Users.role == 'user')
    for user in users:
        recipient_user.append(user.mail)
    send_email(subject, sender, recipient_user, render_template("html_user_body.html", kontakt=kontakt, tel=tel, mobile=mobile))


app.run(debug=True)
    