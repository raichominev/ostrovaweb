# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-06-10 15:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nomenclature', '0002_auto_20170610_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='club_m2m',
            field=models.ManyToManyField(to='nomenclature.Club', verbose_name='Клуб'),
        ),
    ]
