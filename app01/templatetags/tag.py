from django.template import Library
from app01.models import Tag, Tag_Text
from utils.filterobject import TagFilterObject
from django.db.models import Count

register = Library()


@register.inclusion_tag(
    "inclusion/filter.html"
)  # OPTIMIZE原计划在siderbar模型中部署侧边栏，但是无法在模板传入context参数，以后会尝试使用下面两个自定义过滤器函数实现模板传参和函数调用
def all_list(request):
    top_tags = (
        Tag_Text.objects.values("tags")
        .annotate(article_count=Count("article"))
        .order_by("-article_count")
    )  # 获取标签相关文章数量排名列表
    top_tag_id_list = [tag["tags"] for tag in top_tags]
    top_tag_queryset = Tag.objects.filter(id__in=top_tag_id_list)
    filter_list = [TagFilterObject(top_tag_queryset, request)]
    return {"filter_list": filter_list}


@register.filter(name="add_arg")
def template_args(instance, arg):
    """stores the arguments in a separate instance attribute"""
    if not hasattr(instance, "_TemplateArgs"):
        setattr(instance, "_TemplateArgs", [])
    instance._TemplateArgs.append(arg)
    return instance


@register.filter(name="call")
def template_method(instance, method):
    """retrieves the arguments if any and calls the method"""
    method = getattr(instance, method)
    if hasattr(instance, "_TemplateArgs"):
        to_return = method(*instance._TemplateArgs)
        delattr(instance, "_TemplateArgs")
        return to_return
    return method()


@register.filter
def get_item(value, index):  # 用于生成文章url与
    """<a href="{{ article_urls|get_item:forloop.counter0 }}" class="dropdown-item">
    与模板语言中forloop一起使用,使得在循环一个列表时，可以根据当前循环索引去同步获得另外一个列表的对应相同索引

    """
    return value[index]
