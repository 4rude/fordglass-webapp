from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
import os

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from .auth import login_required
from web_app.db import get_db

# Allowed extensions for files
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Giving this a url prefix, like the auth view, so 
bp = Blueprint('cms', __name__, url_prefix = '/cms')

# Determines if the filename is safe
def allowed_file(filename):
  return '.' in filename and \
    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/index')
@login_required
def index():
	db = get_db()

	# Execute the select statement which gathers all the records of product
	items = db.execute(
		'SELECT i.id, i.author_id, i.created, i.item_name, i.picture_url, i.description, c.category, c.sub_category'
		' FROM user u JOIN item i ON u.id = i.author_id JOIN category c ON i.category_id = c.id'
		' ORDER BY i.created DESC'
	).fetchall()

	return render_template('cms/index.html', items=items)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():

	# If the submit buttom is pressed and HTML request is post...
	if request.method == 'POST':
		item_name = request.form['item_name']
		picture_url = request.form['picture_url']
		description = request.form['description']
		category_id = request.form['category_id']
		picture = request.files['picture']
		error = None

		# These are the different error detecting if statements
		if 'picture' not in request.files:
			error = 'No file detected.'
		if not allowed_file(picture.filename):
			error = 'That file name is not allowed.'
		if not picture.filename: 
			error = 'A file name is required.'
		if not picture_url:
			error = 'A picture url is required.'


		if error is not None:
			flash(error)
		else:
			# If there are no errors, insert the data from the form into the database
			db = get_db()
			db.execute(
				'INSERT INTO item (author_id, item_name, picture_url, description, category_id)'
				' VALUES (?, ?, ?, ?, ?)',
				(g.user['id'], item_name, picture_url, description, category_id)
			)
			db.commit()

			filename = secure_filename(picture.filename)
			picture.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

			return redirect(url_for('cms.index'))

	else:

		# If the HTML request if GET, return the form page with the categories drop-down 
		# available for the author
		db = get_db()
	
		categories = db.execute(
			'SELECT id, category, sub_category'
			'	FROM category'
			'	ORDER BY category ASC, sub_category ASC'
		).fetchall()

	return render_template('cms/create.html', categories=categories)


def get_item(argId, check_author=True):
	""" This function fetches a item by id, and checks if the author matches the logged in user. """
	db = get_db()
	item = db.execute(
		'SELECT i.id, i.author_id, i.created, i.item_name, i.picture_url, i.description, c.category, c.sub_category'
		' FROM user u JOIN item i ON u.id = i.author_id JOIN category c ON i.category_id = c.id'
		' WHERE i.id = ?',
		(argId,)
	).fetchone()

	# 404 error means not found
	if item is None:
		abort(404, "Post id {0} doesn't exist.".format(argId))

	# 403 error means forbidden
	if check_author and item['author_id'] != g.user['id']:
		abort(403)
		#item['author_id']
	return item


# Flask will capture the id in the URL and pass it to argId argument as an integer.
@bp.route('/<int:argId>/update', methods=['GET', 'POST'])
@login_required
def update(argId):
	""" This view updates a single item in the database. TODO: Add the picture associated 
	with the item on to the delete form or view. """
	item = get_item(argId)

	if request.method == 'POST':
		item_name = request.form['item_name']
		picture_url = request.form['picture_url']
		description = request.form['description']
		category_id = request.form['category_id']
		error = None

		if not item_name:
			error = 'A name is required for the item.'

		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute(
				'UPDATE item SET item_name = ?, picture_url = ?, description = ?, category_id = ?'
				' WHERE id = ?',
				(item_name, picture_url, description, category_id, argId)
			)

			db.commit()
			return redirect(url_for('cms.index'))

	else:
		# If the HTML request if GET, return the form page with the categories drop-down 
		# available for the author
		db = get_db()
	
		categories = db.execute(
			'SELECT id, category, sub_category'
			'	FROM category'
			'	ORDER BY category ASC, sub_category ASC'
		).fetchall()

	# This may or may not be correct. The original has the post (in this case item) object being
	# passed through to the rendered template. 
	# Original: return render_template('blog/update.html', post=post)
	return render_template('cms/update.html', categories=categories, item=item)


@bp.route('/<int:argId>/delete', methods=['POST',])
@login_required
def delete(argId):
	""" The delete view doesnt have its own template. Its a part of the update.html page, and
	posts to the /<id>/delete URL. It will only handle the post method and redirect to the 
	index view. """

	get_item(argId)
	db = get_db()
	db.execute('DELETE FROM item WHERE id = ?', (argId,))
	db.commit()
	return redirect(url_for('cms.index'))



