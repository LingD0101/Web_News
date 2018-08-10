from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from config import config_name


def create_app(config):
    # app = Flask(__name__, template_folder="info/templates", static_folder="info/static")
    app = Flask(__name__)
    app.config.from_object(config_name[config])  # 从类中调用配置文件
    db = SQLAlchemy(app)
    Session(app)

    # 导入蓝图,并注册
    from info.module.news import new_blueprint
    app.register_blueprint(new_blueprint)
    return app