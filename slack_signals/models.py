from django.db import models


class Todo(models.Model):
    text = models.CharField(max_length=150)

    def __str__(self):
        return str(self.text)
