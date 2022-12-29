from django.db import models

class Secret(models.Model):
    secret_name = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.secret_name
