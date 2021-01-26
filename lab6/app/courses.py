import os
import bleach
from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash
from flask_login import login_required
from tools import Navigator, ImageSaver, CoursesFilter
from models import Course, Category, Image, Theme, User, Step, Page

from app import db

bp = Blueprint('courses', __name__, url_prefix='/courses')

PERMITTED_PARAMS = ['name', 'category_id', 'short_desc', 'full_desc', 'author_id']

PER_PAGE = 3

def params():
    return { p: request.form.get(p) for p in PERMITTED_PARAMS }

def search_params():
    return {
        'name': request.args.get('name'),
        'category_ids': request.args.getlist('category_ids')
    }

@bp.route('/')
@bp.route('/catalog')
def index():
    page = request.args.get('page', 1, type=int)
    categories = Category.query.all()
    courses_filter = CoursesFilter(**search_params())
    courses = courses_filter.perform()
    pagination = courses.paginate(page, PER_PAGE)
    courses = pagination.items
    return render_template(
        'courses/index.html', 
        courses=courses, 
        categories=categories, 
        pagination=pagination,
        search_params=search_params(),
    )

@bp.route('/new')
@login_required
def new():
    categories = Category.query.all()
    users = User.query.all()
    return render_template(
        'courses/new.html', 
        categories=categories, 
        users=users,
    )

@bp.route('/create', methods=['POST'])
@login_required
def create():
    f = request.files.get('background_img') 
    img = None
    if f and f.filename:
        img_saver = ImageSaver(f)
        img = img_saver.save()

    course = Course(**params(), background_image_id=img.id)
    db.session.add(course)
    db.session.commit()

    if img:
        img_saver.bind_to_object(course)

    flash(f'Курс {course.name} был успешно создан!', 'success')

    return redirect(url_for('courses.index'))

@bp.route('/<int:course_id>')
def show(course_id):
    course = Course.query.get(course_id)
    return render_template('courses/show.html', course=course)

@bp.route('/<int:course_id>/themes/create', methods=['POST'])
@login_required
def create_theme(course_id):
    theme = Theme(name=request.form.get('name'))
    parent_id = request.form.get('parent_id')
    if parent_id:
        theme.parent_id = parent_id
    else:
        theme.course_id = course_id
    db.session.add(theme)
    db.session.commit()
    return redirect(url_for('courses.show', course_id=course_id))

@bp.route('/<int:course_id>/themes/<int:theme_id>/steps/new')
@login_required
def new_step(course_id, theme_id):
    course = Course.query.get(course_id)
    theme = Theme.query.get(theme_id)
    step = request.args.get('step', 1, type=int)
    return render_template(
        'courses/steps/new.html', 
        course=course, 
        theme=theme, 
        step=step,
    )

@bp.route('/<int:course_id>/themes/<int:theme_id>/steps/create', methods=['POST'])
@login_required
def create_step(course_id, theme_id):
    step = Step(content_type=request.form.get('content_type'), theme_id=theme_id)
    db.session.add(step)
    db.session.commit()

    if step.content_type == 'text':
        text = bleach.clean(request.form.get('text'))
        page = Page(step_id=step.id, text=text)
        db.session.add(page)
        db.session.commit()

        image_ids = request.form.getlist('image_id')
        images = Image.query.filter(Image.id.in_(image_ids))
        for img in images:
            img.object_type = page.__tablename__
            img.object_id = page.id
            img.active = True
            db.session.add(img)
        db.session.commit()

    return redirect(url_for(
        'courses.show_content', 
        course_id=course_id, 
        theme_id=theme_id, 
        step_id=step.id,
    ))

@bp.route('/<int:course_id>/content', defaults={ 'theme_id': None })
@bp.route('/<int:course_id>/content/themes/<int:theme_id>')
@login_required
def show_content(course_id, theme_id=None):
    course = Course.query.get(course_id)
    theme = Theme.query.get(theme_id) if theme_id else None
    step_id = request.args.get('step_id', type=int)
    step = Step.query.get(step_id) if step_id else None
    theme = step.theme if step is not None else theme
    navigator = Navigator(course, theme, step)
    if step is None:
        step = navigator.current_step
    return render_template(
        'courses/content/show.html', 
        course=course, 
        step=step, 
        theme=theme, 
        navigator=navigator,
    )
