from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Friends(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name="friend")
    confirmation = models.BooleanField(default=False)

    class Meta:
        unique_together = (("user", "friend"),)