from django.http import HttpResponse
from django.template import loader


def some_view(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="somefilename.csv"'},
    )

    # The data is hard-coded here, but you could load it from a database or
    # some other source.
    csv_data = (
        ("First row", "Foo", "Bar", "Baz"),
        ("Second row", "A", "B", "C", '"Testing"', "Here's a quote"),
    )

    t = loader.get_template("my_template_name.txt")
    c = {"data": csv_data}
    response.write(t.render(c))
    return response


import io
from django.http import FileResponse
from reportlab.pdfgen import canvas


def some_view(request):
    # 创建一个类似文件的缓冲区来接收PDF数据。
    buffer = io.BytesIO()

    # 创建PDF对象，将缓冲区用作其“文件”。
    p = canvas.Canvas(buffer)

    # 在PDF上绘制内容。这里是PDF生成的地方。
    # 有关功能的完整列表，请参阅ReportLab文档。
    p.drawString(100, 100, "Hello world.")

    # 干净利落地关闭PDF对象，我们就完成了。
    p.showPage()
    p.save()

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    # FileResponse设置Content-Disposal标头，以便浏览器。
    # 显示保存文件的选项。
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="hello.pdf")
