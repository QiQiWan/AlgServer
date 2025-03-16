from django.shortcuts import render, redirect, HttpResponse
from django.http import JsonResponse
from app01.models import (
    User,
    Like_Text,
    Sidebar,
    Comment_Reply,
    Comment,
    Tag,
    Tag_Text,
)

# , Tag_Text, Tag
from app01.forms.article import *
from utils.generate_bv import enc
from django.db.models import Q, F
from utils.pagenation import Pagination
import os
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from utils.file_upload import upload_obj
import json
import datetime
from collections import Counter


@csrf_exempt
def article_list(request):  # 展示文章，并在本页面通过ajax来创建文章
    if request.method == "GET":
        form = TextModelForm()
        # 创建一个字典用于传输把数据传输到前端
        article_dic = {"create": [], "like": []}
        # 获取我创建的文章
        cre_list = Text.objects.filter(author=request.tracer["user"])
        # 获取我点赞的文章
        all_list = Text.objects.all()  # 获取所有的文章
        like_list = []
        for row in all_list:
            if Like_Text.objects.filter(
                target=row, user=request.tracer["user"]
            ).exists():
                like_list.append(row)
        article_dic = {"create": cre_list, "like": like_list}
        context = {
            "form": form,
            "article_dic": article_dic,
            "status": False,
            "user": request.tracer["user"],
        }
        return render(request, "article_list.html", context)
    else:
        # 由于tag不用作表单处理，故不能使用直接QueryDict对象来提交表单
        data = json.loads(request.body)  # 解析JSON数据
        form_data = data.get("form_data", [])  # 获取表单数据
        tagname_list = data.get("tag", [])  # 获取标签列表数据
        form_data_dict = {}  # 创建一个用于提交表单的字典（此处也可以创建一个空的QueryDict对象）
        for field in form_data:
            field_name = field["name"]
            field_value = field["value"]
            form_data_dict[field_name] = field_value
        form = TextModelForm(form_data_dict)
        if form.is_valid():
            form.instance.author = request.tracer["user"]
            instance = form.save()
            object = Text.objects.filter(title=form.cleaned_data["title"]).first()
            Text.objects.filter(pk=object.id).update(bv_code=enc(object.pk))
            Tags = Tag.objects.all()  # 获取所有分类对象
            print(tagname_list)
            for tagname in tagname_list:
                tag = None
                for item in Tags:
                    if item.tagname == tagname:
                        tag = item
                        break
                if tag is None:
                    tag = Tag.objects.create(tagname=tagname)
                Tag_Text.objects.create(article=object, tags=tag)  # 创建关系

            return JsonResponse({"status": True})
        else:
            print(form.errors)
            return JsonResponse({"status": False, "error": form.errors})


@csrf_exempt
def article_like(request, id):
    if request.POST.get("action") == "clike":
        context = {}
        article_id = id
        article = Text.objects.filter(pk=article_id).first()  # 获取目标文章
        if article:
            if Like_Text.objects.filter(
                target=article, user=request.tracer["user"]
            ).exists():  # 如果已经点赞,则表示取消点赞
                Like_Text.objects.filter(
                    target=article, user=request.tracer["user"]
                ).delete()
                if article.likes != 0:
                    Text.objects.filter(pk=article_id).update(likes=article.likes - 1)
                    context["status"] = False
                    context["likes"] = article.likes - 1  # 由于article是点赞之前获取的故也要作出变化

            else:  # 如果点赞成功
                Like_Text.objects.create(target=article, user=request.tracer["user"])
                Text.objects.filter(pk=article_id).update(likes=article.likes + 1)
                context["status"] = True
                context["likes"] = article.likes + 1

            return JsonResponse(context)
        else:
            return JsonResponse({"status": False})


def article_manage(request, BV_code):
    if request.method == "GET":
        article = Text.objects.filter(bv_code=BV_code).first()
        author = request.tracer["user"]
        form = TextModelForm(instance=article)
        context = {
            "article": article,
            "status": True,
            "form": form,
            "request": request,
            "user": author,
        }
        if article.author != author:  # 只有文章作者才能对该文章进行操作
            return render(request, "error.html")
        else:
            return render(request, "article_manage.html", context)


def article_detail(request, BV_code):
    if request.method == "GET":
        article = Text.objects.filter(bv_code=BV_code).first()
        request.session["article_id"] = article.id
        tag_list = Tag_Text.objects.filter(article=article).all()  # 获取文章标签
        print(tag_list)
        context = {
            "article": article,
            "user": None,
            "is_like": False,
            "comments": Comment.objects.filter(text=article).all(),
            "username": request.tracer["user"],
            "tagname_list": tag_list,
        }
        context["Sidebar_list"] = Sidebar.objects.all()
        user = request.tracer["user"]
        if user:
            context["user"] = user
            if Like_Text.objects.filter(target=article, user=user).exists():
                context["is_like"] = True

        return render(request, "article_detail.html", context)


def article_search(request):  # 文章搜索
    keyword = request.GET.get("keyword", " ")
    # 如果没有输入关键词搜索，默认为显示全部文章
    if not keyword:
        article_list = Text.objects.all()
    else:
        article_list = Text.objects.filter(
            Q(title__icontains=keyword)
            | Q(content__icontains=keyword)
            | Q(desc__icontains=keyword),
            is_public=True,
        )
    page_object = Pagination(request, article_list)
    Sidebar_list = Sidebar.objects.all()
    context = {
        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html(),  # 生成页码
        "Sidebar_list": Sidebar_list,
        "keyword": keyword,
    }
    return render(request, "index.html", context)


def article_write(request, BV_code):
    if request.method == "GET":
        article = Text.objects.filter(bv_code=BV_code).first()
        context = {
            "article": article,
        }
        return render(request, "article.write.html", context)


