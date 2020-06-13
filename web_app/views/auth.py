import functools
from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for
	)
from werkzeug.security import generate_password_hash, check_password_hash
from web_app.db import get_db

# Blueprints organize related views and code. The views and code are registered with the blueprint, 
# and the blueprint is registered with the application instance. 
bp = Blueprint('auth', __name__, url_prefix = '/auth')

@bp.route('/register', methods = ('GET', 'POST'))
def register():
	""" This function requests the form values of username and password. It then
	creates a database variable and an error variable for storing the username and passwords 
	from the form, and any errors to be flashed in the error var. If there is no error, the 
	user is added to the database. If there is, it flashed the error and returns the user to
	the register page. """
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		db = get_db()
		error = None

		if not username:
			error = 'Username is required.'
		elif not password:
			error = 'Password is required'
		elif db.execute(
			'SELECT id FROM user where username = ?',
			(username,)
		).fetchone() is not None:
			error = 'User {} is already registered.'.format(username)

		if error is None:
			db.execute(
				'INSERT INTO user (username, password) VALUES (?, ?)',
				(username, generate_password_hash(password))
			)
			db.commit()
			return redirect(url_for('auth.login'))

		flash(error)

	return render_template('auth/register.html')

@bp.route('/login', methods = ('GET', 'POST'))
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']

		db = get_db()
		error = None
		user = db.execute(
			'SELECT * FROM user WHERE username = ?', (username,)
		).fetchone()

		if user is None:
			error = 'Incorrect username.'
		elif not check_password_hash(user['password'], password):
			error = 'Incorrect password.'

		if error is None:
			session.clear()
			session['user_id'] = user['id']
			return redirect(url_for('cms.create'))

		flash(error)

	return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
	""" This function gets the user id from the session dict. It then makes 
	it available to others views. It does this my adding the user_id to the
	special 'g' object. """
	user_id = session.get('user_id')

	if user_id is None:
		g.user = None
	else: 
		g.user = get_db().execute(
			'SELECT * FROM user WHERE id = ?', (user_id,)
		).fetchone()

@bp.route('/logout')
def logout():
	""" This function removes the user_id from the session """
	session.clear()
	return redirect(url_for('index'))

def login_required(view):
	""" This decorator returns a new view function that wraps the original view its 
	applied to. It checks if a user is logged in and redirects to the login page if not. """
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for('auth.login'))

		return view(**kwargs)
	return wrapped_view



