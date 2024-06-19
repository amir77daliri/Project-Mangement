from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import TaskSerializer, CommentSerializer
from .models import Task, Comment


class TaskListCreateApiView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all()

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


class TaskRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()


class RetrieveTaskCommentsApiView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        print('here...', self.kwargs)
        task_id = self.kwargs.get('pk')
        task = get_object_or_404(Task, pk=task_id)
        return Comment.objects.filter(task=task)

    def post(self, request, *args, **kwargs):
        task_id = self.kwargs.get('pk')
        task = get_object_or_404(Task, pk=task_id)
        ser = self.get_serializer(data=request.data, context={'task': task})
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)
