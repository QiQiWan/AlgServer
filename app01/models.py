from django.db import models

# django中自带的用户模型
from django.contrib.auth.models import AbstractUser
from common.db import BaseModel
from django.template.loader import render_to_string  # 渲染模板
from common.imgdiystorage import FastDFSStorage
from django.core.validators import RegexValidator

# 创建手机号码验证器
phone_regex = RegexValidator(regex=r"^\+?1?\d{9,15}$", message="手机号码格式不正确，请输入有效的手机号码。")


class Img(
    BaseModel, models.Model
):  # TODO编写save函数，用于在保存后根据不同的type，保存到不同的存储桶文件夹中，并把这个模型用于其他模型中
    """图片模型"""

    IMG_TYPE_CHOICES = (
        (1, "用户头像"),
        (2, "标签图片"),
        (3, "用户中心背景图片"),
    )

    img = models.ImageField(
        verbose_name="图片", upload_to="images/%Y/%m", default="images/default.png"
    )
    desc = models.CharField(max_length=100, verbose_name="图片描述", blank=True)
    url = models.CharField(max_length=100, verbose_name="图片地址", blank=True)
    type = models.SmallIntegerField(
        verbose_name="图片类型", choices=IMG_TYPE_CHOICES, default=1
    )

    class Meta:
        db_table = "img_table"
        verbose_name = "图片表"

    def __str__(self):
        return str(self.id) + " " + self.img.url


class User(BaseModel, AbstractUser):
    """用户模型"""

    """
    AbstractUser包含一下几个属性:
        username
        email
        password
    
    """
    GENDER_CHOICES = (
        (1, "男"),
        (2, "女"),
    )
    mobile = models.CharField(
        max_length=11,
        default="",
        verbose_name="手机号码",
        null=True,
        blank=True,
        validators=[phone_regex],
    )

    gender = models.SmallIntegerField(
        verbose_name="性别", choices=GENDER_CHOICES, default=1
    )
    avatar = models.ImageField(
        upload_to="avatars/", default="avatars/default.jpg", null=True, blank=True
    )
    birthday = models.DateField(verbose_name="生日", blank=True, null=True)
    address = models.CharField(max_length=100, verbose_name="居住地", blank=True)
    avatar_url = models.URLField(verbose_name="头像地址", blank=True, null=True)

    class Meta:
        db_table = "users_table"
        verbose_name = "用户表"

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    nike_name = models.CharField(max_length=50, verbose_name="昵称", blank=True)
    profile = models.TextField(verbose_name="个人简介", default="这个人很懒，什么都没有留下")
    signature = models.TextField(verbose_name="个性签名", blank=True)

    class Meta:
        db_table = "User_profile_form"
        verbose_name = "用户中心表"

    def __str__(self):
        return self.owner.username + "的个人中心"


class Text(BaseModel, models.Model):
    """文章模型"""

    COLOR_CHOICES = (
        (1, "#56b8eb"),  # 56b8eb
        (2, "#f28033"),  # f28033
        (3, "#ebc656"),  # ebc656
        (4, "#a2d148"),  # a2d148
        (5, "#20BFA4"),  # #20BFA4
        (6, "#7461c2"),  # 7461c2,
        (7, "#20bfa3"),  # 20bfa3,
    )
    title = models.CharField(max_length=100, verbose_name="文章标题")
    desc = models.TextField(max_length=100, verbose_name="文章描述", default="未填写描述")
    content = models.TextField(
        verbose_name="文章内容", blank=True, null=True, default="在此处开始编写文章内容......"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="发表者", default=""
    )
    likes = models.PositiveIntegerField(default=0, verbose_name="点赞数")
    comment_num = models.PositiveIntegerField(default=0, verbose_name="评论数量")
    bv_code = models.CharField(
        max_length=12, verbose_name="BV编码", default="待生成"
    )  # unique=True表示编码唯一

    color = models.SmallIntegerField(
        verbose_name="颜色", choices=COLOR_CHOICES, default=1
    )
    bucket = models.CharField(max_length=100, verbose_name="存储桶", default="")
    region = models.CharField(max_length=100, verbose_name="存储区域", default="")
    is_public = models.BooleanField(default=False, verbose_name="是否对外公开")

    class Meta:
        db_table = "text_table"
        verbose_name = "文章表"

    def __str__(self):
        return self.title


