# This app holds email functionality
from flask_mail import Message
from flask import current_app
from web_app import mail  # you can now import the Mail() object

def send_email(name, email, subject, message_body):
	# Initialize and fill the message object
	message = Message()

	message.body = "Name: " + name + " Visitor email address: " + email + " Message: " + message_body
	message.subject = subject

	# Set to Henrik's business email
	message.recipients = ["henriksemail@gmail.com"]

	# Set to default email
	message.sender = current_app.config['MAIL_DEFAULT_SENDER']

	mail.send(message)
