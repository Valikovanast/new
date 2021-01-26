import os
from flask import Flask, render_template, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

naming_convention = {
    'pk': 'pk_%(table_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'ix': 'ix_%(table_name)s_%(column_0_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
}

db = SQLAlchemy(app, metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate(app, db)

from models import Image, Category, Course

from courses import bp as courses_bp
from auth import bp as auth_bp, init_login_manager
from api import bp as api_bp

init_login_manager(app)

app.register_blueprint(courses_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

@app.route('/')
def index():
    categories = Category.query.all()
    courses = Course.query.order_by((Course.rating_sum/Course.rating_num)
                          .desc()).limit(6).all()
    return render_template(
        'index.html', 
        categories=categories, 
        courses=courses,
    )

@app.route('/images/<image_id>')
def image(image_id):
    img = Image.query.get(image_id)
    if img is None:
        abort(404)
    return send_from_directory(app.config['UPLOAD_FOLDER'], img.storage_filename)
    