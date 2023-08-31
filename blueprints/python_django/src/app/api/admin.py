from django.contrib import admin
from todo.api.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass
