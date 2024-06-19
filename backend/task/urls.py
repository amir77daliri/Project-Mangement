from django.urls import path
from .views import (
    TaskListCreateApiView,
    TaskRetrieveUpdateDestroyApiView,
    RetrieveTaskCommentsApiView
)

urlpatterns = [
    path('', TaskListCreateApiView.as_view(), name='task_list_create'),
    path('<int:pk>', TaskRetrieveUpdateDestroyApiView.as_view(), name='task_get_update_delete'),
    # for comments :
    path('<int:pk>/comments/', RetrieveTaskCommentsApiView.as_view(), name='task_comments')
]
