# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-05-21 07:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tartrequests', '0011_auto_20170521_0752'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tortapictureregister',
            name='torta_tase_fk',
        ),
    ]
