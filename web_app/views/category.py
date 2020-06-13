from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
import os

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from .auth import login_required
from web_app.db import get_db

# Giving this a url prefix, like the auth view, so 
bp = Blueprint('category', __name__, url_prefix = '/category')

@bp.route('/createcategory', methods=['GET', 'POST'])
@login_required
def createcategory():
	""" This view will display a simple page to create a sub-category based off of
	the categories available. The GET request portion will display the page with the categories
	available to select, with a text box next to it. The POST request portion will take the
	category selected and the sub_category and add it to the database. """
	if request.method == 'POST':
		category = request.form['category']
		sub_category = request.form['sub_category']
		error = None


		if not category:
			error = 'A category name must be selected.'

		if not sub_category:
			error = 'A subcategory name must be selected'

		# Ensure that the subcategory name is inserted into the database as all lowercase
		sub_category = sub_category.lower()

		if error is not None:
			flash(error)
		else:
			# If there are no errors, insert the data from the form into the database
			db = get_db()
			db.execute(
				'INSERT INTO category (category, sub_category)'
				' VALUES (?, ?)',
				(category, sub_category)
			)
			db.commit()

			return redirect(url_for('cms.index'))

	return render_template('category/createcategory.html')
	


@bp.route('/updatecategory', methods=['GET', 'POST'])
@login_required
def updatecategory():
	""" This view will handle updating the subcategory, if the name needs to be changed. """
	if request.method == 'POST':
		category_id = request.form['category_id']
		sub_category = request.form['sub_category']
		error = None

		if not sub_category:
			error = 'A new name is required for the subcategory.'

		if not category_id:
			error = 'A category must be selected.'

		if error is not None:
			flash(error)
		else:
			db = get_db()
			db.execute(
				'UPDATE category SET sub_category = ?'
				' WHERE id = ?',
				(sub_category, category_id)
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

	return render_template('category/updatecategory.html', categories=categories)

@bp.route('/deletecategory', methods=['GET', 'POST'])
@login_required
def deletecategory():
	""" This function will not have its own view, it will handle the delete input from the HTML
	category_delete page. Very similar to the delete() view in the cms.py page, but it has its 
	own view. """
	if request.method == 'POST':

		category_id = request.form['category_id']

		db = get_db()
		db.execute('DELETE FROM category WHERE id = ?', (category_id,))
		db.commit()
		return redirect(url_for('cms.index'))

	else:
		# If this is a get request, populate the categories object and pass it to the 
		# category_delete view. Also render the category_delete template. 
		db = get_db()
	
		categories = db.execute(
			'SELECT id, category, sub_category'
			'	FROM category'
			'	ORDER BY category ASC, sub_category ASC'
		).fetchall()

	return render_template('category/deletecategory.html', categories=categories)
