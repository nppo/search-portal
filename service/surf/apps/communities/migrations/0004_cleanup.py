# Generated by Django 3.2.8 on 2021-10-27 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0003_publisher'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='community',
            name='search_query',
        ),
    ]