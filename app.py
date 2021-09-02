# Store this code in 'app.py' file

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import Identification
import PretestUtil

app = Flask(__name__)


app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456789'
app.config['MYSQL_DB'] = 'gujaratishikshak'

mysql = MySQL(app)

@app.route('/')
def landing():
	return render_template('landing.html')

@app.route('/pretest', methods =['GET', 'POST'])
def pretest():
	return PretestUtil.pretest()


@app.route('/login', methods =['GET', 'POST'])
def login():
	return Identification.login(mysql)

@app.route('/logout')
def logout():
	return Identification.logout(mysql)

@app.route('/register', methods =['GET', 'POST'])
def register():
	return Identification.register(mysql)
	
if __name__=="__main__":
    app.run(debug=True)