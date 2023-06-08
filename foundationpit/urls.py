from django.urls import path

from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    path('StartCalTask', views.start_calc_task, name='StartCalTask'),
    path('GetCalResult', views.get_calc_result, name='GetCalResult'),
    path('HelloWorld', views.hello_world, name='HelloWorld')
]



