from django.db import models
from django.utils import timezone

from model_utils import Choices


class SystemEventModel(models.Model):

  TYPES = Choices(
    (100, "request", "API Request"),
    (101, "response", "API Response"),
    (102, "response_exception", "Error"),
    (200, "logged_in", "Sign in"),
    (201, "logged_out", "Sign out"),
    (202, "login_failed", "Failed Login"),
  )

  created_at = models.DateTimeField(default=timezone.now, blank=True)
  type = models.PositiveSmallIntegerField(choices=TYPES)
  user_id = models.IntegerField(blank=True, null=True, db_index=True)
  user_class = models.CharField(max_length=50, db_index=True)
  request_info = models.TextField()
  other_info = models.TextField(null=True, blank=True)

  class Meta:
    ordering = (
      "-created_at",
    )
