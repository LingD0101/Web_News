from flask import Flask, session, render_template
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import redis

app = Flask(__name__, template_folder="info/templates", static_folder="info/static")


class Config(object):
    DEBUG = True  # 设置debug
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost"  # 设置绑定数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 追踪

    SECRET_KEY = "1vbLyW75/dM3E94CLq7HHor3e2nvMC1Nw0+0OKj8I0i3kSbv4PSEbg=="
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    SESSION_TYPE = 'redis'  # 制定session保存到redis
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用redis的实例
    SESSION_USE_SIGNER = True  # 签名加密
    PERMANENT_SESSION_LEFETIME = 86400


app.config.from_object(Config)  # 从类中调用配置文件
db = SQLAlchemy(app)
manage = Manager(app)
Session(app)


@app.route('/')
def index():
    session['name'] = 'LingD'
    return render_template('news/index.html')


if __name__ == "__main__":
    manage.run()
