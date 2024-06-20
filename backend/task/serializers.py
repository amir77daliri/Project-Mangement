from rest_framework import serializers
from .models import Task, Comment


class TaskSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Task
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    task = TaskSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('author', 'content', 'task', 'created_at')

    def create(self, validated_data):
        task = self.context['task']
        content = validated_data['content']
        author = validated_data['author']
        comment = Comment.objects.create(task=task, content=content, author=author)

        return comment
