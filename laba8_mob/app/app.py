from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
import jwt
import datetime
import base64

app = Flask(__name__)
application = app
app.config.from_pyfile('config.py')


with open("/home/std/web-2021-1/laba8_mob/app/static/img/12.jpg", "rb") as img:
    encoded_string = base64.b64encode(img.read())


def get_users():
    return [{'user_id': '1', 'login': 'login', 'password': 'qwerty'}]

def check_for_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'no access!'}), 403
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'message': 'Invalid token'}), 403
        return func(*args, **kwargs)
    return wrapped


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/secret_page')
@check_for_token
def secret_page():
    return jsonify({'current_time': datetime.datetime.now(), 'message': 'Valikova 191-351', 'img': encoded_string.decode('utf-8')})

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.args.get('login') or request.form.get('login')
    password = request.args.get('password') or request.form.get('password')
    if username and password:
        for user in get_users():
            if user['login'] == username and user['password'] == password:
                session['logged_in'] = True
                token = jwt.encode({
                    'user': username,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=90)
                },
                app.config['SECRET_KEY'])
                # return redirect(url_for('secret_page.html'+'?token='+token))
                # return render_template('secret_page.html'+'?token='+token)
                return jsonify({'token': token})
            else:
                return jsonify({'message': 'no access'}), 403
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
