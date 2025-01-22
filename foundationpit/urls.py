from django.urls import path

from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    path('StartCalTask', views.start_calc_task, name='Start Calculate Task'),
    path('GetCalResult', views.get_calc_result, name='Get Calculate Result'),
    path('GetMeshResult', views.get_mesh_result, name='Get Mesh Result'),
    path('HelloWorld', views.hello_world, name='HelloWorld')
]