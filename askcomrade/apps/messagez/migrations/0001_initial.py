# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-19 16:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(3, 'default'), (0, 'local messagez'), (1, 'email'), (4, 'email for every new thread (mailing list mode)')], db_index=True, default=0)),
                ('unread', models.BooleanField(default=True)),
                ('sent_at', models.DateTimeField(db_index=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MessageBody',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Text')),
                ('subject', models.CharField(max_length=120, verbose_name='Subject')),
                ('sent_at', models.DateTimeField(verbose_name='sent at')),
            ],
        ),
    ]
