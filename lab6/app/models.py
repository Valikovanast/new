import os
from flask import url_for
import sqlalchemy as sa
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import markdown
from app import db

class User(db.Model, UserMixin):
    __tablename__ = 'users4'

    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    login = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())
    role_id = db.Column(db.Integer, db.ForeignKey('roles4.id'))

    def __repr__(self):
        return '<User %r>' % self.login

    @property
    def full_name(self):
        return ' '.join([self.last_name, self.first_name, self.middle_name or ''])

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Role(db.Model):
    __tablename__ = 'roles4'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text())

    def __repr__(self):
        return '<Role %r>' % self.name

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return '<Category %r>' % self.name

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.String(36), primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    md5_hash = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())
    object_type = db.Column(db.String(100))
    object_id = db.Column(db.Integer)
    active = db.Column(db.Boolean(False), nullable=False, default=False)

    def __repr__(self):
        return '<Image %r>' % self.file_name

    @property
    def url(self):
        return url_for('image', image_id=self.id)

    @property
    def storage_filename(self):
        _, ext = os.path.splitext(self.file_name)
        return self.id + ext


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    short_desc = db.Column(db.Text(), nullable=False)
    full_desc = db.Column(db.Text(), nullable=False)
    rating_sum = db.Column(db.Integer, default=0)
    rating_num = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    background_image_id = db.Column(db.String(36), db.ForeignKey('images.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users4.id'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())

    category = db.relationship('Category')
    bg_image = db.relationship('Image')
    themes = db.relationship('Theme', backref='course')
    author = db.relationship('User')

    def __repr__(self):
        return '<Course %r>' % self.name

    @property
    def rating(self):
        if self.rating_num > 0:
            return self.rating_sum/self.rating_num
        else:
            return 0

class Theme(db.Model):
    __tablename__ = 'themes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('themes.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    subthemes = db.relationship('Theme')
    steps = db.relationship('Step', backref='theme')

class Step(db.Model):
    __tablename__ = 'steps'

    id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(db.String(100), nullable=False)
    theme_id = db.Column(db.Integer, db.ForeignKey('themes.id'), nullable=False)

    page = db.relationship('Page', backref='step', uselist=False)

class Page(db.Model):
    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text(), nullable=False)
    step_id = db.Column(db.Integer, db.ForeignKey('steps.id'), nullable=False, unique=True)

    @property
    def html(self):
        return markdown.markdown(self.text)






