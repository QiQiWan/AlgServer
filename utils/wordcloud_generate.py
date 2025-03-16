import pandas as pd
import jieba.analyse
from stylecloud import gen_stylecloud
from wordcloud import STOPWORDS

from utils.get_stopwords import get_stopwords

stopwords = get_stopwords()
text = "内容无法生成"

# 切割分词


class Cloud(object):
    def __init__(self, bv_code="cloud", content=text, icon="fas fa-comment-dots"):
        self.bv_code = bv_code
        self.content = content
        self.icon = icon
        self.img_name = bv_code + ".png"
        self.output_name = "media\cloudimg" + "\\" + self.img_name
        self.stopwords = stopwords

    def jieba_get(self):
        """获取中文分词字符串"""
        wordlist = jieba.cut_for_search("".join(self.content))
        result = " ".join(wordlist)

        return result

    def cloud_gennerate(self):  # TODO通过bv_code来拼接这个文件的文件名，每篇文章
        gen_stylecloud(
            text=self.jieba_get(),  # 直接输入文本数据
            icon_name=self.icon,  # 这里可以定义生成云图的形状,可以参考font-awesome的图标库
            palette="cartocolors.qualitative.Pastel_6",
            background_color="white",
            gradient="horizontal",
            output_name=self.output_name,
            font_path="/root/blog/an-algorithm-platform/msyh.ttc",  # 指定中文字体路径
            custom_stopwords=[
                "你",
                "我",
                "他",
                "她",
                "的",
                "了",
                "在",
                "吧",
                "相信",
                "是",
                "也",
                "都",
                "不",
                "吗",
                "就",
                "我们",
                "还",
                "大家",
                "你们",
                "就是",
                "以后",
                "但是",
                "还有",
                "的",
                "是",
                "在",
                "了",
                "有",
                "吗",
                "呢",
                "么",
                "啊",
                "吧",
                "呀",
                "哦",
                "嗯",
                "哪",
                "谁",
                "如",
                "什么",
                "怎么",
                "这样",
                "那样",
                "一些",
                "一下",
                "一定",
                "一样",
                "不会",
                "不是",
                "不要",
                "不能",
                "不过",
                "可以",
                "可能",
                "只是",
                "就是",
                "才能",
                "才会",
                "并且",
                "而且",
                "而是",
                "而已",
                "之间",
                "如果",
                "虽然",
            ]
            + list(STOPWORDS)
            + self.stopwords,
        )

        print("绘图成功！")
        return self.img_name
