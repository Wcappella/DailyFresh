from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.models import BaseModel
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from utils import constants

# Create your models here.


class User(AbstractUser, BaseModel):
    """用户"""
    class Meta:
        db_table = "df_users"

    def generate_active_token(self):
        """生成用户激活的token"""

        # 创建序列化器对象
        # 创建时传入两个参数: 秘钥, 有效时间
        s = Serializer(settings.SECRET_KEY, constants.USER_ACTIVE_EXPIRES)
        # dumps方法可以将传入的数据序列化,将要序列化的信息通过字典传入
        # 该方法返回的是一个二进制序列号
        token = s.dumps({'user_id': self.id})
        return token.decode()  # 将字节类型转换成字符串


class Address(BaseModel):
    """地址"""
    user = models.ForeignKey(User, verbose_name="所属用户")
    receiver_name = models.CharField(max_length=20, verbose_name="收件人")
    receiver_mobile = models.CharField(max_length=11, verbose_name="联系电话")
    detail_addr = models.CharField(max_length=256, verbose_name="详细地址")
    zip_code = models.CharField(max_length=6, verbose_name="邮政编码")

    class Meta:
        db_table = "df_address"