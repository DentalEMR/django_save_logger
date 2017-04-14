import json
import logging
from traceback import format_exc

from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.signals import user_logged_out
from django.contrib.auth.signals import user_login_failed

from .models import SystemEventModel

logger = logging.getLogger(__name__)


def format_log_message(type, user, request_info, other_info):
  return "{}: pk: {}, username: {}, request info: {}{}".format(
    type,
    getattr(user, "pk", "<no user>"),
    getattr(user, "username", "<no user>"),
    request_info,
    other_info
  )


def request_info(request):
  return json.dumps({
    "method": request.method,
    "path": request.path,
    "REMOTE_ADDR": request.META.get("REMOTE_ADDR", ""),
    "HTTP_USER_AGENT": request.META.get("HTTP_USER_AGENT", ""),
    "HTTP_CLIENT_IP": request.META.get("HTTP_CLIENT_IP", ""),
    "HTTP_X_FORWARDED": request.META.get("HTTP_X_FORWARDED", ""),
    "HTTP_FORWARDED_FOR": request.META.get("HTTP_FORWARDED_FOR", ""),
    "HTTP_FORWARDED": request.META.get("HTTP_FORWARDED", ""),
  })


def response_info(response):
  return json.dumps({
    "response__status_code": response.status_code
  })


def exception_info(exception):
  return json.dumps({
    "exception": format_exc(exception)
  })


class LoginEventMonitor(object):

  def __init__(self, extra_user_attr_infos=None):
    self.started = False
    self.extra_user_attr_infos = extra_user_attr_infos

  def get_extra_user_info(self, user):
    info = ""
    if self.extra_user_attr_infos:
      for extra_user_attr_info in self.extra_user_attr_infos:
        info += ", {}: {}".format(
          extra_user_attr_info.get("title", ""),
          getattr(user, extra_user_attr_info.get("attr", ""))
        )
    return info

  def logged_in(self, sender, request, user, **kwargs):
    logger.info(format_log_message("logged_in", user, request_info(request), self.get_extra_user_info(user)))

  def logged_out(self, sender, request, user, **kwargs):
    logger.info(format_log_message("logged_out", user, request_info(request), self.get_extra_user_info(user)))

  def login_failed(self, sender, credentials, **kwargs):
    logger.info(format_log_message("login_failed", None, None, json.dumps(credentials)))

  def connect(self):
    if not self.started:
      user_logged_in.connect(self.logged_in, weak=False, dispatch_uid="dsl-logged-in")
      user_logged_out.connect(self.logged_out, weak=False, dispatch_uid="dsl-logged-out")
      user_login_failed.connect(self.login_failed, weak=False, dispatch_uid="dsl-logged-failed")
      self.started = True
    return self

  def disconnect(self):
    if self.started:
      user_logged_in.disconnect(self.logged_in, weak=False, dispatch_uid="dsl-logged-in")
      user_logged_out.disconnect(self.logged_out, weak=False, dispatch_uid="dsl-logged-out")
      user_login_failed.disconnect(self.login_failed, weak=False, dispatch_uid="dsl-logged-failed")
      self.started = False
    return self

  def destroy(self):
    self.disconnect()


class LoginEventPersistMonitor(LoginEventMonitor):

  def logged_in(self, sender, request, user, **kwargs):
    SystemEventModel.objects.create(
      type=SystemEventModel.TYPES.logged_in,
      user_pk=user.id,
      user_class="{0._meta.app_label}.{0.__class__.__name__}".format(user),
      request_info=request_info(request),
    )
    super(LoginEventPersistMonitor, self).logged_in(sender, request, user, **kwargs)

  def logged_out(self, sender, request, user, **kwargs):
    if user.is_authenticated():
      event_kwargs = dict(
        type=SystemEventModel.TYPES.logged_out,
        user_pk=user.id,
        user_class="{0._meta.app_label}.{0.__class__.__name__}".format(user),
        request_info=request_info(request),
        other_info=kwargs.get("other_info", {})
      )
      if "created_at" in kwargs:
        event_kwargs.update(created_at=kwargs.get("created_at"))
      SystemEventModel.objects.create(**event_kwargs)
      super(LoginEventPersistMonitor, self).logged_out(sender, request, user, **kwargs)

  def login_failed(self, sender, credentials, **kwargs):
    SystemEventModel.objects.create(
      type=SystemEventModel.TYPES.login_failed,
      other_info=json.dumps(credentials)
    )
    super(LoginEventPersistMonitor, self).login_failed(sender, credentials, **kwargs)
