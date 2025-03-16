from typing import Any, Dict, List
from app01.models import Text, User, Comment, Comment_Reply, Text_cloud_Img
from django import forms
from .BootstrapForm import BootstrapForm


class CommentForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text", "user", "content"]


class Comment_ReplyForm(forms.ModelForm):
    class Meta:
        model = Comment_Reply
        fields = [
            "content",
            "comment",
            "user",
            "reply_user",
        ]

    # def clean_reply_user(self):
    #     reply_user = self.cleaned_data.get("reply_user", "")
    #     if not reply_user:
    #         return reply_user
    #     else:
    #         comment = self.cleaned_data.get("comment")
    #         reply_user = comment.user
    #         return reply_user


class Cloud_ImgForm(forms.ModelForm):
    class Meta:
        model = Text_cloud_Img
        fields = ["icon", "img_name", "article"]
