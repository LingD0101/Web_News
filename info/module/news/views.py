from flask import session, render_template
from . import api


@api.route('/')
def index():
    session['name'] = 'LingD'
    return render_template('news/index.html')
