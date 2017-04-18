from flask.ext.mail import Message, Mail
from flask import render_template

# email server
MAIL_SERVER = 'smtp.mail.ru'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = False
MAIL_USERNAME = 'uva24'
MAIL_PASSWORD = 'erhntktrjv12'

#для почты    
ADMINS = ['uva24@mail.ru']

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = text_body
    msg.html = html_body
    Mail.send(msg)

def follower_notification(followed, follower):
    send_email("Hello!" % follower.kontakt,
        ADMINS[0],
        [followed.mail],
        render_template("text_body.txt"),
        render_template("html_body.html"))
    