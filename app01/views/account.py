from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from app01.models import (
    User,
    Text,
    Sidebar,
    Tag,
    Tag_Text,
    UserProfile,
    Comment,
    Text_cloud_Img,
)
from utils.code import check_code
from io import BytesIO
from app01.forms.account import *
from django_redis import get_redis_connection
from django.db.models import Q, Count
from utils.pagenation import Pagination
from django.views.decorators.csrf import csrf_exempt
from utils.filterobject import TagFilterObject
from datetime import datetime
from django.contrib.auth.decorators import login_required
from utils.wordcloud_generate import Cloud
from app01.forms.comment import Cloud_ImgForm

# def index(request):
#     # 去连接池中获取一个连接
#     conn = get_redis_connection()  # 默认去default中

#     conn.set("nickname", "cc", ex=10)
#     value = conn.get("nickname")
#     print(value)
#     return HttpResponse("OK")


def register(request):  # 注册视图函数
    if request.method == "GET":
        form = RegisterModelForm()
        return render(request, "register.html", {"form": form})
    else:
        form = RegisterModelForm(data=request.POST)

        if form.is_valid():
            # 验证码校验
            user_input_code = form.cleaned_data.pop("code")
            code = request.session.get("image_code", "")
            if code.lower() != user_input_code.lower():
                form.add_error("code", "验证码错误")
                return JsonResponse({"status": False, "error": form.errors})
            else:
                form.save()
            return JsonResponse({"status": True, "data": "/login/"})
        print(form.errors)
        return JsonResponse({"status": False, "error": form.errors})


@csrf_exempt
def login(request):  # 登录视图函数
    if request.method == "GET":
        form = LoginForm()
        return render(request, "login.html", {"form": form})
    else:
        form = LoginForm(data=request.POST)
        if form.is_valid():
            # 验证码校验
            user_input_code = form.cleaned_data.pop("code")
            code = request.session.get("image_code", "")
            if code.lower() != user_input_code.lower():
                form.add_error("code", "验证码错误")  # OPTIMIZE此处问题：验证码输入错误的时候，密码会被刷新掉
                print(form.data)
                return render(request, "login.html", {"form": form})
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            print(password)
            user = (
                User.objects.filter(
                    Q(username=username) | Q(email=username) | Q(mobile=username)
                )
                .filter(password=password)
                .first()
            )
            if user:
                request.session["user_id"] = user.id
                request.session.set_expiry(60 * 60 * 24 * 14)

                return redirect(request.GET.get("next", "/index/"))
            else:
                form.add_error("username", "用户名或密码错误")
        return render(request, "login.html", {"form": form})


def logout(request):  # 退出账号
    request.session.flush()
    return redirect("/login/")


@csrf_exempt  # TODO标签筛选有问题
def index(request):  # 主页展示
    # 查询所有的文章,并根据创建时间排序
    if request.method == "GET":
        print(request.GET.get("start_date", ""))
        # 如果前端发来日期筛选Ajax请求，获取对应的开始日期和截止日期
        start = datetime.strptime(
            request.GET.get("start_date", "1970-01-01"), "%Y-%m-%d"
        )
        end = datetime.strptime(request.GET.get("end_date", "2099-12-30"), "%Y-%m-%d")

        condition = {}
        allow_filter_name = [
            "TOP_tag",
            "publish_time",
        ]  # OPTIMIZE此处目前只有筛选发布时间和热门标签两个功能，以后可以继续添加
        for name in allow_filter_name:
            value_list = request.GET.getlist(name)  # 获取对应标签的筛选值列表
            if not value_list:
                continue
            if name == "TOP_tag":  # 由于没有对文章直接赋予标签属性,对标签筛选作特殊处理
                tag_queryset = Tag.objects.filter(
                    Q(tagname__in=value_list)
                )  # 获取标签对应的queryset
                tag_id_list = [tag.id for tag in tag_queryset]  # 获取标签id表
                article_tag_queryset = Tag_Text.objects.filter(
                    Q(tags__in=tag_id_list)  # SKILL使用__in+字段名实现一个字段对属性值列表的查询
                )  # 获取标签对应的文章queryset
                # print(tag_id_list)
                # print(article_tag_queryset)
                article_id_list = [
                    tag_text.article.id for tag_text in article_tag_queryset
                ]  # 获取标签对应的文章id表
                condition["id__in"] = article_id_list  # 由标签转换id筛选条件
                continue
            condition["{}__in".format(name)] = value_list  # 构造筛选条件
        # print(condition)
        article_list = (
            Text.objects.filter(is_public=True)
            .filter(**condition)
            .order_by("-create_time")
        )
        if start and end:
            article_list = article_list.filter(create_time__range=(start, end))

        # 获取分页对象
        page_object = Pagination(request, article_list)
        Sidebar_list = Sidebar.objects.filter(place=1)  # 查询用于主页的侧边栏

        context = {
            "queryset": page_object.page_queryset,  # 分完页的数据
            "page_string": page_object.html(),  # 生成页码
            "Sidebar_list": Sidebar_list,
            "username": request.tracer["user"],
            "keyword": request.GET.get("keyword", ""),
        }

        context["date_Select_before"] = "2023-10-10 至 2023-10-17"
        return render(request, "index.html", context)


