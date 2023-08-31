from django.db import models


class Project(models.Model):
    """Project model"""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.TextField()


class Task(models.Model):
    """Task model"""

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.TextField()
    description = models.TextField()
    completed = models.BooleanField(default=False)
