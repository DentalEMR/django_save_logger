from django_save_logger.archivers import BaseWriter
from boto.s3.connection import S3Connection
import uuid
from django.conf import settings


KEY = settings.BOTO_KEY
SECRET = settings.BOTO_SECRET

class BotoWriter(BaseWriter):
    def __init__(self):
        self.conn = S3Connection(aws_access_key=KEY, aws_secret_access_key=SECRET)
        self.bucket = conn.get_bucket(BUCKET)

    def write(self, key, formatted_obj):
        key = bucket.new_key(uuid.uuid4()).set_contents_from_string(str(formatted_obj))
        pass

    def destroy(self):
        pass

