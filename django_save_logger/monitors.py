import logging
import json


from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed

logger = logging.getLogger( __name__ )

class LoginMonitor(object):

  def __init__(self, extra_user_attr_infos=None):
    self.started = False
    self.extra_user_attr_infos = extra_user_attr_infos

  def get_extra_user_info(self, user):
    info = ''    
    if self.extra_user_attr_infos:
      for extra_user_attr_info in self.extra_user_attr_infos:
        info += ', {}: {}'.format(
          extra_user_attr_info.get('title', ''),
          getattr(user, extra_user_attr_info.get('attr', ''))
        )
    return info
 
  def logged_in(self, sender, request, user, **kwargs):
    logger.info(
      'Logged in: pk: {}, username: {}{}'.format(
        user.pk, 
        user.username, 
        self.get_extra_user_info(user)
      )
    )

  def logged_out(self, sender, request, user, **kwargs):
    if user is None:
      logger.info(
        'Logged out: user was not authenticated'
      )
    else:
      logger.info(
        'Logged out: pk: {}, username: {}{}'.format(
          user.id, 
          user.username, 
          self.get_extra_user_info(user)
        )
      )

  def login_failed(self, sender, credentials, **kwargs):
    logger.info(
      'Login failed: credentials: {}'.format(json.dumps(credentials))
    )
  
  def connect(self):
    if not self.started:
      user_logged_in.connect(self.logged_in)
      user_logged_out.connect(self.logged_out)
      user_login_failed.connect(self.login_failed)
      self.started = True
    return self

  def disconnect(self):
    if self.started:
      user_logged_in.disconnect(self.logged_in)
      user_logged_out.disconnect(self.logged_out)
      user_login_failed.disconnect(self.login_failed)
      self.started = False    
    return self

  def destroy(self):
    self.disconnect()



