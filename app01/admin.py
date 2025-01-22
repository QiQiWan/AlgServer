from django.contrib import admin

# Register your models here.
from .models import *


class ArticleAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = (
        "id",
        "title",
        "author",
        "likes",
        "comment_num",
        "bv_code",
        "create_time",
        "update_time",
        "is_delete",
        "is_public",
    )  # 指定要显示在表格中的字段
    search_fields = ("title",)  # 添加搜索字段，使管理员能够根据文章标题搜索
    actions = ["make_public", "make_private"]  # 注册批量处理动作

    def make_public(self, request, queryset):
        queryset.update(is_public=True)  # 将选定的文章设为公开

    make_public.short_description = "设为公开"  # 动作在界面中显示的名字

    def make_private(self, request, queryset):
        queryset.update(is_public=False)  # 将选定的文章设为私有

    make_private.short_description = "设为私有"


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "mobile", "create_time", "avatar")
    search_fields = ("username",)


class CommentAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("id", "user", "text", "content", "likes", "create_time")


class TagAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("id", "tagname", "create_time")


class Tag_TextAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("id", "article", "tags")


class Comment_ReplyAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("id", "user", "reply_user", "comment", "content", "create_time")


admin.site.register(User, UserAdmin)
admin.site.register(Text, ArticleAdmin)
admin.site.register(Sidebar)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like_Text)
admin.site.register(Like_Comment)
admin.site.register(Comment_Reply, Comment_ReplyAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Tag_Text, Tag_TextAdmin)
admin.site.register(UserProfile)
admin.site.register(Like_Comment_Reply)
