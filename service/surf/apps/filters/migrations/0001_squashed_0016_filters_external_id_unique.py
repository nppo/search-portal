# Generated by Django 2.2.13 on 2020-12-14 12:30

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import uuid


# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
# surf.apps.filters.migrations.0008_auto_20190829_1437
# surf.apps.filters.migrations.0010_auto_20190830_1329
# surf.apps.filters.migrations.0014_auto_20200702_1005

class Migration(migrations.Migration):

    replaces = [('filters', '0001_initial'), ('filters', '0002_filter_owner'), ('filters', '0003_auto_20181116_1253'), ('filters', '0004_filter_materials_count'), ('filters', '0005_filtercategoryitem_order'), ('filters', '0006_filtercategory_title_translations'), ('filters', '0007_mpttfilteritem'), ('filters', '0008_auto_20190829_1437'), ('filters', '0009_filteritem_mptt_category_item'), ('filters', '0010_auto_20190830_1329'), ('filters', '0011_auto_20190905_1521'), ('filters', '0012_auto_20191112_0918'), ('filters', '0013_auto_20191112_1040'), ('filters', '0014_auto_20200702_1005'), ('filters', '0015_remove_user_filters'), ('filters', '0016_filters_external_id_unique')]

    initial = True

    dependencies = [
        ('locale', '0004_improved_translations'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MpttFilterItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_from_edurep_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('external_id', models.CharField(blank=True, max_length=255, verbose_name='Field id in EduRep')),
                ('enabled_by_default', models.BooleanField(default=False)),
                ('is_hidden', models.BooleanField(default=False)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='filters.MpttFilterItem')),
                ('title_translations', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='locale.Locale')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='mpttfilteritem',
            options={'verbose_name': 'filter category item'},
        ),
        migrations.AlterField(
            model_name='mpttfilteritem',
            name='level',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='mpttfilteritem',
            name='lft',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='mpttfilteritem',
            name='rght',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='mpttfilteritem',
            name='external_id',
            field=models.CharField(max_length=255, unique=True, verbose_name='Field id in EduRep'),
        ),
    ]
