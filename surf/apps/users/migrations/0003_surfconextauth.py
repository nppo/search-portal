# Generated by Django 2.0.6 on 2018-11-12 11:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20181026_0857'),
    ]

    operations = [
        migrations.CreateModel(
            name='SurfConextAuth',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('display_name', models.CharField(max_length=100)),
                ('external_id', models.CharField(max_length=255)),
                ('access_token', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surfconext_auth', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'SurfConext Auth',
                'verbose_name_plural': 'SurfConext Auths',
                'ordering': ('display_name',),
            },
        ),
    ]
