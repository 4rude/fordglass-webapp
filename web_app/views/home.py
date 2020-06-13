from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
import os

from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from .auth import login_required
from web_app.db import get_db
from web_app.mail import send_email


# Blueprints organize related views and code. The views and code are registered with the blueprint, 
# and the blueprint is registered with the application instance. This blueprint doesn't require
# a url_prefix because its the main page of the site. This controller may be used for
# the entirety of the website, minus any sort of shopping cart. 
bp = Blueprint('home', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
	# If a visitor sends in a request for corrospondence using the Home page form
	if request.method == 'POST':

		# Put user input into variables
		visitor_name = request.form['visitor_name']
		visitor_email = request.form['visitor_email']
		visitor_subject = request.form['visitor_subject']
		visitor_message = request.form['visitor_message']

		send_email(visitor_name, visitor_email, visitor_subject, visitor_message)

		return redirect(url_for('home.index'))

	else:
		# Create database object to query
		db = get_db()

		# Execute the select statement which gathers all the records of product. Order by category -> subcategory
		items = db.execute(
			'SELECT i.id, i.author_id, i.created, i.item_name, i.picture_url, i.description, c.category, c.sub_category'
			' FROM user u JOIN item i ON u.id = i.author_id JOIN category c ON i.category_id = c.id'
			' ORDER BY c.category ASC, c.sub_category ASC'
		).fetchall()

	return render_template('home.html', items=items)


