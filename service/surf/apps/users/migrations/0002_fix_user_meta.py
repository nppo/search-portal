# Generated by Django 2.2.13 on 2021-01-05 11:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_squashed_0007_clean_authentication'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
    ]
