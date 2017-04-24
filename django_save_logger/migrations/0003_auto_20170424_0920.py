# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_save_logger', '0002_auto_20170415_0603'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='systemeventmodel',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterField(
            model_name='systemeventmodel',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(100, b'API Request'), (101, b'API Response'), (102, b'Error'), (200, b'Sign in'), (201, b'Sign out'), (202, b'Failed Login')]),
        ),
    ]
