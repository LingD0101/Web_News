import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session  # 使用扩展包实现session信息的储存
from config import config_name, Config
from redis import StrictRedis
from flask_wtf import CSRFProtect, csrf

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("./logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
# 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)

db = SQLAlchemy()
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)


def create_app(config):
    # app = Flask(__name__, template_folder="info/templates", static_folder="info/static")
    app = Flask(__name__)
    app.config.from_object(config_name[config])  # 从类中调用配置文件

    db.init_app(app)

    Session(app)
    # 开启csrf保护
    CSRFProtect(app)

    # 设置token,用请求钩子方法,每个请求都会携带csrf
    @app.after_request
    def after_request(response):
        csrf_token = csrf.generate_csrf()
        response.set_cookie('csrf_token',csrf_token)
        return response

    # 导入主页蓝图,并注册
    from info.modules.news import new_blueprint
    app.register_blueprint(new_blueprint)
    # 导入注册页面蓝图
    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)

    return app
