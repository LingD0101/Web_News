from flask import session, render_template, current_app
from . import new_blueprint


@new_blueprint.route('/')
def index():
    session['name'] = 'LingD'
    return render_template('news/index.html')


# 创建ico小图标
@new_blueprint.route("/favicon.ico")
def favicon():
    # current_app默认创建static,需要补充ico路径到url
    return current_app.send_static_file("news/favicon.ico")