# Generated by Django 2.0.13 on 2019-07-31 11:55

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('locale', '0003_fill_localizations'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocaleHTML',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('asset', models.CharField(max_length=512, unique=True, verbose_name='Asset ID')),
                ('en', models.TextField(blank=True, max_length=16384, null=True, verbose_name='English, en')),
                ('nl', models.TextField(max_length=16384, verbose_name='Dutch, nl')),
                ('is_fuzzy', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Localization with HTML',
                'verbose_name_plural': 'Localizations with HTML',
            },
        ),
        migrations.AlterModelOptions(
            name='locale',
            options={'verbose_name': 'Localization', 'verbose_name_plural': 'Localizations'},
        ),
        migrations.AddField(
            model_name='locale',
            name='is_fuzzy',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='locale',
            name='nl',
            field=models.CharField(max_length=5120, verbose_name='Dutch, nl'),
        ),
    ]
