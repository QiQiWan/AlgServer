from app01.forms.comment import CommentForm, Cloud_ImgForm
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from app01.models import (
    User,
    Text,
    Comment,
    Like_Comment,
    Comment_Reply,
    Text_cloud_Img,
)
from app01.forms.comment import CommentForm, Comment_ReplyForm
from utils.comment_generate import Comment_generate
import datetime
from common.Like import Like
from django.apps import apps
from utils.wordcloud_generate import Cloud


@csrf_exempt
def comment_post(request):  # 文章发表评论
    article = Text.objects.filter(pk=request.session["article_id"]).first()  # 获取当前所处文章
    print(request.POST)
    context = {
        "user": request.tracer["user"],  # 获取发表用户
        "text": article,
        "content": request.POST["keyword"],  # 获取发表内容
    }  # 用于上传表单保存
    # bv_code = context["text"].bv_code
    form = CommentForm(context)
    if form.is_valid():
        instance = form.save()  # SKILL使用instance可以接收from新创建的对象
        comment_dic = {
            "username": request.tracer["user"].username,  # 获取用户名称
            "content": request.POST["keyword"],
            "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "id": instance.id,
        }
        Text.objects.filter(pk=request.session["article_id"]).update(
            comment_num=article.comment_num + 1
        )
        return JsonResponse(
            {"status": True, "dic": comment_dic, "comment_num": article.comment_num + 1}
        )
    else:
        return render(request, "error.html")


@csrf_exempt
def comment_reply(request):  # 回复评论
    comment_id = request.POST["id"]
    content = request.POST["content"]
    type = request.POST["type"]
    print(request.POST)
    if content and comment_id:
        comment = Comment.objects.filter(pk=comment_id).first()
        user = request.tracer["user"]
        context = {
            "content": content,
            "comment": comment,
            "user": user,
            "reply_user": comment.user,  # TODO目前默认为评论的作者，如果是回复一个回复评论时就要对其作出修改
        }
        if type != "comment_to_reply":
            context["reply_user"] = (
                Comment_Reply.objects.filter(pk=type).first().user
            )  # 如果为回复评论，那么被评论对象为回复评论的评论者
        form = Comment_ReplyForm(context)
        if form.is_valid():
            instance = form.save()
            print(instance)
            html = Comment_generate(request, [instance]).html
            return JsonResponse({"status": True, "html": html})
        else:
            print(form.errors)
            return JsonResponse({"status": False})

    return JsonResponse({"status": False})


def reply_get(request):
    comment_id = request.GET["id"]
    comment = Comment.objects.filter(id=comment_id).first()  # 获取指定评论
    queryset = Comment_Reply.objects.filter(comment=comment)
    # queryset = Comment_Reply.objects.all()
    comment_dic = {
        "username": comment.user.username,  # 获取用户名称
        "content": comment.content,
        "datetime": comment.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        "id": comment.id,
    }
    html = Comment_generate(request, queryset).html
    print(html)

    return JsonResponse(
        {"status": True, "html": html, "count": queryset.count(), "dict": comment_dic}
    )


@csrf_exempt
def comment_Like(request, id):
    comment_type = request.POST["type"]  # 获取评论类型，评论或回复评论
    dict = Like(comment_type, id, request)
    return JsonResponse(dict)


def comment_to_cloudimg(request, bv_code):
    article = Text.objects.filter(bv_code=bv_code).first()
    comment_value_list = Comment.objects.filter(
        text=article.id, is_delete=False
    ).values_list(
        "content", flat=True
    )  # SKILL通过values_list获取所有评论内容，通过将 flat=True 设置为 True，我们可以直接获取评论内容的平面列表，而不需要每个评论内容都作为单个元组返回。

    comments_str = " ".join(comment_value_list)  # 使用空格将评论内容连接起来
    cloud = Cloud(article.bv_code, comments_str)
    img_name = cloud.cloud_gennerate()
    context = {
        "icon": 1,
        "img_name": img_name,
        "article": article,
    }

    if Text_cloud_Img.objects.filter(article=article).exists():
        Text_cloud_Img.objects.filter(article=article).update(**context)

    else:
        form = Cloud_ImgForm(context)

        if form.is_valid():
            instance = form.save()
            print(instance)
        else:
            print(form.errors)
    return JsonResponse({"status": True, "img_name": img_name})


@csrf_exempt
def comment_delete(request):
    comment_id = request.POST["id"]
    Comment.objects.filter(pk=comment_id).update(is_delete=True)
    return JsonResponse({"status": True})
