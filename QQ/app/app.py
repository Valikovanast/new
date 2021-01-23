from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_login import login_required, current_user
from mysql_db import MySQL
import mysql.connector as connector


app= Flask(__name__)
application = app

app.config.from_pyfile('config.py')
mysql = MySQL(app)

from auth import bp as auth_bp, init_login_manager, check_rights
from visits import bp as visits_bp

init_login_manager(app)
app.register_blueprint(auth_bp)
app.register_blueprint(visits_bp)

@app.before_request
def save_visit_info():
    user_id= getattr(current_user, 'id', None)
    query = 'INSERT INTO visit_logs (path, user_id) VALUES (%s, %s);'
    with mysql.connection.cursor(named_tuple= True) as cursor:
        try:
            cursor.execute(query, (request.path, user_id))
            mysql.connection.commit()
        except:
            pass


def load_roles():
    cursor = mysql.connection.cursor(named_tuple = True)
    cursor.execute('SELECT id, name FROM roles2;')
    roles= cursor.fetchall()
    cursor.close()
    return roles

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users')
def users():
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute('SELECT users2.*, roles2.name AS role_name FROM users2 LEFT OUTER JOIN roles2 ON users2.role_id = roles2.id;')
    users = cursor.fetchall()
    cursor.close()
    return render_template('users/index.html', users= users)


@app.route('/users/<int:user_id>')
@check_rights('show')
@login_required
def show(user_id):
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute('SELECT * FROM users2 WHERE id = %s;', (user_id,))
    user=cursor.fetchone()
    cursor.execute('SELECT * FROM roles2 WHERE id = %s;', (user.role_id,))
    role=cursor.fetchone()
    cursor.close()
    return render_template('users/show.html', user= user, role =role ) 


@app.route('/users/new')
@check_rights('new')
@login_required
def new():
    return render_template('users/new.html', user={}, roles= load_roles())



@app.route('/users/<int:user_id>/edit')
@check_rights('edit')
@login_required
def edit(user_id):
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute('SELECT * FROM users2 WHERE id = %s;', (user_id,))
    user=cursor.fetchone()
    cursor.close()
    return render_template('users/edit.html', user=user, roles= load_roles())

@app.route('/users/create',methods =['POST'])
@check_rights('new')
@login_required
def create():
    login = request.form.get('login') or None
    password = request.form.get('password') or None
    first_name = request.form.get('first_name') or None
    last_name = request.form.get('last_name') or None
    middle_name = request.form.get('middle_name') or None
    try:
        role_id = int(request.form.get('role_id'))
    except ValueError:
        role_id= None
    query = '''
        INSERT INTO users2 (login, password_hash, first_name, last_name, middle_name, role_id)
        VALUES (%s, SHA2(%s,256), %s, %s, %s, %s);
    '''
    cursor = mysql.connection.cursor(named_tuple= True)
    try:
        cursor.execute(query, (login, password, first_name, last_name, middle_name, role_id))
    except connector.errors.DatabaseError as err:
        flash('Введены некорректные данные. Ошибка сохранения.', 'danger')
        user={
                'login' : login,
                'password' : password,
                'first_name' : first_name,
                'last_name' : last_name,
                'middle_name' : middle_name,
                'role_id' : role_id
        }
        return render_template('/users/new.html', user= user, roles= load_roles())
    mysql.connection.commit()
    cursor.close()
    flash(f'Пользователь {login} был успешно создан.', 'success')
    return redirect(url_for('users'))

@app.route('/users/<int:user_id>/update',methods =['POST'])
@check_rights('edit')
@login_required
def update(user_id):
    first_name = request.form.get('first_name') or None
    last_name = request.form.get('last_name') or None
    middle_name = request.form.get('middle_name') or None
    role_id = request.form.get('role_id') or None
    query = '''
        UPDATE users2 SET first_name=%s, last_name=%s, middle_name=%s, role_id=%s 
        WHERE id=%s;
    '''
    cursor = mysql.connection.cursor(named_tuple = True)
    try:
        cursor.execute(query, (first_name, last_name, middle_name, role_id))
    except connector.errors.DatabaseError as err:
        flash('Введены некорректные данные. Ошибка сохранения.', 'success')
        user={
                'id' : user_id,
                'first_name' : first_name,
                'last_name' : last_name,
                'middle_name' : middle_name,
                'role_id' : role_id
        }
        return render_template('/users/edit.html', user= user, roles= load_roles())
    mysql.connection.commit()
    cursor.close()
    flash(f'Пользователь {first_name} был успешно обновлен.', 'success')
    return redirect(url_for('users'))

@app.route('/users/<int:user_id>/delete', methods =['POST'])
@check_rights('delete')
@login_required
def delete(user_id):
    with mysql.connection.cursor(named_tuple= True) as cursor:
        try:
            cursor.execute('DELETE FROM users2 WHERE id = %s;', (user_id,))
        except connector.errors.DatabaseError as err:
            flash('Не удалось удалить запись', 'danger')
            return redirect(url_for('users'))
        mysql.connection.commit()
        flash('Запись была успешно удалена!', 'success')
    return redirect(url_for('users'))