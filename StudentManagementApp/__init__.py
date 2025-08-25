#__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.secret_key = 'GHFGH&*%^$^*(JHFGHF&Y*R%^$%$^&*TGYGJHFHGVJHGY'


#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:01676831139Chi%40@localhost:3306/studentdb?charset=utf8mb4"
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:26032004@localhost/studentdb?charset=utf8mb4"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:askme@localhost:3306/studentdb?charset=utf8mb4"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['nambatdau'] = 2025

# Khởi tạo DB
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

from StudentManagementApp.models import User, Role
app.jinja_env.globals['Role'] = Role

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Đăng ký các Blueprint
from StudentManagementApp.routes.teacher import teacher
from StudentManagementApp.routes import auth
from StudentManagementApp.routes.staff import staff

app.register_blueprint(staff)
app.register_blueprint(teacher)

from StudentManagementApp import admin_view
