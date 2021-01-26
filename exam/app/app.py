import os
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_login import login_required, current_user
from mysql_db import MySQL
from werkzeug.utils import secure_filename
import mysql.connector as connector

app=Flask(__name__)

application=app
app.config.from_pyfile('config.py')

mysql=MySQL(app)

from auth import bp as auth_bp, init_login_manager


init_login_manager(app)
app.register_blueprint(auth_bp)



def load_reviews(user_id, film_id):
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM `exam_review` WHERE users_id=%s AND film_id=%s;',(user_id, film_id,))
    review=cursor.fetchone()
    cursor.close()
    return review

def load_films(film_id):
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM `film_description` WHERE film_description.id=%s;',(film_id,))
    film=cursor.fetchone()
    cursor.close()
    return film

def load_status(status_id):
    cursor = mysql.connection.cursor(named_tuple=True)
    cursor.execute('SELECT * FROM exam_status WHERE id=%s;',(status_id,))
    status=cursor.fetchone()
    cursor.close()
    return status


@app.route('/')
def index():
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute('SELECT film_description.id as id, film_description.name as name, film_description.description as description, film_description.prod_year as prod_year,film_description.country as country, film_description.director as director, film_description.screenwriter as screenwriter,film_description.actors as actors, film_description.duration as duration, GROUP_CONCAT(genre.name) as genre, COUNT(exam_review.film_id) as count FROM film_description LEFT OUTER JOIN film_genre ON film_description.id=film_genre.film_id LEFT OUTER JOIN genre ON film_genre.genre_id=genre.id LEFT OUTER JOIN exam_review ON exam_review.film_id=film_description.id GROUP BY film_description.id ORDER BY prod_year DESC;')
    films = cursor.fetchall()
    cursor.close()
    return render_template('index.html', films=films)
"""
@app.route('/users')
def users():
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute('SELECT exam_users.*, roles_for_films.name AS role_name FROM users LEFT OUTER JOIN roles_for_films ON users.role_id = roles_for_films.id;')
    users = cursor.fetchall()
    cursor.close()
    return render_template('index.html', users= users)
"""

@app.route('/films/<int:film_id>/edit')
@login_required
def edit(film_id):
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute('SELECT film_description.*, GROUP_CONCAT(genre.name) as genre FROM film_description LEFT OUTER JOIN film_genre ON film_description.id=film_genre.film_id LEFT OUTER JOIN genre ON film_genre.genre_id=genre.id WHERE film_description.id=%s GROUP BY film_description.id;',(film_id,))
    film=cursor.fetchone()
    cursor.close()
    return render_template('films/edit.html', film=film)

@app.route('/films/<int:film_id>')
@login_required
def show(film_id):
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute('SELECT film_description.*, GROUP_CONCAT(genre.name) as genre FROM film_description LEFT OUTER JOIN film_genre ON film_description.id=film_genre.film_id LEFT OUTER JOIN genre ON film_genre.genre_id=genre.id WHERE film_description.id=%s GROUP BY film_description.id;', (film_id,) )
    film=cursor.fetchone()
    cursor.close()
    return render_template('films/show.html', film=film)


@app.route('/users/<int:film_id>/review')
@login_required
def review(film_id):
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute('SELECT * FROM exam_review WHERE film_id=%s;',(film_id,))
    review=cursor.fetchone()
    #cursor.execute('SELECT * FROM exam_users WHERE id = %s;', (review.user_id,))
    #user = cursor.fetchone()
    cursor.close()
    return render_template('users/review.html', review = review )


@app.route('/films/new')
@login_required
def new():
    return render_template('films/new.html', film={})


@app.route('/films/create',methods =['POST'])
@login_required
def create():
    name = request.form.get('name') or None
    genre = request.form.get('genre') or None
    description = request.form.get('description') or None
    prod_year = request.form.get('prod_year') or None
    country = request.form.get('country') or None
    director = request.form.get('director') or None
    screenwriter = request.form.get('screenwriter') or None
    actors = request.form.get('actors') or None
    duration = request.form.get('duration') or None
    query = '''
        INSERT INTO film_description (name, description, prod_year, country, director, screenwriter, actors, duration)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    '''
    cursor = mysql.connection.cursor(named_tuple= True)
    try:
        cursor.execute(query, (name, description, prod_year, country, director, screenwriter, actors, duration))
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
                'duration' : duration
        }
        return render_template('films/new.html', film=film)
    mysql.connection.commit()
    cursor.close()
    flash(' Фильм был успешно добавлен', 'success')
    return redirect(url_for('index'))

"""
@app.route('/films/create', method=['POST'])
@login_required
def add_post():
    post = request.files.get('poster')
    img = None
    if post and post.filename:
        post_server = ImageSaver(post)
        img = post_server.save()


    if img:
        img_server.bind_to_object(course)

    flash('Фильм был успешно добавлен', 'success')

    return redirect(url_for('index.html'))

"""


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
    duration = request.form.get('duration') or None
    query = '''
        UPDATE film_description
        SET name= %s, description= %s, prod_year= %s, country= %s, director= %s, screenwriter= %s, actors= %s, duration= %s   
        WHERE id=%s;
    '''
    cursor = mysql.connection.cursor(named_tuple = True)
    try:
        cursor.execute(query, (id, name, description, prod_year, country, director, screenwriter, actors, duration))
    except connector.errors.DatabaseError as err:
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        film={
                'id' : id,
                'name' : name,
                'description' : description,
                'prod_year' : prod_year,
                'country' : country,
                'director' : director,
                'screenwriter' : screenwriter,
                'actors' : actors,
                'duration' : duration
        }
        return render_template('films/edit.html', film=film)
    mysql.connection.commit()
    cursor.close()
    flash('Фильм успешно обновлен', 'success')
    return redirect(url_for('index'))


@app.route('/films/<int:film_id>/delete', methods =['POST'])
@login_required
def delete(film_id):
    with mysql.connection.cursor(named_tuple= True) as cursor:
        try:
            cursor.execute('DELETE FROM film_description WHERE id = %s;', (film_id,))
        except connector.errors.DatabaseError as err:
            flash('Не удалось удалить запись', 'danger')
            return redirect(url_for('films'))
        mysql.connection.commit()
        flash('Запись была успешно удалена!', 'success')
    return redirect(url_for('films'))


@app.route('/users/<int:film_id>/review',methods =['POST'])
@login_required
def make_review(film_id):
    mark = request.form.get('mark') or None
    text_field = request.form.get('text_field') or None
    query = '''
        INSERT INTO exam_review (mark, text_field)
        VALUES (%s, %s);
    '''
    cursor = mysql.connection.cursor(named_tuple = True)
    try:
        cursor.execute(query, ( text_field, mark))
    except connector.errors.DatabaseError as err:
        flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        review={
                'tetx_field' : text_field,
                'mark' : mark
        }
        return render_template('users/review.html', review=review)
    mysql.connection.commit()
    cursor.close()
    flash('Ваш отзыв успешно добавлен', 'success')
    return redirect(url_for('index'))

"""
@app.route('/images/<image_id>')
def image(image_id):
    img = Image.query.get(image_id)
    if img is None:
        abort(404)
    return send_from_directory(app.config['UPLOAD_FOLDER'], img.storage_filename)



    def html(self):
        return markdown.markdown(self.text)
        """