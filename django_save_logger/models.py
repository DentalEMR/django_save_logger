from django.db import models

from model_utils import Choices


class SystemEventModel(models.Model):

  TYPES = Choices(
    (100, "request"),
    (101, "response"),
    (102, "response_exception"),
    (200, "logged_in"),
    (201, "logged_out"),
    (202, "login_failed"),
  )

  type = models.PositiveSmallIntegerField(choices=TYPES)
  user_pk = models.IntegerField(blank=True, null=True)
  request_info = models.TextField()
  other_info = models.TextField(null=True, blank=True)
