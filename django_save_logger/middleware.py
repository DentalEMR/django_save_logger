import logging

from .monitors import format_log_message
from .monitors import request_info
from .monitors import response_info
from .monitors import exception_info

from .models import SystemEventModel

logger = logging.getLogger(__name__)


class ApiCallEventMiddleware(object):

  def process_request(self, request):
    logger.info(
      format_log_message("request", request.user, request_info(request), "")
    )

  def process_response(self, request, response):
    logger.info(
      format_log_message(
        "response",
        getattr(request, 'user', None),
        request_info(request),
        response_info(response)
      )
    )
    return response

  def process_exception(self, request, exception):
    logger.info(
      format_log_message(
        "response_exception",
        request.user,
        request_info(request),
        exception_info(exception)
      )
    )
    return None


class ApiCallEventPersistMiddleware(ApiCallEventMiddleware):
  # # rely on process_response for practice"s to track api calls
  # def process_request(self, request):
  #   ret = super(ApiCallEventPersistMiddleware, self).process_request(request)
  #   SystemEventModel.objects.create(
  #     type=SystemEventModel.TYPES.request,
  #     user_id=request.user.id,
  #     user_class="{0._meta.app_label}.{0.__class__.__name__}".format(request.user),
  #     request_info=request_info(request),
  #   )
  #   return ret

  def process_response(self, request, response):
    ret = super(ApiCallEventPersistMiddleware, self).process_response(request, response)
    if hasattr(request, 'user') and request.user.is_authenticated():
      user_class = "{0._meta.app_label}.{0.__class__.__name__}".format(request.user)
      user_id = request.user.id
    else:
      user_class = "AnonymousUser"
      user_id = None

    SystemEventModel.objects.create(
      type=SystemEventModel.TYPES.response,
      user_id=user_id,
      user_class=user_class,
      api_endpoint=request.path,
      request_info=request_info(request),
      other_info=response_info(response)
    )
    return ret

  # def process_exception(self, request, exception):
  #   ret = super(ApiCallEventPersistMiddleware, self).process_exception(request, exception)
  #   SystemEventModel.objects.create(
  #     type=SystemEventModel.TYPES.response_exception,
  #     user_id=request.user.id,
  #     user_class="{0._meta.app_label}.{0.__class__.__name__}".format(request.user),
  #     request_info=request_info(request),
  #     other_info=exception_info(exception)
  #   )
  #   return ret
