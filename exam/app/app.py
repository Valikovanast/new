import os
import io
import math
import datetime
from flask import Flask, render_template, request, session, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from mysql_db import MySQL
from werkzeug.utils import secure_filename
import mysql.connector as connector
import hashlib
import bleach
import markdown
from werkzeug.utils import secure_filename


UPLOAD_FOLDER='media/images/'
app=Flask(__name__)

application=app
app.config.from_pyfile('config.py')
mysql=MySQL(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from auth import bp as auth_bp, init_login_manager

init_login_manager(app)
app.register_blueprint(auth_bp)

def load_genres():
    cursor= mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT genre.* FROM genre;')
    genre=cursor.fetchall()
    cursor.close()
    return genre

def counting_reviews():
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT film_description.* FROM film_description ORDER BY film_description.prod_year DESC;')
    films=cursor.fetchall()
    cursor.execute('SELECT film_description.id as id, COUNT(t2.id) as count FROM film_description LEFT OUTER JOIN (SELECT exam_review.film_id as id FROM exam_review WHERE exam_review.status="2") as t2 ON t2.id=film_description.id GROUP BY id ORDER BY film_description.prod_year DESC;')
    coun=cursor.fetchall()
    cursor.close()
    number=[]
    for film in films:
        for num in coun:
            if film.id == num.id and num.id:
                number.append(num)
    return number


def download_post(film_id):
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM `film_post` WHERE film_id=%s;',(film_id,))
    poster = cursor.fetchone()
    cursor.close()
    return poster


def load_review(film_id):
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute(' SELECT * FROM `exam_review` WHERE film_id=%s;')
    review = cursor.fetchone()
    cursor.close()
    return review

def rev():
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM exam_review;')
    rev = cursor.fetchall()
    cursor.close()
    return rev

def load_film(film_id, markdown=False):
    cursor=mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM film_description WHERE id=%s;',(film_id,))
    film= cursor.fetchone()
    if markdown:
        film = film.mrk(description=markdown(film.description))
    cursor.close()
    return film

def load_films():
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM `film_description`;')
    film=cursor.fetchall()
    cursor.close()
    return film

def load_status(status_id):
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM exam_status WHERE id=%s;',(status_id,))
    status=cursor.fetchone()
    cursor.close()
    return status

def users():
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute('SELECT exam_users.id_us as id, roles_for_films.name AS role_name FROM exam_users LEFT OUTER JOIN roles_for_films ON exam_users.role = roles_for_films.id;')
    users = cursor.fetchall()
    cursor.close()
    return users


@app.route('/films/<int:film_id>/edit')
@login_required
def edit(film_id):
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute('SELECT film_description.* FROM film_description WHERE film_description.id=%s;',(film_id,))
    film=cursor.fetchone()
    cursor.close()
    return render_template('films/edit.html', film=film, genre=load_genres())


@app.route('/films/<int:film_id>')
@login_required
def show(film_id):
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute('SELECT film_description.*, GROUP_CONCAT(genre.name) as genre FROM film_description LEFT OUTER JOIN film_genre ON film_description.id=film_genre.film_id LEFT OUTER JOIN genre ON film_genre.genre_id=genre.id WHERE film_description.id=%s GROUP BY film_description.id;', (film_id,) )
    film=cursor.fetchone()
    cursor.execute('SELECT exam_review.*, exam_users.* FROM `exam_review` LEFT OUTER JOIN exam_users ON exam_users.id_us=exam_review.users_id WHERE exam_review.film_id=%s GROUP BY exam_review.id_rev;',(film_id,))
    reviews=cursor.fetchall()
    cursor.close()
    return render_template('films/show.html', film=film, reviews=reviews)

#для пользователя, отображение его рецензий
@app.route('/users/<int:user_id>/showrew')
@login_required
def reviews(user_id):
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute('SELECT film_description.name as name, exam_status.status as status, exam_review.text_field as text, exam_review.mark as mark FROM film_description RIGHT OUTER JOIN exam_review ON film_description.id=exam_review.film_id LEFT OUTER JOIN exam_status ON exam_review.status=exam_status.id WHERE exam_review.users_id=%s AND (exam_status.id="2" or exam_status.id="3");', (user_id, ))
    reviews=cursor.fetchall()
    cursor.close()
    return render_template('films/users/showrew.html', reviews=reviews)

PER_PAGE_2=5
@app.route('/users/reviewstab')
@login_required
def mod_review():
    page = request.args.get('page', 1, type= int)
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT COUNT(*) as count FROM exam_review WHERE exam_review.status="1";')
        total_strs= cursor.fetchone().count
    total_pages = math.ceil(total_strs/PER_PAGE_2)#округление до ближайшего числа
    pagination_inf = {
        'current_page': page,
        'total_pages': total_pages,
        'per_page': PER_PAGE_2
    }
    query = '''
     SELECT film_description.name as name, exam_users.last_name as userlast, exam_users.first_name as userfirst, exam_users.middle_name as usermid, exam_review.pr_date as date, exam_review.id_rev as id FROM film_description RIGHT OUTER JOIN exam_review ON film_description.id = exam_review.film_id LEFT OUTER JOIN exam_users ON exam_review.users_id=exam_users.id_us WHERE exam_review.status="1" ORDER BY date DESC LIMIT %s OFFSET %s; 
    '''
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute(query,(PER_PAGE_2, PER_PAGE_2*(page-1)))
    rev=cursor.fetchall()
    cursor.close()
    return render_template('films/users/reviewstab.html', rev=rev, pagination_inf=pagination_inf)

@app.route('/users<int:review_id>/control')
@login_required
def modif(review_id):
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute('SELECT film_description.name as name, exam_users.last_name as userlast, exam_users.first_name as userfirst, exam_users.middle_name as usermid, exam_review.pr_date as pr_date, exam_review.id_rev as id_rev, exam_review.mark as mark, exam_review.text_field as text FROM film_description RIGHT OUTER JOIN exam_review ON film_description.id = exam_review.film_id LEFT OUTER JOIN exam_users ON exam_review.users_id=exam_users.id_us WHERE id_rev=%s;',(review_id, ))
    review=cursor.fetchone()
    cursor.close()
    return render_template('films/users/control.html', review=review)

@app.route('/users/<int:review_id>/acceptmod',methods =['POST'])
@login_required
def acceptmod(review_id):    
    with mysql.connection.cursor(named_tuple= True) as cursor:
        try:
            cursor.execute('UPDATE exam_review SET exam_review.status="2" WHERE exam_review.id_rev=%s;', (review_id,))
        except connector.errors.DatabaseError as err:
            flash('При обновлении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return redirect(url_for('mod_review'))
        mysql.connection.commit()
        flash('Статус рецензии успешно обновлен. Рецензия была одобрена', 'success')
    return redirect(url_for('mod_review'))


@app.route('/users/<int:review_id>/rejectmod', methods =['POST'])
@login_required
def rejectmod(review_id):
    with mysql.connection.cursor(named_tuple= True) as cursor:
        try:
            cursor.execute('UPDATE exam_review SET exam_review.status="3" WHERE exam_review.id_rev=%s;', (review_id,))
        except connector.errors.DatabaseError as err:
            flash('При обновлении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return redirect(url_for('mod_review'))
        mysql.connection.commit()
        flash('Статус рецензии успешно обновлен. Рецензия была отклонена.', 'success')
    return redirect(url_for('mod_review'))


@app.route('/films/new')
@login_required
def new():
    return render_template('films/new.html', film={}, genre=load_genres())

@app.route('/films/create',methods =['POST'])
@login_required
def create():
    name = request.form.get('name') or None
    description = bleach.clean(request.form.get('description')) or None
    prod_year = request.form.get('prod_year') or None
    country = request.form.get('country') or None
    director = request.form.get('director') or None
    screenwriter = request.form.get('screenwriter') or None
    actors = request.form.get('actors') or None
    duration = request.form.get('duration') or None
    description=markdown.markdown(description)
    poster = request.files['poster']
    file_name = secure_filename(poster.filename)
    poster.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
    mime_type=poster.mimetype
    md5_hash = hashlib.md5(poster.read()).hexdigest()

    query1 = '''
        INSERT INTO film_description (name, description, prod_year, country, director, screenwriter, actors, duration)
        VALUES (%s, %s, %s, %s, %s, %s , %s , %s);'''
    query2='''
        SET @a=SELECT MAX(id) as id FROM `film_description`;
        INSERT INTO film_post( `id_film`, `file_name`, `MIME_type`, `MD5_hash`) VALUES (@a, %s, %s, %s);'''
    cursor = mysql.connection.cursor(named_tuple= True)
    try:
        cursor.execute(query1, (name, description, prod_year, country, director, screenwriter, actors, duration))
        cursor.execute('SELECT MAX(id) as id FROM `film_description`;')
        film_id=cursor.fetchone()
        cursor.execute(query2, (film_id, file_name, mime_type, md5_hash))
    except connector.errors.DatabaseError as err:
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        film={
                'name' : name,
                'description' : description,
                'prod_year' : prod_year,
                'country' : country,
                'director' : director,
                'screenwriter' : screenwriter,
                'actors' : actors,
                'duration' : duration,
        },
        mysql.connection.rollback()
        mysql.connection.commit()
        cursor.close()
        if request.form.get('genre'):
            for genre in request.form.get('genre'):
                cursor = mysql.connection.cursor(named_tuple=True)
                cursor.execute('SELECT * FROM `genre`;')
                gens= cursor.fetchall()
                for gen in gens:
                    if gen.name == genre:
                        query = ''' INSERT INTO film_genre (film_id, genre_id) VALUES (%s, %s);'''
                        cursor.execute('SELECT MAX(id) as id FROM `film_description`;')
                        film_id=cursor.fetchone()
                        cursor.execute(query, (film_id, gen.id))
                        mysql.connection.commit()
                        cursor.close()
        return render_template('films/new.html', film=film, genre=load_genres())
    flash(' Фильм был успешно добавлен', 'success')
    return redirect(url_for('index'))

@app.route('/media/images/<filename>')
def uploaded_posters(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

@app.route('/films/<int:film_id>/update',methods =['POST'])
@login_required
def update(film_id):
    name = request.form.get('name') or None
    description = request.form.get('description') or None
    prod_year = request.form.get('prod_year') or None
    country = request.form.get('country') or None
    director = request.form.get('director') or None
    screenwriter = request.form.get('screenwriter') or None
    actors = request.form.get('actors') or None
    try:
        duration = int(request.form.get('duration'))
    except ValueError:
        duration = None
    description=markdown.markdown(description)
    query = '''
        UPDATE film_description
        SET name= %s, description= %s, prod_year= %s, country= %s, director= %s, screenwriter= %s, actors= %s, duration= %s   
        WHERE id=%s;
    '''
    cursor = mysql.connection.cursor(named_tuple = True)
    try:
        cursor.execute(query, (name, description, prod_year, country, director, screenwriter, actors, duration))
    except connector.errors.DatabaseError as err:
        flash('При обновлении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        film={
                'id' : film_id,
                'name' : name,
                'description' : description,
                'prod_year' : prod_year,
                'country' : country,
                'director' : director,
                'screenwriter' : screenwriter,
                'actors' : actors,
                'duration' : duration
        }
        return render_template('films/edit.html', film=film, genre=load_genres())
    mysql.connection.commit()
    cursor.close()
    flash('Фильм успешно обновлен', 'success')
    return redirect(url_for('index'))



@app.route('/media/<filename>')
def posterimgs(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/films/<int:film_id>/delete', methods =['POST'])
@login_required
def delete(film_id):
    with mysql.connection.cursor(named_tuple= True) as cursor:
        try:
            cursor.execute('DELETE FROM `film_description` WHERE film_description.id = %s;', (film_id,))
        except connector.errors.DatabaseError as err:
            flash('Не удалось удалить запись', 'danger')
            return redirect(url_for('index'))
        mysql.connection.commit()
        flash('Запись была успешно удалена!', 'success')
    return redirect(url_for('index'))


@app.route('/films/<int:film_id>/make_review', methods =[ 'GET','POST'])
@login_required
def make_review(film_id):
    cursor = mysql.connection.cursor(named_tuple = True)
    if request.method== 'GET':
        return render_template('films/review.html')
    if request.method== 'POST':
        user_id = getattr(current_user, 'id', None)
        mark = request.form.get('mark') or None
        text_field = bleach.clean(request.form.get('text_field')) or None
        text_field=markdown.markdown(text_field)
        status = int(request.form.get('status')) or None
        query = '''
        INSERT INTO exam_review (film_id, users_id, mark, text_field, status) VALUES (%s, %s, %s, %s, %s); '''
        try:
            cursor.execute(query, ( film_id, user_id, mark, text_field, status))
        except connector.errors.DatabaseError as err:
            flash('Не удалось сохранить ваш отзыв. Проверьте корректность введённых данных.', 'danger')
            review={
                'mark' : mark,
                'tetx_field' : text_field,
                'status': status 
            }
            return render_template('films/review.html', review=review)
        mysql.connection.commit()
        cursor.close()
        flash('Ваш отзыв успешно добавлен', 'success')
    return redirect(url_for('show', film_id=film_id))

PER_PAGE = 10

@app.route('/')
def index():
    page = request.args.get('page', 1, type= int)
    with mysql.connection.cursor(named_tuple=True) as cursor:
        cursor.execute('SELECT count(*) AS count FROM film_description;')
        total_strs= cursor.fetchone().count
    total_pages = math.ceil(total_strs/PER_PAGE)#округление до ближайшего числа
    pagination_info = {
        'current_page': page,
        'total_pages': total_pages,
        'per_page': PER_PAGE
    }
    query = '''
     SELECT film_description.id as id, film_description.name as name, film_description.description as description, film_description.prod_year as prod_year,film_description.country as country, film_description.director as director, film_description.screenwriter as screenwriter,film_description.actors as actors, film_description.duration as duration, GROUP_CONCAT(genre.name) as genre FROM film_description LEFT OUTER JOIN film_genre ON film_description.id=film_genre.film_id LEFT OUTER JOIN genre ON film_genre.genre_id=genre.id GROUP BY film_description.id ORDER BY prod_year DESC LIMIT %s OFFSET %s; 
    '''
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute(query,(PER_PAGE, PER_PAGE*(page-1)) )
    films=cursor.fetchall()
    cursor.close()
    return render_template('index.html', films=films, number=counting_reviews(), user=users(), pagination_info= pagination_info)