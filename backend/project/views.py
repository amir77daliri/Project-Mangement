from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import ProjectSerializers
from .models import Project
from django.core.cache import cache

PROJECT_LIST_CACHE_KEY = 'project_list'


class ProjectListCreateApiView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializers

    def get_queryset(self):
        return Project.objects.all()

    def get(self, request, *args, **kwargs):
        project_list = cache.get(PROJECT_LIST_CACHE_KEY)
        # check for cached data
        if project_list is not None:
            return Response(project_list, status=status.HTTP_200_OK)

        # retrieve from db and cache
        queryset = self.get_queryset()
        data = self.serializer_class(queryset, many=True).data
        cache.set(PROJECT_LIST_CACHE_KEY, data)

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data
        ser_data = self.serializer_class(data=data)
        ser_data.is_valid(raise_exception=True)
        ser_data.save()
        # invalidation cache :
        cache.delete(PROJECT_LIST_CACHE_KEY)

        return Response(ser_data.data, status=status.HTTP_201_CREATED)


class ProjectRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializers
    queryset = Project.objects.all()

    def put(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # invalidation cache :
        cache.delete(PROJECT_LIST_CACHE_KEY)
        return response

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        # invalidation cache :
        cache.delete(PROJECT_LIST_CACHE_KEY)
        return response
