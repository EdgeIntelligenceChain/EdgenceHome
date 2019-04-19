from flask import render_template,url_for,redirect
from . import main


@main.route('/')
def index():
    print(url_for('main.static',filename='1.jpg'))
    return render_template('index.html')

@main.route('/masternodes')
def masternodes():
	return redirect(url_for("explorer.blockexplorer"))

