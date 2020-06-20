import json

from django.db import models

class City(models.Model):
    name = models.CharField(max_length=30)

    def _str_(self):
        return self.name
