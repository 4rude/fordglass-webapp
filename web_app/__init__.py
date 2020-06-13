import os
from flask import Flask
from flask_mail import Mail

# Creating the mail object before the create_app() function
mail = Mail()

def create_app(test_config = None):
	# This is where the app is initialized
	app = Flask(__name__, instance_relative_config = True)
	
	# Object for testing 
	app.config.from_mapping(
		SECRET_KEY = 'dev',
		DATABASE = os.path.join(app.instance_path, 'web_app.sqlite'),
	)

	# Calling: export FLASK_ENV=development
	# before the flask application is ran via the CLI will 
	# make the application run is development mode
	if test_config is None:
		# Should allow us to put configuration variables in config.py and instance/config.py files
		app.config.from_object('config')
		# app.config.from_pyfile('config.py', silent=True)
	else:
		app.config.from_mapping(test_config)

	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# Test page
	@app.route('/hello')
	def hello():
		return 'Hello, world!'
	
	# .init_app() is used to safely bind a database handler to a Flask app
	from . import db 
	db.init_app(app)

	# Initialize the mail object
	mail.init_app(app)

	# Registering views with the Flask app here
	from web_app.views import auth
	app.register_blueprint(auth.bp)

	from web_app.views import cms
	app.register_blueprint(cms.bp)

	from web_app.views import category
	app.register_blueprint(category.bp)

	from web_app.views import home
	app.register_blueprint(home.bp)
	app.add_url_rule('/', endpoint='index')

	return app 