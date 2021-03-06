# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-06-12 13:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tartrequests', '0020_auto_20170611_0749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tortarequest',
            name='dostavka_date',
            field=models.DateField(db_index=True, null=True, verbose_name='Дата доставка'),
        ),
        migrations.AlterField(
            model_name='tortarequestpicture',
            name='filename',
            field=models.FileField(blank=True, null=True, upload_to='tartImages/СОБСТВЕНО ИЗОБРАЖЕНИЕ', verbose_name='Изображение'),
        ),
    ]