class Tag(models.Model):  # TODO此表以后可以用于关键词搜索时使用
    """标签表"""

    tagname = models.CharField(max_length=15, verbose_name="标签名")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    desc = models.TextField(verbose_name="描述", default="")
    img = models.ImageField(
        verbose_name="图片", blank=True, null=True, storage=FastDFSStorage
    )  # TODO此处添加自定义存储引擎

    class Meta:
        db_table = "Tag_table"
        verbose_name = "标签表"

    def __str__(self):
        return self.tagname

    # def save(self, *args, **kwargs):
    #     if self.img:
    #         # 上传图片到 COS
    #         # cos_client = CosS3Client(
    #         #     CosConfig(
    #         #         Secret_id=settings.COS_SECRET_ID,
    #         #         Secret_key=settings.COS_SECRET_KEY,
    #         #         Region=kwargs.get('region', 'ap-guangzhou')
    #         #     )
    #         # )
    #         # key = default_storage.save(self.image.name, self.image.file)
    #         print("hhh")
    #         print(self.img.name)
    #         print(self.img.url)
    #         print(self.img.file)
    #         print(self.img)
    #         # 更新图片的 URL
    #         # self.img.url = (
    #         #     "https://algserver-md-img-1252510405.cos.ap-chengdu.myqcloud.com/p1.png"
    #         # )
    #         # self.img.url = "dede"
    #     super().save(*args, **kwargs)


class Tag_Text(models.Model):
    """文章标签表"""

    article = models.ForeignKey(to="Text", verbose_name="文章", on_delete=models.CASCADE)
    # tags = models.CharField(max_length=20, verbose_name="标签")
    tags = models.ForeignKey(to="Tag", verbose_name="标签名", on_delete=models.CASCADE)

    class Meta:
        db_table = "tag_article_table"
        verbose_name = "文章标签表"

    def __str__(self):
        return self.article.title + ":" + self.tags.tagname


class Like_Text(models.Model):
    """文章点赞模型"""

    user = models.ForeignKey(verbose_name="点赞用户", to="User", on_delete=models.CASCADE)
    target = models.ForeignKey(to="Text", verbose_name="文章", on_delete=models.CASCADE)

    class Meta:
        db_table = "like_text_table"
        verbose_name = "文章点赞表"

    def __str__(self) -> str:
        return self.target.title


class Comment(models.Model):
    """评论模型"""

    text = models.ForeignKey(
        Text, on_delete=models.CASCADE, verbose_name="所属文章", null=True
    )  # 评论所属文章
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="评论者", null=True
    )
    content = models.TextField(verbose_name="评论内容")
    likes = models.PositiveIntegerField(default=0, verbose_name="点赞数量")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_delete = models.BooleanField(default=False, verbose_name="删除标记")

    class Meta:
        db_table = "comment_table"
        verbose_name = "评论表"

    def __str__(self):
        return self.user.username + ":" + self.content


class Like_Comment(models.Model):
    user = models.ForeignKey(verbose_name="点赞用户", to="User", on_delete=models.CASCADE)
    target = models.ForeignKey(
        to="Comment", verbose_name="评论", on_delete=models.CASCADE
    )

    class Meta:
        db_table = "comment_like_table"
        verbose_name = "评论点赞表"

    def __str__(self):
        return self.target.text


class Comment_Reply(models.Model):
    content = models.TextField(verbose_name="评论内容")
    likes = models.PositiveIntegerField(default=0, verbose_name="点赞数量")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, null=True, blank=True, verbose_name="评论对象"
    )
    reply_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="被评论者",
        related_name="reply_user",
        null=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="评论者",
        null=True,
    )

    class Meta:
        db_table = "comment_reply_table"
        verbose_name = "评论回复表"

    def __str__(self):
        return self.user.username + "回复" + self.reply_user.username + ":" + self.content


