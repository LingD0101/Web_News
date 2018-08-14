from flask import session, render_template, current_app
from . import new_blueprint
from info.models import User


@new_blueprint.route('/')
def index():
    """
    检查用户登陆界面
    1.尝试通过session对象从redis获取用户ID
    2.通过id查找用户信息
    3.如果有信息就返回,没有就返回none
    """
    user_id = session.get('user_id')
    user = None
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)

    data = {
        'user_info': user.to_dict() if user else None
    }
    return render_template('news/index.html', data=data)


# 创建ico小图标
@new_blueprint.route("/favicon.ico")
def favicon():
    # current_app默认创建static,需要补充ico路径到url
    return current_app.send_static_file("news/favicon.ico")
