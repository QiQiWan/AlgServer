from typing import Any, Dict
from app01.models import User, UserProfile
from django import forms
from utils.encrypt import md5
from .BootstrapForm import BootstrapForm, BulmaForm
from django.core.validators import RegexValidator

# 定义密码的正则表达式
password_regex = "^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d]+$"

# 创建密码验证器
password_validator = RegexValidator(password_regex, "密码必须由数字和字母组合")
# 创建手机号码验证器
phone_regex = RegexValidator(regex=r"^\+?1?\d{9,15}$", message="手机号码格式不正确，请输入有效的手机号码。")


class RegisterModelForm(BootstrapForm, forms.ModelForm):  # 用户注册表单
    password = forms.CharField(
        label="密码",
        min_length=8,
        max_length=64,
        error_messages={"min_length": "密码最少为8位", "max_length": "密码最多为128位"},
        widget=forms.PasswordInput,
        validators=[password_validator],
    )
    password_confirm = forms.CharField(label="确定密码", widget=forms.PasswordInput)
    code = forms.CharField(label="验证码")

    class Meta:
        model = User
        fields = ["username", "password", "password_confirm"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        exists = User.objects.filter(username=username).exists()
        if exists:
            raise forms.ValidationError("用户名已存在")
        return username

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)

    def clean_password_confirm(self):
        pwd = self.cleaned_data.get("password")
        print(pwd)
        comfirm_pwd = md5(self.cleaned_data.get("password_confirm"))
        if pwd != comfirm_pwd:
            raise forms.ValidationError("两次密码不一致")
        return comfirm_pwd


class LoginForm(BootstrapForm, forms.Form):  # 用户登录表单
    username = forms.CharField(label="用户名或手机号码或邮箱")
    password = forms.CharField(
        label="密码", min_length=8, max_length=64, widget=forms.PasswordInput
    )
    code = forms.CharField(label="验证码", widget=forms.TextInput)

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)


class UserProfileForm(BulmaForm, forms.ModelForm):  # 用户编辑表单
    class Meta:
        model = UserProfile
        fields = ["nike_name", "profile", "signature"]

        help_texts = {
            "signature": "个性签名最多不超过50字",
        }
        # error_messages = {
        #     "avatar": {"required": "请上传头像"},
        #     "signature": {"required": "请填写个性签名"},
        # }


class UserForm(BulmaForm, forms.ModelForm):
    avatar = forms.ImageField(required=False, label="头像")
    email = forms.EmailField(required=False, label="邮箱")
    mobile = forms.CharField(
        required=False,
        label="手机号码",
        validators=[phone_regex],
        max_length=11,
        error_messages={"max_length": "手机号码最多为11位"},
    )

    class Meta:
        model = User
        fields = [
            "avatar",
            "username",
            "gender",
            "birthday",
            "email",
            "mobile",
            "address",
        ]
        help_texts = {
            "password": "密码最少为8位",
            "mobile": "手机号码为11位",
            "email": "请输入正确的邮箱格式",
        }

    # def clean_avatar(self):
    #     avatar = self.cleaned_data.get("avatar")
    #     print("路由：" + avatar.url)
    #     return avatar

    # error_messages = {
    #     "avatar": {"required": "请上传头像"},
    #     "signature": {"required": "请填写个性签名"},
    # }
