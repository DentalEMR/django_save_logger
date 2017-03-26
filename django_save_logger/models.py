from django.db import models
from django.contrib.auth.models import AbstractBaseUser

class SystemEventModel(models.Model):

  TYPES = (
    ('logged_in', 'logged_in'),
    ('logged_out', 'logged_out'),
    ('login_failed', 'login_failed'),
    ('request', 'request'),
    ('response', 'response'),
    ('response_exception', 'response_exception'),
  )

  type            = models.CharField(max_length=100, choices=TYPES)
  user_pk         = models.IntegerField(blank=True, null=True)
  request_info    = models.TextField()
  other_info      = models.TextField(null=True, blank=True) 

