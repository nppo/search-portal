# Generated by Django 2.0.6 on 2018-10-26 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0002_collection_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='materials',
            field=models.ManyToManyField(blank=True, related_name='collections', to='materials.Material'),
        ),
    ]
