from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

def login(mysql):
	msg=""
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE username = % s AND password = % s', (username, password, ))
		users = cursor.fetchone()
		if users:
			session['loggedin'] = True
			session['id'] = users['id']
			session['username'] = users['username']
			msg = 'Logged in successfully !'
			cursor.execute('SELECT * FROM pretest WHERE id = % s', (users['id'], ))
			users = cursor.fetchone()
			
			if users['has_completed']==1:
				return render_template('index.html', msg = msg)
			else:
				return render_template('tp.html')
		else:
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)

def logout(mysql):
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

def register(mysql):
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
		users = cursor.fetchone()
		if users:
			msg = 'users already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			cursor.execute('SELECT * FROM users WHERE username = % s AND password = % s', (username, password,))
			users = cursor.fetchone()
			#print(type(users['id']))
			cursor.execute('INSERT INTO pretest VALUES ( %s, 0)', (users['id'], ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
			return render_template('tp.html', msg = msg)
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	
	return render_template('register.html', msg = msg)