from django.urls import path
from app01.views import account, article, comment, test

urlpatterns = [
    # 用户管理
    path("register/", account.register),  # 用户注册
    path("img/code/", account.image_code),  # 验证码的生成
    path("login/", account.login),  # 用户登录
    path("index/", account.index),  # 平台主页
    path("logout/", account.logout),  # 退出用户
    path("account/info/", account.user_profile),  # 个人中心
    path("account/edit/", account.user_edit),  # 个人编辑")
    path("account/comment_manage/", account.comment_manage),  # 个人中心评论管理
    # 文章管理
    path("account/list/", article.article_list),  # 个人文章中心
    path("article/like/<int:id>/", article.article_like),  # 文章点赞功能
    path("article/<str:BV_code>/manage/", article.article_manage),  # 文章的管理
    path("article/<str:BV_code>/detail/", article.article_detail),  # 显示文章详情页
    path("article/search/", article.article_search),  # 文章搜索功能
    path("article/<str:BV_code>/write/", article.article_write),  # 文章的编写
    path("article/<str:BV_code>/delete/", article.article_delete),  # 文章的删除
    path("article/<str:BV_code>/release/", article.article_release),  # 文章的发布
    path("article/<str:BV_code>/edit/", article.article_edit),  # 文章的编辑
    path("markdown/img/<str:BV_code>/", article.md_imgupload),  # markdown的图片上传
    # path("test/", article.test),
    # 评论管理
    path("comment/post/", comment.comment_post),  # 评论的发表
    path("comment/reply_get/", comment.reply_get),  # 获取评论回复列表
    path("comment/reply_post/", comment.comment_reply),  # 发表回复评论
    path("comment/like/<int:id>/", comment.comment_Like),  # 评论点赞功能
    path("comment/delete/", comment.comment_delete),  # 评论删除功能
    # 标签管理
    path("article/statistic/", article.statistic),  # 文章数据统计
    path("article/<int:id>/taglist/", article.tag_index),
    path("tag_static/get/", article.tag_statistic_pie),  # 标签饼状图数据获取,
    path("article/statistic/get/", article.tag_article_statistic_pie),
    path("tag/keywords/get/", article.tag_keywords_get),  # 获取搜索关键词
    path("comment/wordcloud/<str:bv_code>/", comment.comment_to_cloudimg),  # 根据文章评论生成云图
    path("test1/", test.some_view),  # 生成CSV文件
]