def article_delete(request, BV_code):
    if request.method == "GET":
        article = Text.objects.filter(bv_code=BV_code).first()
        if article.author == request.tracer["user"]:
            article.delete()
            return redirect("/account/list/")
        else:
            return render(request, "error.html")


def article_release(request, BV_code):
    data = request.POST
    Text.objects.filter(bv_code=BV_code).update(content=data.get("content"))
    return JsonResponse({"status": True})


def article_edit(request, BV_code):
    article = Text.objects.filter(bv_code=BV_code).first()
    if request.method == "GET":
        form = TextModelForm()
        return render(request, "article.manage.html", {{"form": form}})
    else:
        form = TextModelForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": True})
        else:
            return JsonResponse({"status": False, "error": form.errors})


@csrf_exempt  # csrf-token认证装饰器
def md_imgupload(request, BV_code):
    result = {
        "success": 1,
        "message": True,
        "url": "#",
    }  # 上传结果
    img_obj = request.FILES.get("editormd-image-file")  # 获取文件对象
    print(img_obj)
    if not img_obj:  # 上传文件失败
        result["success"] = 0
        result["message"] = "文件不存在"
    else:
        url = upload_obj(img_obj, BV_code)
        result["url"] = url
    print(result)
    return JsonResponse(result)


def test(request):
    return render(request, "article_write.html")


def tag_index(request, id):
    # 获取对应标签id
    tag_id = id
    # 获取标签对应的文章
    list = Tag_Text.objects.filter(tags=tag_id)
    # 获取标签对象
    tag = Tag.objects.filter(pk=tag_id).first()
    # 获取标签对应的文章数量
    count = len(list)
    # 获取标签对应的文章列表
    # article_list = []
    # for item in list:
    #     article_list.append(item.article)
    article_list = [item.article.id for item in list]
    # 将python列表转化为queryset，用于分页功能参数使用
    tag_article_queryset = Text.objects.filter(Q(id__in=article_list))
    # 获取Tag_Text中"text"字段的queryset
    # text_queryset = tag_article_queryset.values_list("article", flat=True)

    # 获取侧边栏
    Sidebar_list = Sidebar.objects.all()
    print(count)
    # print(tag.img.url)
    print(tag_article_queryset)
    # 获取分页
    page_object = Pagination(request, tag_article_queryset)
    context = {
        "queryset": tag_article_queryset,
        "tag": tag,
        "article_count": count,
        "page_string": page_object.html(),
        "Sidebar_list": Sidebar_list,
        "username": request.tracer["user"],
    }

    return render(request, "article_tag_index.html", context)


def tag_statistic_pie(request):
    # 获取标签列表
    Tags = Tag.objects.all()
    tag_list = [tag.tagname for tag in Tags]
    tag_value_list = [
        {"name": tag.tagname, "value": Tag_Text.objects.filter(tags=tag.id).count()}
        for tag in Tags
    ]
    return JsonResponse({"tag_list": tag_list, "tag_value_list": tag_value_list})


def tag_article_statistic_pie(request):
    # 获取最近七天发表的文章
    end = datetime.date.today()
    start = end - datetime.timedelta(days=6)
    article_list = Text.objects.filter(
        create_time__range=(start, end + datetime.timedelta(days=1))
    )
    # article_create_time_list = list(
    #     set([article.create_time.strftime("%Y-%m-%d") for article in article_list])
    # )
    # article_create_time_list.insert(0, "publish")
    # 获取每天创建文章的类型
    source = []
    # source.append(article_create_time_list)
    tag_total_list = []
    article_create_time_list = []
    current_date = start
    while current_date <= end:
        current_article_list = article_list.filter(
            create_time__range=(
                current_date,
                current_date + datetime.timedelta(days=1),
            )
        )
        if current_article_list:
            tags = Tag_Text.objects.filter(article__in=current_article_list).values(
                "tags"
            )  # 获取当天标签
            tag_ids = list(set([tag["tags"] for tag in tags]))
            tag_name_list = [
                tag["tagname"]
                for tag in Tag.objects.filter(pk__in=tag_ids).values("tagname")
            ]
            print(tag_name_list)
            tag_total_list += tag_name_list
        article_create_time_list.append(current_date.strftime("%Y-%m-%d"))
        current_date += datetime.timedelta(days=1)
    tag_total_list = list(set(tag_total_list))  # 获取7天内所有的标签
    article_create_time_list.insert(0, "publish")
    source.append(article_create_time_list)
    for tag in tag_total_list:
        base_list = []
        base_list.append(tag)
        current_date = start
        tag_object = Tag.objects.filter(tagname=tag).first()
        tag_article_current_list = Tag_Text.objects.filter(tags=tag_object.id).values(
            "article"
        )
        article_id_list = [
            article["article"] for article in tag_article_current_list
        ]  # 获取标签的所有文章id
        article_current_list = Text.objects.filter(id__in=article_id_list)  # 获取标签的所有文章
        # 获取标签对应每天数量列表
        while current_date <= end:
            count = article_current_list.filter(
                create_time__range=(
                    current_date,
                    current_date + datetime.timedelta(days=1),
                )
            ).count()
            base_list.append(count)

            current_date += datetime.timedelta(days=1)
        source.append(base_list)

    print(source)

    return JsonResponse({"source": source, "status": True})


def statistic(request):
    return render(
        request,
        "article_statistic.html",
        {
            "username": request.tracer["user"],
        },
    )


def tag_keywords_get(request):
    tag_list = Tag.objects.all()
    keywords = list(map(lambda x: x.tagname, tag_list))
    print(keywords)
    return JsonResponse({"status": True, "data": keywords})
