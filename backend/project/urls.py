from django.urls import path
from .views import ProjectListCreateApiView, ProjectRetrieveUpdateDestroyApiView


urlpatterns = [
    path('', ProjectListCreateApiView.as_view(), name='list_create_project'),
    path('<int:pk>', ProjectRetrieveUpdateDestroyApiView.as_view(), name='get_update_delete_project')
]
