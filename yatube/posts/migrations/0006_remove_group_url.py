# Generated by Django 2.2.19 on 2021-08-26 15:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_group_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='url',
        ),
    ]
