from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_login import login_required, current_user
from mysql_db import MySQL
import mysql.connector as connector

app=Flask(__name__)

application=app
app.config.from_pyfile('config.py')

mysql=MySQL(app)