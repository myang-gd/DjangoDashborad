# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-11-06 22:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('productkey', models.SmallIntegerField(db_column='ProductKey', primary_key=True, serialize=False)),
                ('productcode', models.TextField(db_column='ProductCode')),
                ('productname', models.TextField(db_column='ProductName')),
                ('productdescription', models.TextField(blank=True, db_column='ProductDescription', null=True)),
                ('retailerkey', models.SmallIntegerField(db_column='RetailerKey')),
                ('programkey', models.SmallIntegerField(blank=True, db_column='ProgramKey', null=True)),
            ],
            options={
                'managed': False,
                'db_table': 'product',
            },
        ),
    ]