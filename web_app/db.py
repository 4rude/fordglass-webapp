# This app holds database functionality
import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

# This function creates a conection with the app database, and returns a special object (g) which stores data during a request.
def get_db():
	""" Current_app is an object which is a procy to the application handling the current request. Used when an application 
			  follows a application factory patter, or blueprints + extensions. """

	if 'db' not in g:
		g.db = sqlite3.connect(
			
			current_app.config['DATABASE'],
			detect_types = sqlite3.PARSE_DECLTYPES
		)

		g.db.row_factory = sqlite3.Row

	return g.db

def close_db(e = None):

	db = g.pop('db', None)

	if db is not None:
		db.close()

def init_db(): 

	db = get_db()

	with current_app.open_resource('schema.sql') as f:
		db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
	""" Clear the existing data and create new tables. """

	init_db()
	click.echo('Initialized the database.')

def init_app(app):
	""" This function registers these functions with application instance. """

	# Calls the function when cleaning up after returning a response.
	app.teardown_appcontext(close_db)

	# Adds a new command that can be called with the flask CLI.
	app.cli.add_command(init_db_command)

