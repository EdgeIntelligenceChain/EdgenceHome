from flask import render_template
from . import main


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/masternodes')
def masternodes():
	return render_template('masternodes.html')

