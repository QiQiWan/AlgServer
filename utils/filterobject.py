"""
一个用于生成筛选的可迭代对象
"""
from django.utils.safestring import mark_safe
from django.db.models import Count  # 使用聚合函数计算对象数量
import random


class TagFilterObject(object):  # 标签类
    def __init__(self, data_list, request, filter_num=5):
        self.filter_list = data_list[:filter_num]
        self.value_list = request.GET.getlist("TOP_tag")
        self.request = request

        # print(self.request.GET)
        # print(self.request.GET.copy().pop("page", None))

    def color_generator(self):
        while True:
            r = random.randint(128, 255)
            g = random.randint(128, 255)
            b = random.randint(128, 255)
            color_code = "#{:02x}{:02x}{:02x}".format(r, g, b)
            yield color_code

    def color_random(self):
        style = """
        style= "background-image: linear-gradient({r}deg, {g} 0%, {b} 100%); font-weight:600 "  
        """
        gen = self.color_generator()
        style = style.format(r=90, g=next(gen), b=next(gen))
        return style

    def __iter__(self):
        # ck = ""
        # if self.request.GET.copy().pop("page", None):
        #     ck = "checked"
        # yield mark_safe(
        #     "<a class='cell' href='#'><input type='checkbox' {}><label>全部</label></a>".format(
        #         ck
        #     )
        # )
        for item in self.filter_list:
            ck = ""
            self.value_list = self.request.GET.getlist("TOP_tag")
            if item.tagname in self.value_list:
                style = self.color_random()
                ck = style
                self.value_list.remove(item.tagname)  # 如果标签被选中，则在URL中删除该标签
            else:
                self.value_list.append(item.tagname)
            # 生成指定URL
            queryset_dict = self.request.GET.copy()  # 不使用copy（）会影响原生的值的改变
            queryset_dict._mutable = True
            queryset_dict.setlist("TOP_tag", self.value_list)
            url = "{}?{}".format(self.request.path, queryset_dict.urlencode())

            # html = "<a class='cell' href='{url}'><input type='checkbox' {ck}><label>{name}</label></a>".format(
            #     url=url, ck=ck, name=item.tagname
            # )

            html = """<a class='cell' href='{url}'><label {ck} ">{name}</label></a>""".format(
                url=url, ck=ck, name=item.tagname
            )

            yield mark_safe(html)