def image_code(request):
    """生成图片验证码"""

    # 调用pillow函数，生成图片
    img, code_string = check_code()

    # 写入到自己的session中（以便于后续获取验证码再进行校验）
    request.session["image_code"] = code_string
    # 给Session设置60s超时
    request.session.set_expiry(60)

    stream = BytesIO()
    img.save(stream, "png")
    return HttpResponse(stream.getvalue())


# @login_required(login_url="/login/")
def user_profile(request):
    user = request.tracer["user"]  # 获取当前登录用户
    profile = UserProfile.objects.filter(owner=user).first()
    if request.method == "GET":
        form = UserProfileForm(instance=profile)
        return render(
            request,
            "user_profile.html",
            {"user": user, "profile": profile, "form": form},
        )
    else:
        print(request.POST)
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            instance = form.save()
            return render(
                request,
                "user_profile.html",
                locals(),
            )


def user_edit(request):
    """编辑用户信息"""
    user = request.tracer["user"]  # 获取当前登录用户
    if request.method == "POST":
        form = UserForm(
            request.POST,
            request.FILES,
            instance=user,  # SKILL在表单中传输文件的时候要另外设置一个request.FILES，request.POST中不包含文件信息
        )  # 修改原来的数据并保存在form中，instance为显示原有的数据
        # user_profile_form = UserProfileForm(
        #     request.POST, instance=UserProfile.objects.filter(user=user).first()
        # )
        # if form.is_valid() and user_profile_form.is_valid():
        if form.is_valid():
            form.save()
            # user_profile_form.save()
            return redirect("/account/info/")
        else:
            print(form.errors)
            return render(request, "error.html")
    else:
        form = UserForm(instance=user)
        user_profile_form = UserProfileForm(
            instance=UserProfile.objects.filter(owner=user).first()
        )
        return render(request, "user_edit.html", locals())  # SKILL可以返回这个函数的所有本地变量


def comment_manage(request):
    user = request.tracer["user"]  # 获取当前登录用户
    if request.method == "GET":
        BV_code = request.GET.get("bv_code", "")
        context = {}
        articles = Text.objects.filter(author=user)  # 获取用户的所有文章
        urls = []
        for item in articles:
            url = "/account/comment_manage/?bv_code=" + item.bv_code
            urls.append(url)
        context["urls"] = urls
        context["articles"] = articles
        if BV_code:
            article = Text.objects.filter(bv_code=BV_code).first()
            context["article"] = article
        else:
            context["article"] = articles.first()
        # 获取当前文章的所有评论
        comment_list = Comment.objects.filter(
            text=context["article"].id, is_delete=False
        )
        context["comments"] = comment_list
        page_object = Pagination(request, comment_list, 5)
        context["page_string"] = page_object.html()  # 生成页码
        context["queryset"] = page_object.page_queryset  # 分完页的数据
        context["articles"] = articles

        # 生成云图
        comment_value_list = Comment.objects.filter(
            text=context["article"].id, is_delete=False
        ).values_list(
            "content", flat=True
        )  # SKILL通过values_list获取所有评论内容，通过将 flat=True 设置为 True，我们可以直接获取评论内容的平面列表，而不需要每个评论内容都作为单个元组返回。

        comments_str = " ".join(comment_value_list)  # 使用空格将评论内容连接起来
        cloud = None
        if context["article"].comment_num == 0:
            cloud = Cloud(context["article"].bv_code)
        else:
            cloud = Cloud(context["article"].bv_code, comments_str)
        img_name = cloud.cloud_gennerate()
        context1 = {
            "icon": 1,
            "img_name": img_name,
            "article": context["article"],
        }

        if Text_cloud_Img.objects.filter(article=context["article"]).exists():
            Text_cloud_Img.objects.filter(article=context["article"]).update(**context1)

        else:
            form = Cloud_ImgForm(context1)

            if form.is_valid():
                instance = form.save()
                print(instance)
            else:
                print(form.errors)
        cloud = Text_cloud_Img.objects.filter(article=context["article"]).first()
        context["img_url"] = cloud.img_name
        return render(request, "user_comment_manage.html", context)
