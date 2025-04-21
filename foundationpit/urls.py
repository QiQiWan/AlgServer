from django.urls import path

from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    path("GetSingleMesh", views.get_single_mesh, name='Get Single Mesh'),
    path('StartCalTask', views.start_calc_task, name='Start Calculate Task'),
    path('GetCalResult', views.get_calc_result, name='Get Calculate Result'),
    path('GetMeshResult', views.get_mesh_result, name='Get Mesh Result'),
    path('GetTaskList', views.get_all_result, name='Get All Tasks'),
    path('HelloWorld', views.hello_world, name='HelloWorld')
]