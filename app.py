from flask import Flask
from flask import redirect, Blueprint, render_template, request, session
import psycopg2
from Db import db
from Db.models import useradmin
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from rgz import rgz


app = Flask(__name__)
app.register_blueprint(rgz)

app.secret_key = "123"
user_db = "postgres"
host_ip = "127.0.0.1"
host_port = "5432"
database_name = "book"
password = "postgres"

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user_db}:{password}@{host_ip}:{host_port}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Инициализация Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return useradmin.query.get(int(user_id))
