from django.db import models
from django.utils import timezone

from model_utils import Choices


class SystemEventModel(models.Model):

  TYPES = Choices(
    (100, "request", "request"),
    (101, "response", "response"),
    (102, "response_exception", "response_exception"),
    (200, "logged_in", "logged_in"),
    (201, "logged_out", "logged_out"),
    (202, "login_failed", "login_failed"),
  )

  created_at = models.DateTimeField(default=timezone.now, blank=True)
  type = models.PositiveSmallIntegerField(choices=TYPES)
  user_id = models.IntegerField(blank=True, null=True, db_index=True)
  user_class = models.CharField(max_length=50, db_index=True)
  request_info = models.TextField()
  other_info = models.TextField(null=True, blank=True)

  class Meta:
    ordering = (
      "created_at",
    )
