# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-05-21 07:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tartrequests', '0010_auto_20170521_0703'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tortapictureregister',
            name='code',
            field=models.CharField(max_length=50, unique=True, verbose_name='Код'),
        ),
        migrations.AlterField(
            model_name='tortarequest',
            name='code',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tartrequests.TortaPictureRegister', to_field='code', verbose_name='Кат.Номер'),
        ),
        migrations.AlterField(
            model_name='tortarequest',
            name='palnej',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tartrequests.TortaTasteRegister', verbose_name='Пълнеж'),
        ),
    ]
