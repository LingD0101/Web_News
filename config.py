from redis import StrictRedis


class Config(object):
    DEBUG = True  # 设置debug
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost"  # 设置绑定数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 追踪

    SECRET_KEY = "1vbLyW75/dM3E94CLq7HHor3e2nvMC1Nw0+0OKj8I0i3kSbv4PSEbg=="
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    SESSION_TYPE = 'redis'  # 制定session保存到redis
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用redis的实例
    SESSION_USE_SIGNER = True  # 签名加密
    PERMANENT_SESSION_LEFETIME = 86400  # 设置有效时间


# 定义开发模式
class DevelopmentConfig(Config):
    DEBUG = True


# 定义生产模式
class ProductionConfig(Config):
    DEBUG = False


config_name = {
    'develop': DevelopmentConfig,
    'produce': ProductionConfig
}
