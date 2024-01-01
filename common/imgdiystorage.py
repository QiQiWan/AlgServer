from django.core.files.storage import Storage


class FastDFSStorage(Storage):  # TODO自定义文件上传类
    def _open(self, name, mode="rb"):
        # 打开django本地文件
        pass

    def _save(self, name, content, max_length=None):
        # 上传图片
        pass

    # 给返回的图片标识加上前缀
    def url(self, name):
        return "http://image.mysite.site:8888/" + name

    def exists(self, name):
        return False
