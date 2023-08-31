from typing import ClassVar

from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet
from todo.api.models import Project, Task


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    ordering: ClassVar[list[str]] = ["-created_at"]


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    ordering: ClassVar[list[str]] = ["-created_at"]

    # XXX: Notifications
    # XXX: Cache GET
    # XXX: Cache invalidation on POST/PUT/PATCH/DELETE
