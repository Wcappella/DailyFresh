from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
import re
from django.core.mail import send_mail
from django.conf import settings
from users.models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from utils import constants
from celery_task.tasks import send_active_email
# Create your views here.

def register(request):
    """注册"""

    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        # post接受表单数据
        pass

# 类视图
class RegisterView(View):
    """注册类视图"""

    def get(self, request):
        """对应get请求方式的逻辑"""
        return render(request, 'register.html')

    def post(self, request):
        """对应post请求方式的逻辑"""
        # 获取post信息
        user_name = request.POST.get('user_name')
        password = request.POST.get('pwd')
        password2 = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 校验用户信息

        # 如果有信息为空,信息完整
        if not all([user_name, password, password2, email, allow]):

            # 动态引用url
            url = reverse('users:register')
            return redirect(url)

        # 检验参数
        # 0, 0.0, None, False, '', [], {}, () 在逻辑判断里面都是假
        if password2 != password:
            # 如果两次密码不一样
            return render(request, 'register.html', {'errmsg': '两次输入密码不一致'})

        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}', email):
            # 如果邮箱不符合规范
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            # 如果未勾选同意协议
            return render(request, 'register.html', {'errmsg': '请先同意用户协议'})


        # 业务处理
        # 保存用户数据到数据库
        # create_user方法是django用户认证系统提供的
        # 可以实现密码加密保存
        try:
            user = User.objects.create_user(user_name, email, password)
        except IntegrityError as e:
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 重置用户激活状态,用户认证系统默认用户为激活状态
        user.is_active = False
        user.save()


        # 生成用户激活的身份token 令牌
        token = user.generate_active_token()
        # 拼接激活的链接
        active_url = 'http://127.0.0.1:8000/users/active/' + token
        # 发送激活邮件
        # # send_mail(邮件标题, 邮件内容, 发件人, 收件人, html_message=html格式的邮件内容)
        # html_message = """
        # <h1>天天生鲜用户激活</h1>
        # <h2>尊敬的%s用户: 感谢您使用天天生鲜,请在24小时内点击以下链接进行用户激活:</h2>
        # <a href=%s>%s</a>
        # """ % (user_name, active_url, active_url)
        # send_mail('天天生鲜用户激活', '', settings.EMAIL_FROM, [email], html_message=html_message)

        # 异步发送邮件, 非阻塞
        send_active_email.delay(user_name, active_url, email)

        # 响应

        return HttpResponse('这是登录界面')


    # 发送激活邮件
    # user_id = 4
    # 请点击下面的链接激活:
        # http://127.0.0.1:8000/users/active/sahdkhiahfnaldhflehhfenaew
    # 加密过程是不可反推的,不能通过加密后的信息反推出原信息
    # 通过签名序列化实现对user_id的隐藏

class UserActiveView(View):
    """用户激活视图"""

    def get(self, request, user_token):
        """
        用户激活
        :param request:
        :param user_token: 用户激活令牌
        :return:
        """

        # 创建转换工具对象(序列化器)
        s = Serializer(settings.SECRET_KEY, constants.USER_ACTIVE_EXPIRES)

        try:
            data = s.loads(user_token)
        except SignatureExpired as e:
            # 表示token已过期
            return HttpResponse('链接已过期')
        user_id = data.get('user_id')

        # 更新用户的激活状态
        # 可以用以下的update方法实现查询的时候更改值
        # 查询结果集才能使用update方法, update方法里面是关键字参数传入
        # user = User.objects.filter(id=user_id).update(is_active = True)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            # 如果不存在该user_id, 会抛出这个异常
            return HttpResponse('用户不存在')
        user.is_active = True
        user.save()

        return HttpResponse('这是登录页面')
