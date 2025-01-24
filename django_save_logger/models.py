
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from model_utils import Choices

@python_2_unicode_compatible
class SystemEventModel(models.Model):

  TYPES = Choices(
    (100, "request", "API Request"),
    (101, "response", "API Response"),
    (102, "response_exception", "Error"),
    (200, "logged_in", "Sign in"),
    (201, "logged_out", "Sign out"),
    (202, "login_failed", "Failed Login"),
  )

  REQUEST_TYPES = Choices(
    ("GET", "GET"),
    ("POST", "POST"),
    ("PUT", "PUT"),
    ("DELETE", "DELETE"),
    ("PATCH", "PATCH"),
  )

  created_at = models.DateTimeField(default=timezone.now, blank=True)
  type = models.PositiveSmallIntegerField(choices=TYPES)
  user_id = models.IntegerField(blank=True, null=True, db_index=True)
  user_class = models.CharField(max_length=50, db_index=True)
  request_info = models.TextField()
  other_info = models.TextField(null=True, blank=True)
  api_endpoint = models.CharField(max_length=255, null=True, blank=True)
  request_type = models.CharField(max_length=10, choices=REQUEST_TYPES, null=True, blank=True)

  class Meta:
    ordering = ("-created_at",)

  @property
  def type_display(self):
    return self.get_type_display()

  def __str__(self):
    return "SystemEventModel({0.id}, {0.created_at}, {0.user_class}/{0.user_id}, {0.type_display})".format(self)
