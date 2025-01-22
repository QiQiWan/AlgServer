from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from algserver import settings
import time
import os


def key_create(filename):  # 随机生成一个文件名
    basename, extension = os.path.splitext(filename)  # 拆分文件名和后缀
    timestamp = str(round(time.time() * 1000))
    filename = timestamp + extension
    return filename


secret_id = settings.SECRET_ID
secret_key = settings.SECRET_KEY
region = "ap-chengdu"  # 替换为用户的 Region
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
client = CosS3Client(config)


def upload_obj_avatar(user, file_obj):  # 上传用户头像
    key = key_create(file_obj)
    filetype = file_obj.name.rsplit(".")[-1]  # 获取文件后缀
    response = client.upload_file_from_buffer(
        Bucket="algserver-md-img-1252510405",
        Body=file_obj,  # 需要上传的文件对象
        Key="user_avatar/{}_avatar.{}".format(user.username, filetype),  # 上传到桶之后的文件名
    )


road = "user_avatar/"  # 文件夹的路径


def get_avatar(user):
    file_key = "user_avatar/"
    response = client.list_objects(
        Bucket="algserver-md-img-1252510405", Prefix="user_avatar"
    )
    for content in response["Contents"]:
        user_avatar = content["Key"].split("/")[-1].split(".")[0]  # 去除文件后缀，获取纯文件名
        avatar_name = "{}_avatar".format(user.username)
        if user_avatar == avatar_name:
            avatar_url = (
                "https://algserver-md-img-1252510405.cos.ap-chengdu.myqcloud.com/"
                + content["Key"]
            )
            return avatar_url


def upload_obj(img_obj, bv):  # 上传文件对象,并生成一个图片链接
    key = "article-md-img/" + key_create(img_obj.name)
    response = client.upload_file_from_buffer(
        Bucket="algserver-md-img-1252510405",
        Body=img_obj,  # 需要上传的文件对象
        Key=key,  # 上传到桶之后的文件名
    )
    url = "https://algserver-md-img-1252510405.cos.ap-chengdu.myqcloud.com/" + key
    # 图片url格式:https://algserver-md-img-1252510405.cos.ap-chengdu.myqcloud.com/article-md-img/1.png
    print(url)
    return url


class cencloud:
    def __init__(self, secret_id, secret_key, region):
        self.config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
        self.client = CosS3Client(self.config)

    # --------------------上传文件的方法--------------

    def upload(self):
        response = self.client.upload_file(
            Bucket="algserver-md-img-1252510405",
            LocalFilePath=r"day16\app01\static\js\echarts.js",  # 本地文件的路径
            # "r"前缀用于定义一个原始字符串，其中的反斜杠不需要进行额外的转义
            Key="{}".format("username"),  # 上传到桶之后的文件名
        )
        print(response["ETag"])

    def upload_obj(self, img_obj):  # 上传文件对象
        response = self.client.upload_file_from_buffer(
            Bucket="algserver-md-img-1252510405",
            Body=img_obj,  # 需要上传的文件对象
            Key="p1.png",  # 上传到桶之后的文件名
        )

    # --------------创建存储桶的方法--------------

    def create_buc(self):
        response = self.client.create_bucket(
            Bucket="test-1251317460",  # 创建桶名称
            ACL="public-read",  # private  /  public-read / public-read-write
        )


if __name__ == "__main__":
    get_avatar(1)
