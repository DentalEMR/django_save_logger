from __future__ import absolute_import

# import uuid
# from boto.s3.connection import S3Connection

from django.conf import settings

from ..archivers import BaseWriter

AWS_ACCESS_KEY_ID = getattr(settings, "AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = getattr(settings, "AWS_SECRET_ACCESS_KEY")


class BotoWriter(BaseWriter):
  def __init__(self):
    # self.conn = S3Connection(aws_access_key=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    # self.bucket = self.conn.get_bucket(BUCKET)
    pass

  def write(self, key, formatted_obj):
    # key = self.bucket.new_key(uuid.uuid4()).set_contents_from_string(str(formatted_obj))
    pass

  def destroy(self):
    pass
