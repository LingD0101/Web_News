from . import passport_blur
from flask import request, jsonify, current_app, make_response
from info.utils.response_code import RET
from info.utils.captcha.captcha import captcha
from info import redis_store, constants
import re, random
from info.librarys.yuntongxun import sms


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
        return jsonify(errno=RET.PARAMERR, errmsg="参数缺失")
    # 调用captcha生成验证码图片
    name, text, image = captcha.generate_captcha()
    # 把验证码内容存入redis数据库
    try:
        redis_store.setex("imageCode_" + image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码失败")
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
    1.获取数据 mobile/image_code/image_code_id
    2.检查数据完整性
    3.验证手机号是否符合,用正则
    4.从本地获取验证码数据
    5.判断是否有数据
    6.删除redis中图片数据,因图片验证一次有效
    7.对比本地数据跟数据库数据是否一致,统一转换成小写
    8.生成短信验证码6位随机数
    9.保存到redis
    10.调用云通讯发送短信
    11.判断发送结果
    12.反馈结果
    """
    # 获取数据
    mobile = request.json.get('mobile')
    image_code = request.json.get('image_code')
    image_code_id = request.json.get('image_code_id')
    # 检查数据是否存完整
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="数据不完整")
    # 验证手机号是否符合规则
    if not re.match(r'^1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.NODATA, errmsg="手机号不符合")
    # 获取本地验证码
    try:
        real_image_code = redis_store.get('imageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取图片验证码失败")
    # 判断是否有数据
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="验证码已过期")
    # 删除数据,因为原则上是只验证一次
    try:
        redis_store.delete('imageCode_' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
    # 验证码跟数据库是否一致
    if real_image_code.decode().lower() != image_code.lower():
        return jsonify(errno=RET.PARAMERR, errmsg="验证码不一致")
    # 生成随机数
    sms_code = '%06d' % random.randint(0, 999999)
    # 保存数据到redis
    try:
        redis_store.setex("SMSCode_" + mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码失败")
    # 调用云通讯方法发送短信
    try:
        ccp = sms.CCP()
        result = ccp.send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="短信发送失败")
    # 判断发送结果
    if result == 0:
        return jsonify(errno=RET.OK, errmsg="短信发送成功")
    else:
        return jsonify(errno=RET.THIRDERR, errmsg="短信发送失败")

