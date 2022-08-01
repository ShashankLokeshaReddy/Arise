from django.db import models

# Create your models here.
class Machine(models.Model):
    resourceId = models.CharField(max_length=140)
    title = models.CharField(max_length=140)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']