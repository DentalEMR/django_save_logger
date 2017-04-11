# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SystemEventModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, blank=True)),
                ('type', models.PositiveSmallIntegerField(choices=[(100, b'request'), (101, b'response'), (102, b'response_exception'), (200, b'logged_in'), (201, b'logged_out'), (202, b'login_failed')])),
                ('user_pk', models.IntegerField(db_index=True, null=True, blank=True)),
                ('user_class', models.CharField(max_length=50, db_index=True)),
                ('request_info', models.TextField()),
                ('other_info', models.TextField(null=True, blank=True)),
            ],
        ),
    ]
