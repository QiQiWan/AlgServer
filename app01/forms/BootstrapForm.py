from dataclasses import field


class BootstrapForm(object):  # 用于继承bootstrap装饰
    Bootstrap_class_exclude = ["color", "is_public"]  # 排除一些字段不作bootstrap装饰

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.Bootstrap_class_exclude:
                continue
            old_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = "{} form-control".format(old_class)
            field.widget.attrs["placeholder"] = "请输入" + field.label


class BulmaForm(object):
    Bulma_class_exclude = ["avatar", "gender", "birthday", ""]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.Bulma_class_exclude:
                continue
            old_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = "{} input is-success".format(old_class)
            field.widget.attrs["placeholder"] = "请输入" + field.label
