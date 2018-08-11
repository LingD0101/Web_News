# 创建图片验证模块的蓝图
from flask import Blueprint

# 路由映射
passport_blur = Blueprint('passport_blue', __name__)

from . import views
