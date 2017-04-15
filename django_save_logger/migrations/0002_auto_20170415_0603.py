# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_save_logger', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='systemeventmodel',
            options={'ordering': ('created_at',)},
        ),
        migrations.RenameField(
            model_name='systemeventmodel',
            old_name='user_pk',
            new_name='user_id',
        ),
    ]