class Like_Comment_Reply(models.Model):
    user = models.ForeignKey(verbose_name="点赞用户", to="User", on_delete=models.CASCADE)
    target = models.ForeignKey(
        to="Comment_Reply", verbose_name="评论", on_delete=models.CASCADE
    )

    class Meta:
        db_table = "comment_reply_like_table"
        verbose_name = "评论回复点赞表"

    def __str__(self):
        return self.user.username + ":" + self.target.content


class Sidebar(models.Model):
    # 侧边栏的模型数据

    STATUS = ((1, "隐藏"), (2, "展示"))

    DISPLAY_TYPE = (
        (1, "搜索"),
        (2, "最新文章"),
        (3, "最热文章"),
        (4, "最近评论"),
        (5, "文章归档"),
        (6, "HTML"),
    )
    PLACE_CHOICE = (
        (1, "主页"),
        (2, "文章详情页"),
        (3, "标签页"),
    )

    title = models.CharField(max_length=50, verbose_name="模块名称")  #  模块名称
    display_type = models.PositiveIntegerField(
        default=1, choices=DISPLAY_TYPE, verbose_name="展示类型"
    )  # 侧边栏  搜索框/最新文章/热门文章/HTML自定义等
    content = models.CharField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="内容",
        help_text="如果设置的不是HTML类型，可为空",
    )  # 这个字段是专门用来给HTML类型用的，其他类型可为空
    sort = models.PositiveIntegerField(
        default=1, verbose_name="排序", help_text="序号越大越靠前"
    )
    status = models.PositiveIntegerField(
        default=2, choices=STATUS, verbose_name="状态"
    )  # 隐藏  显示状态
    add_date = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  # 时间
    place = models.PositiveIntegerField(
        default=1, choices=PLACE_CHOICE, verbose_name="展示位置"
    )

    class Meta:
        verbose_name = "侧边栏"
        verbose_name_plural = verbose_name
        ordering = ["-sort"]

    def __str__(self):
        return self.title

    @classmethod  # 类方法装饰器，这个就变成了这个类的一个方法可以调用
    def get_sidebar(cls):
        return cls.objects.filter(status=2)  # 查询到所有允许展示的模块

    @property  # 成为一个类属性，调用的时候不需要后边的（）,是只读的，用户没办法修改
    def get_content(self):
        if self.display_type == 1:  # 查询文章
            context = {}
            return render_to_string("sidebar/search.html", context=context)
        elif self.display_type == 2:  # 最新发布的文章
            context = {}
            return render_to_string("sidebar/new_post.html", context=context)
        elif self.display_type == 3:  # 点赞最多的文章
            context = {}
            return render_to_string("sidebar/hot_post.html", context=context)
        elif self.display_type == 4:  # 评论
            context = {}
            return render_to_string("sidebar/comment.html", context=context)
        elif self.display_type == 5:  # 文章归档
            context = {"username": "John", "comment_text": "这是一条很棒的评论！"}
            return render_to_string("sidebar/archives.html", context=context)
        elif self.display_type == 6:  # 自定义侧边栏
            return self.content  # 在侧边栏直接使用这里的html，模板中必须使用safe过滤器去渲染HTML


class Text_cloud_Img(models.Model):
    ICON_CHOICE = (
        (0, "fas fa-comment-dots"),
        (1, "fa fa-flag"),
        (2, "fa fa-apple"),
        (3, "fa fa-cloud"),
    )
    icon = models.PositiveIntegerField(default=0, verbose_name="图标类型")
    img_name = models.CharField(default="", verbose_name="图片名", max_length=100)
    article = models.ForeignKey(
        to="Text", verbose_name="所属文章", on_delete=models.CASCADE
    )
