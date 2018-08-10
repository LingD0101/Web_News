from flask import session, render_template
from . import new_blueprint


@new_blueprint.route('/')
def index():
    session['name'] = 'LingD'
    return render_template('news/index.html')
