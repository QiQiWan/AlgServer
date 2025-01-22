from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
from app01 import models
from django.shortcuts import redirect
from django.conf import settings
import re


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_id = request.session.get("user_id", 0)
        # print(user_id)
        user = models.User.objects.filter(pk=user_id).first()
        request.tracer = {"user": user}
        # 定义正则表达式匹配规则
        regex = r"^/admin/.*$"
        regexAPI = r"^/foundationpit/.*"
        # 没有登录可以访问的内容（白名单）
        if request.path_info in settings.WHITE_REGEX_URL_LIST or re.match(
            regex, request.path_info
        ) or re.match(regexAPI, request.path_info):
            return

        # 检查用户是否已登录，如果未登录返回到登录界面
        if not request.tracer["user"]:
            print(request.path)
            print(request.path_info)
            return redirect("/login/" + "?next=" + request.path)
