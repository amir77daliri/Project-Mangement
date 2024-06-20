from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import TaskSerializer, CommentSerializer
from .models import Task, Comment
from django.core.cache import cache
from django.shortcuts import render


Task_LIST_CACHE_KEY = 'task_list'


def index_ws(request):
    return render(request, 'task/index.html')


def room(request, room_name):
    print(room_name)
    return render(request, "task/room.html", {"room_name": room_name})


class TaskListCreateApiView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all()

    def get(self, request, *args, **kwargs):
        task_list = cache.get(Task_LIST_CACHE_KEY)
        # check for cached data :
        if task_list is not None:
            print('get from cache...')
            return Response(task_list, status=status.HTTP_200_OK)
        # get from db and cache data
        queryset = self.get_queryset()
        data = self.serializer_class(queryset, many=True).data
        cache.set(Task_LIST_CACHE_KEY, data)
        print('get from db....')
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data
        ser_data = self.serializer_class(data=data)
        ser_data.is_valid(raise_exception=True)
        ser_data.save()
        # invalidate cache
        cache.delete(Task_LIST_CACHE_KEY)
        return Response(ser_data.data, status=status.HTTP_201_CREATED)


class TaskRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def put(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # invalidation cache :
        cache.delete(Task_LIST_CACHE_KEY)
        return response

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        # invalidation cache :
        cache.delete(Task_LIST_CACHE_KEY)
        return response


class RetrieveTaskCommentsApiView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
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
