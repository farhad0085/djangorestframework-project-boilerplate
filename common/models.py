from django.db import models


class TrackingModel(models.Model):
    """By inheriting this model, we get created and updated time out of the box"""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
