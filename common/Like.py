from django.apps import apps


# 点赞模型命名规则与定义规则
# 命名：Like_对象模型名称
# 定义:
''' 
class Like_Text(models.Model):
    """点赞模型"""

    user = models.ForeignKey(verbose_name="点赞用户", to="User", on_delete=models.CASCADE)
    target = models.ForeignKey(to="Text", verbose_name="文章", on_delete=models.CASCADE)

    class Meta:
        db_table = "like_text_table"
        verbose_name = "文章点赞表"
'''


# -*- coding: utf-8 -*-

# import this

"""
                    _ooOoo_
                   o8888888o
                   88" . "88
                   (| -_- |)
                    O\ = /O
                ____/`---'\____
              .   ' \\| |// `.
               / \\||| : |||// \
              / _||||| -:- |||||- \
              | | \\\ - /// | |
              | \_| ''\---/'' | |
              \ .-\__ `-` ___/-. /
           ___`. .' /--.--\ `. . __
        ."" '< `.___\_<|>_/___.' >'"".
       | | : `- \`.;`\ _ /`;.`/ - ` : | |
         \ \ `-. \_ __\ /__ _/ . - ` /
 ======`-.____`-.___\_____/___.-`____.-'======
                    `=---='

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
          佛祖保佑         永无BUG
"""


# 返回类型：字典context，包含信息，状态，点赞数三对键值
def Like(classname, id, request):
    model = apps.get_model("app01", classname)  # 获取指定模型
    if model is not None:
        obj = model.objects.filter(pk=id).first()  # 获取指定对象
        context = {"status": True, "likes": obj.likes}
        if obj is not None:
            Like_classname = "Like_" + classname
            Like_model = apps.get_model("app01", Like_classname)  # 获取点赞模型
            if Like_model is not None:
                if Like_model.objects.filter(
                    target=obj, user=request.tracer["user"]
                ).exists():
                    Like_model.objects.filter(
                        target=obj, user=request.tracer["user"]
                    ).delete()

                    model.objects.filter(pk=id).update(likes=obj.likes - 1)
                    context["message"] = "Like_c succesfully!"
                    context["likes"] = obj.likes - 1
                    return context
                else:
                    Like_model.objects.create(target=obj, user=request.tracer["user"])
                    model.objects.filter(pk=id).update(likes=obj.likes + 1)
                    context["message"] = "Like succesfully!"
                    context["likes"] = obj.likes + 1
                    return context
            else:
                context["status"] = False
                context["message"] = "LikeModel not Found !"
                return context
        else:
            context["message"] = "Object not Found !"
            return context
    else:
        return {"message": "Model not Found !", "status": False}
