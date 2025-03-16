from typing import Any, Dict
from django import forms
from app01.models import Text
from .BootstrapForm import BootstrapForm
from .widgets import ColorRadioSelect


class TextModelForm(BootstrapForm, forms.ModelForm):
    class Meta:
        model = Text
        fields = ["title", "color", "desc", "is_public", "content"]
        widgets = {
            "color": ColorRadioSelect(attrs={"class": "color-radio"}),
            # "is_public": forms.RadioSelect(choices=((True, "是"), (False, "否"))),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if Text.objects.filter(title=title).exists():
            raise forms.ValidationError("文章标题重复，请更换一个")
        else:
            return title

    def clean_content(self):
        content = self.cleaned_data.get("content")
        if content == None:
            content = "待填写"
        return content
