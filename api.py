import json
from typing import Dict
from flask import Flask, render_template, request
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user, login_user, UserMixin, login_required



app = Flask(__name__)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key = 'my Pa$$word!!!'

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"

admin = Admin(app, name='microblog', template_mode='bootstrap3')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def check_password(self, password):
        return self.password == password


class Classes(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    class_name = db.Column(db.String, nullable=False)
    timeslot = db.Column(db.String, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    enrolled = db.Column(db.Integer, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    students = db.relationship('Students', secondary='enrollment')


class Students(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    classes = db.relationship('Classes', secondary='enrollment')


class Teachers(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    classes = db.relationship('Classes', backref=db.backref('classes', lazy=True))


class Enrollment(db.Model):
    class_id = db.Column('class_id', db.Integer, db.ForeignKey('classes.id'), primary_key=True)
    student_id = db.Column('student_id', db.Integer, db.ForeignKey('students.id'), primary_key=True)
    grade = db.Column('grade', db.String, nullable=False)



admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Classes, db.session))
admin.add_view(ModelView(Teachers, db.session))
admin.add_view(ModelView(Students, db.session))

db.create_all()
db.session.commit()
u1 = User(username="alcerpa", password="2023")
u = User(username="kirpal", password="2022")
db.session.add(u)
db.session.add(u1)
db.session.commit()
s = Students(first_name = "Sabir", last_name = "Kirpal", user_id = u.id)
db.session.add(s)
db.session.commit()
t = Teachers(first_name = "Al", last_name = "Cerpa", user_id = u1.id)
db.session.add(t)
db.session.commit()
c = Classes(class_name= "CSE 106", timeslot = "10", size = 50, enrolled = 20, teacher_id = t.id)
db.session.add(c)
db.session.commit()



@login_manager.user_loader
def load_user(user_id):
    try:
        u = User.query.get(user_id)
        return u
    except:
        return None

@app.route("/", methods=["GET"])
def landingPage():
    if(current_user.is_authenticated):
        return render_template("dashboard.html", name = current_user.username)
    else:
        return render_template("login.html")

@app.route("/login", methods=["POST"])
def returningUser():
    user = User.query.filter_by(username=request.json['username']).first()
    if user is not None and user.check_password(request.json['password']):
        login_user(user)
        print("LOGGED IN USER WITH ID: " + str(user.id))
        return render_template("dashboard.html", name = current_user.username)
    else:
        return dict(msg = "FAILED")

@app.route("/dashboard", methods = ["GET"])
@login_required
def loadDashboard():
    return render_template("dashboard.html", name = current_user.username)

@app.route("/browseclasses/", methods=["GET"])
@login_required
def loadClasses():
    user = User.query.filter_by(id = current_user.id).first()
    stu = Students.query.filter(Students.user_id == user.id).first()
    print(stu.classes)
    c = Classes.query.filter_by(class_name = "CSE 106").first()

    stu.classes.append(c)

    print(stu.classes)
    db.session.commit()

app.run()