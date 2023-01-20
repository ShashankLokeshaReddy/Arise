from django.db import models


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    email = models.CharField(max_length=80, null=True)
    password = models.CharField(max_length=200, null=True)
