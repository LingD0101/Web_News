from . import passport_blur
from flask import request, jsonify, current_app, make_response
from info.utils.response_code import RET
from info.utils.captcha.captcha import captcha
from info import redis_store, constants


# 验证码
@passport_blur.route('/image_code')
def generate_image_code():
    """
    1.获取前端传入的uuid参数
    2.判断参数是否存在
    3.调用captcha生成验证码,验证码包含text/image/name
    4.根据uuid来储存验证码的字符串,存在redis数据库
    5.返回验证码图片给浏览器,使用Make_response返回图片
    """

    # 获取uuid参数
    image_code_id = request.args.get('image_code_id')
    # 判断参数
    if not image_code_id:
        return jsonify(error=RET.PARAMERR, errmsg="参数缺失")
    # 调用captcha生成验证码图片
    name, text, image = captcha.generate_captcha()
    # 把验证码内容存入redis数据库
    try:
        redis_store.setex("ImageCode_" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR, errmsg="数据库存入错误")
    # 返回验证码图片给浏览器
    else:
        # 调用make_response方法
        response = make_response(image)
        # 修改请求头的content类型
        response.headers['Content-type'] = 'image/jpg'
        return response


# 短信验证
@passport_blur.route('/sms_code', methods=['POST'])
def sen_sms_code():
    """
    1.
    """
    pass
