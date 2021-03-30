from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from app import mysql
from users_policy import UsersPolicy

bp= Blueprint('auth', __name__, url_prefix='/auth')

class User(UserMixin):
    def __init__(self, user_id, login, role, last_name, first_name, middle_name):
        super().__init__()
        self.id=user_id
        self.login=login
        self.role=role
        self.last_name=last_name
        self.first_name=first_name
        self.middle_name=middle_name

    def can(self, action, record = None):
        policy = UsersPolicy(record= record)
        method = getattr(policy, action, None)
        if method:
            return method()
        return False

def user_info(user_id):
    if user_id is None:
        return None
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute('SELECT * FROM exam_users WHERE id_us = %s;', (user_id,))
    user=cursor.fetchone()
    cursor.close()
    return user

def check_rights(action):
    def decorator(funk):
        @wraps(funk)
        def wrapper(*args, **kwargs):#функция обертка
            user = user_info(kwargs.get('user_id'))
            if not current_user.can(action, record= user):
                flash('У вас недостаточно прав для доступа к данной странице', 'danger')
                return redirect(url_for('index'))
            return funk(*args, **kwargs) 
        return wrapper
    return decorator  


def load_user(user_id):
    cursor = mysql.connection.cursor(named_tuple= True)
    cursor.execute('SELECT * FROM exam_users WHERE id_us = %s;', (user_id,))
    db_user=cursor.fetchone()
    cursor.close()
    if db_user:
        return User(user_id= db_user.id_us, login = db_user.login, role=db_user.role, last_name=db_user.last_name, first_name=db_user.first_name, middle_name=db_user.middle_name)
    return None

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        login=request.form.get('login')
        password = request.form.get('password')
        if login and password:
            cursor = mysql.connection.cursor(named_tuple= True)
            cursor.execute( 'SELECT * FROM exam_users WHERE login = %s AND hash_password = SHA2(%s, 256);', (login, password))
            db_user = cursor.fetchone()
            cursor.close()
            if db_user:
                user = User(user_id=db_user.id_us, login=db_user.login, role=db_user.role, last_name=db_user.last_name, first_name=db_user.first_name, middle_name=db_user.middle_name)
                login_user(user)
                flash('Вы успешно аутентифицировались', 'success')
                next = request.args.get('next')
                return redirect(next or url_for('index'))
        flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Для выполнения данного действия необходимо пройти процедуру аутентификации.'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)