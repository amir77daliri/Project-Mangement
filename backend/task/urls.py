from django.urls import path
from .views import (
    TaskListCreateApiView,
    TaskRetrieveUpdateDestroyApiView,
    RetrieveTaskCommentsApiView,
    index_ws,
    room
)

urlpatterns = [
    path('', TaskListCreateApiView.as_view(), name='task_list_create'),
    path('index', index_ws, name='index_websocket'),
    path('room/<str:room_name>', room, name='room_websocket'),
    path('<int:pk>', TaskRetrieveUpdateDestroyApiView.as_view(), name='task_get_update_delete'),
    # for comments :
    path('<int:pk>/comments/', RetrieveTaskCommentsApiView.as_view(), name='task_comments')
]
