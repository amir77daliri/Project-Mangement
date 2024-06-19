from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/projects/', include('project.urls')),
    path('api/v1/tasks/', include('task.urls')),
]
