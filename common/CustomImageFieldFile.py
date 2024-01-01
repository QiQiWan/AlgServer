from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile


class CustomImageFieldFile(ImageFieldFile):
    @property
    def url(self):
        # 在这里添加你的自定义 URL 逻辑
        return "your_custom_url"

    def save(self, name, content, save=True):
        pass


class CustomImageField(ImageField):
    attr_class = CustomImageFieldFile
