"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os
from flask import Flask, render_template, request, redirect, url_for
import logging
from slackclient import SlackClient

token = "xoxp-48970123489-48964881879-50048816096-fd79da89e6"      # found at https://api.slack.com/web#authentication
sc = SlackClient(token)


app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')


###
# Routing for your application.
###

@app.route('/')
def home():
    test= sc.api_call("api.test")
    channels= sc.api_call("channels.list", token=token)
    print channels
    logging.debug(channels)
    # print sc.api_call(
    #     "chat.postMessage", channel="#general", text="Hello from Python! :tada:",
    #     username='pybot', icon_emoji=':robot_face:'
    # )
    """Render website's home page."""
    return render_template('home.html', test=test, channels=channels,msglist='')

@app.route('/switchmsg', methods=['GET', 'POST'])
def foo(x=None, y=None):
    # do something to send email
    id=request.form['id']
    channels= sc.api_call("channels.list", token=token)
    msglist= sc.api_call("channels.history",token=token, channel=id)
    return render_template('home.html', channels=channels,msglist=msglist)

@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')


###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
