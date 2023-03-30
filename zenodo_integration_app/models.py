from django.db import models
from django.contrib.auth.models import User
import uuid

class ZenodoExperiment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    experiment_id = models.CharField(max_length=100)
    refresh_token = models.CharField(max_length=200, blank=True, null=True)
    depo_id = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'experiment_id')