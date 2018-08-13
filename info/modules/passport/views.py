from . import passport_blue
from flask import request, jsonify, current_app, make_response, session
from info.utils.response_code import RET
from info.utils.captcha.captcha import captcha
from info import redis_store, constants, db
import re, random, datetime
from info.librarys.yuntongxun import sms
from info.models import User


# 验证码
@passport_blue.route('/image_code')
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
@passport_blue.route('/sms_code', methods=['POST'])
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


# 注册页面
@passport_blue.route('/register', methods=['POST'])
def register():
    """
    1.获取参数mobile/smscode/password
    2.验证参数完整性
    3.验证mobile是否符合
    4.检查手机号是否已注册
    5.获取本地真实smscode数据
    6.检验是否存在数据
    7.先对比参数,因为短信验证码有效期内可以多次输入验证
    8.删除redis中的smscode
    9.创建类对象保存数据mobile/password/nike_name
    10.提交数据到数据库
    11.保存缓存到redis
    12.返回结果
    :return:
    """
    # 获取参数
    mobile = request.json.get('mobile')
    sms_code = request.json.get('smscode')
    password = request.json.get('password')
    # 验证完整性
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='数据不完整')
    # 验证手机号是否符合
    if not re.match(r'^1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.NODATA, errmsg='手机号不符合')
    # 验证手机是否已注册
    try:
        # 获取数据
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg='查询用户失败')
    else:
        # 判断数据是否存在
        if user:
            return jsonify(errno=RET.DATAEXIST, errmsg='该手机已注册')
    # 获取本地smscode
    try:
        red_sms_code = redis_store.get('SMSCode_' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.NODATA, errmsg='查询短信验证码失败')
    # 判断获取的数据是否已过期
    if not red_sms_code:
        return jsonify(errno=RET.NODATA, errmsg='验证码已过期')
    # 判断验证码是否正确,由于前段获取的未必是字符串,所以需转换成字符串做对比
    if red_sms_code != str(sms_code):
        return jsonify(errno=RET.PARAMERR, errmsg='短信验证码错误')
    # 删除redis数据库中的短信验证码
    try:
        redis_store.delete(red_sms_code)
    except Exception as e:
        current_app.logger.error(e)
    # 创建类对象,实现用户信息存储和密码加密
    user = User()
    user.mobile = mobile
    user.password = password
    user.nick_name = mobile
    # 保存到mysql数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='数据保存失败')
    # 保存缓存数据到redis
    session['user_id'] = user.id
    session['mobile'] = mobile
    session['nike_name'] = mobile
    # 返回结果
    return jsonify(errno=RET.OK, errmsg='注册成功')


# 登陆页面
@passport_blue.route('/login', methods=['POST'])
def login():
    """
    1.获取数据
    2.验证数据完整性
    3.判断手机格式
    4.查询mysql确认用户存在
    5.判断查询结果
    6.判断密码是否正确
    7.记录用户最后登陆时间
    8.缓存用户信息
    9.返回结果
    :return:
    """
    # 获取数据
    mobile = request.json.get('mobile')
    password = request.json.get('password')
    # 验证完整性
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    # 判断手机格式
    if not re.match(r'^1[3456789]\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号格式错误')
    # 查询mysql,看是否已注册用户
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询错误')
    # 判断用户和密码
    if user is None or not user.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg='用户名或密码错误')
    # 记录登陆时间
    user.last_login = datetime.datetime.now()
    # 缓存用户信息
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nike_name'] = user.nick_name
    return jsonify(errno=RET.OK, errmsg='登陆成功')
