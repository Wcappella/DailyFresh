from celery import Celery
# 将django项目的配置文件信息保存操作系统中
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'DailyFresh06.settings'

# 启动celery的时候需要, 启动django的时候不需要(则注释掉下面两句)
# 让django初始化一下, django读入配置文件的信息
# django.setup()会询问操作系统配置文件的位置,读入配置文件的信息
# import django
# django.setup()


from django.core.mail import send_mail
from django.conf import settings
# 创建celery应用

# 参数1: 当前Celery工程的名字(自己取)
# 参数2: 指定使用的broker队列,例如使用redis作为broker:
# redis://主机ip:port/数据库编号(redis默认为我们准备了16个数据库0 ~ 15)
app = Celery('dailyfresh', broker='redis://127.0.0.1:6379/0')


# 定义任务
@app.task
def send_active_email(user_name, active_url, email):
    """发送激活邮件"""
    # send_mail(邮件标题, 邮件内容, 发件人, 收件人, html_message=html格式的邮件内容)
    html_message = """
           <h1>天天生鲜用户激活</h1>
           <h2>尊敬的%s用户: 感谢您使用天天生鲜,请在24小时内点击以下链接进行用户激活:</h2>
           <a href=%s>%s</a>
           """ % (user_name, active_url, active_url)
    send_mail('天天生鲜用户激活', '', settings.EMAIL_FROM, [email], html_message=html_message)

