from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import ProjectSerializers
from .models import Project


class ProjectListCreateApiView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializers

    def get_queryset(self):
        return Project.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = self.serializer_class(queryset, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data
        ser_data = self.serializer_class(data=data)
        ser_data.is_valid(raise_exception=True)
        ser_data.save()
        return Response(ser_data.data, status=status.HTTP_201_CREATED)


class ProjectRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializers
    queryset = Project.objects.all()

